import urllib.request, json, ssl, time, os, sys, uuid, shutil, subprocess
from datetime import datetime, timezone
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from card_generator import make_table_pdf
from recommendation_engine import run_recommendation_engine
from newsletter_builder import render_newsletter_html

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

CLASSIC_LEAGUE_ID = 19441
H2H_LEAGUE_ID = 1069869

# Credentials & Configuration (Loaded strictly from GitHub Secrets)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_IDS = [cid.strip() for cid in os.environ.get("TELEGRAM_CHAT_ID", "").split(",") if cid.strip()]

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "")

STATE_FILE = "state.json"
CACHE_DIR = "/tmp/fpl_cache"
DOCS_DIR = "docs"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.join(DOCS_DIR, "archive"), exist_ok=True)

CHIP_NAMES = {
    "wildcard": "Wildcard",
    "freehit": "Free Hit",
    "3xc": "Triple Captain",
    "bboost": "Bench Boost"
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"newsletter_gw": 9, "locked_gw": 9, "concluded_gw": 9}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def fetch_json(url, retries=4, delay=2):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(delay * (i + 1))

# ==========================================
# DISPATCHERS (TELEGRAM & EMAIL)
# ==========================================
def send_telegram_photo(image_path, caption=""):
    if not BOT_TOKEN or not CHAT_IDS:
        print(f"[TELEGRAM PHOTO DRY RUN] {image_path}: {caption}")
        return True
    filename = os.path.basename(image_path)
    with open(image_path, "rb") as f:
        file_bytes = f.read()
        
    success = True
    for cid in CHAT_IDS:
        boundary = uuid.uuid4().hex
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}", "User-Agent": "Mozilla/5.0"}
        body = [
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n{cid}\r\n".encode('utf-8'),
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n{caption}\r\n".encode('utf-8') if caption else b"",
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"parse_mode\"\r\n\r\nHTML\r\n".encode('utf-8'),
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"{filename}\"\r\nContent-Type: image/png\r\n\r\n".encode('utf-8'),
            file_bytes,
            f"\r\n--{boundary}--\r\n".encode('utf-8')
        ]
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        req = urllib.request.Request(url, data=b"".join(body), headers=headers)
        try:
            with urllib.request.urlopen(req, context=CTX, timeout=25) as r:
                res = json.loads(r.read().decode())
                print(f"Delivered photo to Telegram {cid}: {res.get('ok')}")
        except Exception as e:
            print(f"Telegram photo error for {cid}: {e}")
            success = False
    return success

def send_html_email(subject, html_content):
    print(f"--> Initiating Outbound Email Dispatch...")
    print(f"  SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"  SMTP Username: '{SMTP_USERNAME}'")
    print(f"  SMTP Password configured: {'YES' if SMTP_PASSWORD else 'NO (EMPTY SECRET!)'}")
    print(f"  Email Recipient(s): '{EMAIL_RECIPIENT}'")
    
    if not SMTP_PASSWORD or not SMTP_USERNAME:
        err_msg = "❌ CRITICAL: SMTP_USERNAME or SMTP_PASSWORD is missing in GitHub Repository Secrets!"
        print(err_msg)
        raise ValueError(err_msg)
        
    recipients = [r.strip() for r in EMAIL_RECIPIENT.split(",") if r.strip()]
    if not recipients:
        err_msg = "❌ CRITICAL: EMAIL_RECIPIENT secret is empty!"
        print(err_msg)
        raise ValueError(err_msg)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Toxic 90 Scout <{SMTP_USERNAME}>"
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText("Please enable HTML to view the Toxic 90 Scout Briefing.", "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, recipients, msg.as_string())
            print(f"✅ Email successfully delivered to {recipients}")
            return True
    except Exception as e:
        print(f"❌ SMTP Dispatch Failed: {e}")
        raise e

def send_email_with_card_attachments(subject, caption, image_paths):
    if not SMTP_PASSWORD or not SMTP_USERNAME:
        print(f"[EMAIL CARDS DRY RUN] Subject: {subject} | Images: {image_paths}")
        return True
    recipients = [r.strip() for r in EMAIL_RECIPIENT.split(",") if r.strip()]
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = f"Toxic 90 FPL <{SMTP_USERNAME}>"
    msg["To"] = ", ".join(recipients)
    
    html_parts = [f"<div style='font-family: Arial, sans-serif; padding: 15px;'>"]
    html_parts.append(f"<h2 style='color: #0f172a; margin-bottom: 8px;'>{subject}</h2>")
    html_parts.append(f"<p style='color: #475569; font-size: 14px;'>{caption}</p>")
    
    for idx, img in enumerate(image_paths):
        cid = f"card_{idx}"
        html_parts.append(f"<div style='margin-top: 15px;'><img src='cid:{cid}' style='max-width: 100%; border-radius: 8px; border: 1px solid #e2e8f0;' /></div>")
    html_parts.append("</div>")
    
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(caption, "plain"))
    msg_alt.attach(MIMEText("".join(html_parts), "html"))
    
    for idx, img in enumerate(image_paths):
        with open(img, "rb") as f:
            img_data = MIMEImage(f.read())
            img_data.add_header("Content-ID", f"<card_{idx}>")
            img_data.add_header("Content-Disposition", "inline", filename=os.path.basename(img))
            msg.attach(img_data)
            
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, recipients, msg.as_string())
            print(f"Cards email delivered to {recipients}")
            return True
    except Exception as e:
        print(f"Cards email error: {e}")
        return False

# ==========================================
# TRIGGER 0: PRE-DEADLINE SCOUT NEWSLETTER (T - 3 HOURS)
# STRICT CHANNEL SEPARATION: EMAIL ONLY + GITHUB PAGES ARCHIVE
# ==========================================
def trigger_newsletter(gw):
    print(f"\n--> Executing Trigger 0: GW{gw} 3-HOUR PRE-DEADLINE SCOUT NEWSLETTER...")
    data = run_recommendation_engine()
    html_content = render_newsletter_html(data)
    
    # 1. Update Layer 2: GitHub Pages Web Archive
    index_path = os.path.join(DOCS_DIR, "index.html")
    archive_path = os.path.join(DOCS_DIR, "archive", f"gw{gw}.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Updated GitHub Pages archive: {index_path} and {archive_path}")
    
    # 2. Dispatch Layer 1: Email Newsletter (Email ONLY - NOT Telegram)
    subject = f"Toxic 90 Scout: Game Week {gw} Final Briefing (3 Hours to Lock)"
    send_html_email(subject, html_content)

# ==========================================
# TRIGGER 1: POST-DEADLINE ARTIFACTS 1 & 2 (T + 20 MINS)
# STRICT CHANNEL RULE: POST HIGH-RES IMAGES TO TELEGRAM
# ==========================================
def trigger_deadline(gw, bs):
    print(f"\n--> Executing Trigger 1: GW{gw} LOCKED (20 mins post-deadline)...")
    elements_map = {el["id"]: el["web_name"] for el in bs["elements"]}
    
    # 1. Artifact 1: Top 5 & Captains
    c_url = f"https://fantasy.premierleague.com/api/leagues-classic/{CLASSIC_LEAGUE_ID}/standings/"
    c_data = fetch_json(c_url)
    top5 = c_data["standings"]["results"][:5]
    
    art1_rows = []
    for rank, entry in enumerate(top5, 1):
        entry_id = entry["entry"]
        mgr_name = entry["player_name"]
        entry_name = entry["entry_name"]
        
        picks_url = f"https://fantasy.premierleague.com/api/entry/{entry_id}/event/{gw}/picks/"
        cap_name, vc_name, chip_str = "-", "-", "-"
        try:
            p_data = fetch_json(picks_url)
            chip_raw = p_data.get("active_chip")
            chip_str = CHIP_NAMES.get(chip_raw, chip_raw.title() if chip_raw else "-")
            for p in p_data.get("picks", []):
                if p.get("is_captain"):
                    cap_name = elements_map.get(p["element"], "Unknown")
                elif p.get("is_vice_captain"):
                    vc_name = elements_map.get(p["element"], "Unknown")
        except Exception as e:
            print(f"Could not fetch picks for {mgr_name}: {e}")
            
        art1_rows.append([str(rank), mgr_name, entry_name, cap_name, vc_name, chip_str])
        
    headers_1 = ["Rank", "Manager", "Team Name", "Captain (C)", "Vice-Captain (VC)", "Active Chip"]
    widths_1 = [45, 135, 145, 95, 95, 80]
    aligns_1 = ['C', 'L', 'L', 'L', 'L', 'C']
    pdf_1 = f"artifact_1_top5_captains_gw{gw}.pdf"
    png_1 = make_table_pdf(pdf_1, f"Game Week {gw} Locked: Top 5 Managers & Captains", headers_1, art1_rows, widths_1, aligns_1)

    # 2. Artifact 2: Head-to-Head Matchups
    h2h_matches_url = f"https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{H2H_LEAGUE_ID}/?page=1&event={gw}"
    m_data = fetch_json(h2h_matches_url)
    matches = m_data.get("results", [])
    
    art2_rows = []
    for m_idx, m in enumerate(matches, 1):
        p1 = m.get("entry_1_player_name", "TBD")
        t1 = m.get("entry_1_name", "")
        p2 = m.get("entry_2_player_name", "TBD")
        t2 = m.get("entry_2_name", "")
        art2_rows.append([f"Match {m_idx}", p1, t1, "vs", t2, p2])
        
    headers_2 = ["Match", "Manager 1", "Team 1", "VS", "Team 2", "Manager 2"]
    widths_2 = [60, 125, 125, 30, 125, 125]
    aligns_2 = ['C', 'L', 'L', 'C', 'R', 'R']
    pdf_2 = f"artifact_2_h2h_matchups_gw{gw}.pdf"
    png_2 = make_table_pdf(pdf_2, f"Game Week {gw} Head-to-Head Matchups", headers_2, art2_rows, widths_2, aligns_2)

    # Dispatch to Telegram (High-res Cards ONLY)
    send_telegram_photo(png_1, f"🏆 <b>Toxic 90 ☢️ | GW {gw} Locked</b>\nTop 5 Managers, Captains & Active Chips.")
    send_telegram_photo(png_2, f"⚔️ <b>Toxic 90 ☢️ | GW {gw} Head-to-Head Matchups</b>\nFull fixture lineup for the gameweek.")
    
    # Dispatch Email with Attached Cards (Safe execution - won't block Telegram)
    try:
        send_email_with_card_attachments(
            f"[Toxic 90] Game Week {gw} Locked: Top 5 Captains & H2H Matchups",
            f"Game Week {gw} has locked! Here are the Top 5 Managers, Captain selections, and H2H Matchups:",
            [png_1, png_2]
        )
    except Exception as e:
        print(f"Email dispatch note (Telegram was delivered): {e}")

# ==========================================
# TRIGGER 2: POST-GAMEWEEK FINAL SETTLEMENT (ARTIFACTS 3 & 4)
# CONDITION: finished == True AND data_checked == True
# ==========================================
def trigger_over(gw, bs):
    print(f"\n--> Executing Trigger 2: GW{gw} CONCLUDED (Official settlement complete)...")
    
    # 1. Classic Standings
    c_url = f"https://fantasy.premierleague.com/api/leagues-classic/{CLASSIC_LEAGUE_ID}/standings/"
    c_data = fetch_json(c_url)
    standings = c_data["standings"]["results"]
    
    art3_rows = []
    row_colors = []
    for entry in standings:
        rank = entry["rank"]
        last_rank = entry.get("last_rank", rank)
        if last_rank > rank:
            mv = f"▲ {last_rank - rank}"
        elif last_rank < rank:
            mv = f"▼ {rank - last_rank}"
        else:
            mv = "="
            
        mgr = entry["player_name"]
        team = entry["entry_name"]
        gw_pts = str(entry["event_total"])
        tot_pts = str(entry["total"])
        
        art3_rows.append([str(rank), mv, mgr, team, gw_pts, tot_pts])
        if rank == 1:
            row_colors.append((0.99, 0.96, 0.88)) # Gold theme
        else:
            row_colors.append(None)
            
    headers_3 = ["Rank", "Move", "Manager", "Team Name", "GW Pts", "Total Pts"]
    widths_3 = [45, 45, 140, 150, 65, 75]
    aligns_3 = ['C', 'C', 'L', 'L', 'C', 'C']
    pdf_3 = f"artifact_3_classic_standings_gw{gw}.pdf"
    png_3 = make_table_pdf(pdf_3, f"Game Week {gw} Standings: Toxic 90 League", headers_3, art3_rows, widths_3, aligns_3, row_colors)

    # 2. H2H Standings & Results
    h2h_url = f"https://fantasy.premierleague.com/api/leagues-h2h/{H2H_LEAGUE_ID}/standings/"
    h2h_data = fetch_json(h2h_url)
    h_standings = h2h_data["standings"]["results"]
    
    h2h_matches_url = f"https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{H2H_LEAGUE_ID}/?page=1&event={gw}"
    m_data = fetch_json(h2h_matches_url)
    matches = m_data.get("results", [])
    
    scores = {}
    for m in matches:
        e1, e2 = m.get("entry_1_entry"), m.get("entry_2_entry")
        p1, p2 = m.get("entry_1_points", 0), m.get("entry_2_points", 0)
        n1, n2 = m.get("entry_1_player_name", ""), m.get("entry_2_player_name", "")
        if e1:
            scores[e1] = f"{p1} - {p2} (vs {n2})"
        if e2:
            scores[e2] = f"{p2} - {p1} (vs {n1})"
            
    art4_rows = []
    for entry in h_standings:
        rank = str(entry["rank"])
        mgr = entry["player_name"]
        team = entry["entry_name"]
        pld = str(entry["matches_played"])
        w = str(entry["matches_won"])
        d = str(entry["matches_drawn"])
        l = str(entry["matches_lost"])
        pts = str(entry["total"])
        gw_res = scores.get(entry["entry"], "-")
        art4_rows.append([rank, mgr, team, pld, w, d, l, pts, gw_res])
        
    headers_4 = ["Rank", "Manager", "Team Name", "P", "W", "D", "L", "Pts", f"GW {gw} Score"]
    widths_4 = [40, 115, 120, 25, 25, 25, 25, 35, 130]
    aligns_4 = ['C', 'L', 'L', 'C', 'C', 'C', 'C', 'C', 'L']
    pdf_4 = f"artifact_4_h2h_standings_gw{gw}.pdf"
    png_4 = make_table_pdf(pdf_4, f"Game Week {gw} Head-to-Head Standings & Results", headers_4, art4_rows, widths_4, aligns_4)

    # Dispatch to Telegram (Cards ONLY)
    send_telegram_photo(png_3, f"🏆 <b>Toxic 90 ☢️ | GW {gw} Final Standings</b>\nOfficial data settled, auto-subs & bonus points applied.")
    send_telegram_photo(png_4, f"⚔️ <b>Toxic 90 ☢️ | GW {gw} Head-to-Head Results</b>\nFinal match scorelines and updated table.")
    
    # Dispatch Email with Attached Cards (Safe execution - won't block Telegram)
    try:
        send_email_with_card_attachments(
            f"[Toxic 90] Game Week {gw} Final Standings & H2H Results",
            f"Game Week {gw} is officially settled! Find the updated Classic and H2H tables below:",
            [png_3, png_4]
        )
    except Exception as e:
        print(f"Email dispatch note (Telegram was delivered): {e}")

# ==========================================
# MASTER AUTONOMOUS ORCHESTRATOR
# ==========================================
def poll_cycle():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Toxic 90 Autonomous Check...")
    state = load_state()
    bs = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
    now = datetime.now(timezone.utc)
    now_epoch = int(time.time())
    events = bs['events']
    
    current_ev = next((e for e in events if e.get("is_current")), None)
    next_ev = next((e for e in events if e.get("is_next")), None)
    
    print(f"Status: Current GW = {current_ev['id'] if current_ev else 'None'} | Next GW = {next_ev['id'] if next_ev else 'None'}")
    
    # Check 0: 3 Hours Before Deadline (Newsletter via Email)
    target_dl_ev = next_ev or current_ev
    if target_dl_ev and not target_dl_ev.get("finished"):
        gw_id = target_dl_ev["id"]
        dl_str = target_dl_ev["deadline_time"]
        dl_dt = datetime.strptime(dl_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        diff_hours = (dl_dt - now).total_seconds() / 3600.0
        
        print(f"GW {gw_id} deadline in {diff_hours:.2f} hours.")
        # Fires when within ~3 hours before deadline (2.5 to 3.5 hour window)
        if 0.0 <= diff_hours <= 3.5 and state.get("newsletter_gw", 0) < gw_id:
            try:
                trigger_newsletter(gw_id)
                state["newsletter_gw"] = gw_id
                save_state(state)
            except Exception as e:
                print(f"Error in Trigger 0 (Newsletter GW{gw_id}): {e}")
        elif state.get("newsletter_gw", 0) >= gw_id:
            print(f"GW {gw_id} newsletter already sent.")

    # Check 1: 20 Minutes Post-Deadline (Artifacts 1 & 2 via Telegram)
    eval_lock_ev = current_ev if (current_ev and not current_ev.get("finished")) else next_ev
    if eval_lock_ev:
        gw_id = eval_lock_ev["id"]
        dl_epoch = eval_lock_ev["deadline_time_epoch"]
        if now_epoch >= (dl_epoch + 1200):
            if state.get("locked_gw", 0) < gw_id:
                try:
                    trigger_deadline(gw_id, bs)
                    state["locked_gw"] = gw_id
                    save_state(state)
                except Exception as e:
                    print(f"Error in Trigger 1 (Locked GW{gw_id}): {e}")
            else:
                print(f"GW {gw_id} post-deadline cards already sent.")
        else:
            time_left = (dl_epoch + 1200) - now_epoch
            print(f"GW {gw_id} deadline + 20m not reached yet ({time_left // 60} mins remaining).")

    # Check 2: Post-Gameweek Settlement (Artifacts 3 & 4 via Telegram)
    if current_ev:
        gw_id = current_ev["id"]
        is_finished = current_ev.get("finished", False)
        data_checked = current_ev.get("data_checked", False)
        print(f"GW {gw_id} Settlement: finished={is_finished}, data_checked={data_checked}")
        if is_finished and data_checked:
            concluded_key = state.get("concluded_gw", state.get("over_gw", 0))
            if concluded_key < gw_id:
                try:
                    trigger_over(gw_id, bs)
                    state["concluded_gw"] = gw_id
                    state["over_gw"] = gw_id
                    save_state(state)
                except Exception as e:
                    print(f"Error in Trigger 2 (Concluded GW{gw_id}): {e}")
            else:
                print(f"GW {gw_id} post-gameweek cards already sent.")
        else:
            print(f"GW {gw_id} awaiting final settlement (auto-subs & bonus points).")

    print("Poll cycle finished.")

if __name__ == "__main__":
    force = os.environ.get("FORCE_TRIGGER", "").strip().lower()
    if force == "newsletter":
        print("FORCE TRIGGER: Executing GW10 Pre-Deadline Scout Newsletter...")
        trigger_newsletter(10)
    elif force == "deadline":
        bs = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
        print("FORCE TRIGGER: Executing GW10 Post-Deadline Artifacts 1 & 2...")
        trigger_deadline(10, bs)
    elif force == "concluded":
        bs = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
        print("FORCE TRIGGER: Executing GW9 Concluded Artifacts 3 & 4...")
        trigger_over(9, bs)
    else:
        poll_cycle()
