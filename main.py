import urllib.request, json, ssl, time, os, sys, uuid, shutil, subprocess, argparse
from datetime import datetime, timezone
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from card_generator import make_table_pdf
from recommendation_engine import run_recommendation_engine
from newsletter_builder import render_newsletter_html

# Vercel Serverless Function entrypoint export
try:
    from app import app as app, application as application
    from api.subscribe import handler as handler
except Exception:
    app = None
    application = None
    handler = None

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

CLASSIC_LEAGUE_ID = 19441
H2H_LEAGUE_ID = 1069869

# Credentials & Configuration (Loaded strictly from Environment / GitHub Secrets)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_IDS = [cid.strip() for cid in os.environ.get("TELEGRAM_CHAT_ID", "").split(",") if cid.strip()]

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "")
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DB_URL", "")

STATE_FILE = "state.json"
CACHE_DIR = "/tmp/fpl_cache"
DOCS_DIR = "docs"
PUBLIC_DIR = "public"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(os.path.join(DOCS_DIR, "archive"), exist_ok=True)
os.makedirs(os.path.join(PUBLIC_DIR, "archive"), exist_ok=True)

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
# NEON DB SUBSCRIBER MANAGEMENT
# ==========================================
def get_db_connection(db_url):
    """
    Establishes connection to Neon PostgreSQL using psycopg2-binary or pg8000.
    """
    if ":***" in db_url or ":****" in db_url:
        raise ValueError("DATABASE_URL contains literal asterisks (***). Please copy the connection string from Neon with the password revealed (click 'Show password' in Neon console).")

    clean_url = db_url.replace("&channel_binding=require", "").replace("channel_binding=require&", "").replace("?channel_binding=require", "")

    # 1. Try psycopg2 (natively supports postgresql:// with poolers and SSL options)
    try:
        import psycopg2
        return psycopg2.connect(clean_url)
    except Exception as e_psycopg2:
        print(f"psycopg2 notice: {e_psycopg2}")

    # 2. Fallback to pg8000
    import urllib.parse
    parsed = urllib.parse.urlparse(clean_url)
    import pg8000.dbapi
    return pg8000.dbapi.connect(
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip("/"),
        ssl_context=ssl.create_default_context()
    )

def get_newsletter_recipients():
    """
    Retrieves subscriber email addresses from Neon DB 'newsletter' table.
    Filters strictly for non-null, non-empty email addresses.
    Falls back gracefully to EMAIL_RECIPIENT secret if DATABASE_URL is not set.
    """
    if DATABASE_URL:
        try:
            conn = get_db_connection(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS newsletter (
                    id SERIAL PRIMARY KEY,
                    manager_name VARCHAR(150),
                    team_name VARCHAR(150),
                    fpl_team_id INTEGER NOT NULL UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    leagues JSONB DEFAULT '[]'::jsonb
                );
            """)
            try:
                cur.execute("ALTER TABLE newsletter ADD COLUMN IF NOT EXISTS team_name VARCHAR(150);")
            except Exception:
                pass
            conn.commit()
            cur.execute("SELECT email FROM newsletter WHERE email IS NOT NULL AND email != '';")
            rows = cur.fetchall()
            cur.close()
            conn.close()
            db_emails = [r[0].strip() for r in rows if r and r[0] and r[0].strip()]
            if db_emails:
                print(f"✅ Loaded {len(db_emails)} subscriber(s) from Neon DB 'newsletter' table: {db_emails}")
                return db_emails
            else:
                print("ℹ️ Neon DB 'newsletter' table currently has no active email addresses.")
        except Exception as e:
            print(f"⚠️ Neon DB lookup notice ({e}). Falling back to EMAIL_RECIPIENT secret.")

    # Fallback to comma-separated secret
    secret_emails = [r.strip() for r in EMAIL_RECIPIENT.split(",") if r.strip()]
    if secret_emails:
        print(f"ℹ️ Loaded {len(secret_emails)} subscriber(s) from EMAIL_RECIPIENT secret.")
    return secret_emails

def sync_leagues_for_manager(fpl_team_id):
    """
    Fetches official leagues and team name for a given FPL team ID from official FPL API
    and updates the 'leagues' JSONB and 'team_name' columns in Neon DB 'newsletter' table.
    If fpl_team_id is 'all', syncs leagues for all managers in the newsletter table.
    """
    if not DATABASE_URL:
        print("❌ DATABASE_URL or NEON_DB_URL is not configured in environment.")
        return False
        
    conn = get_db_connection(DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE newsletter ADD COLUMN IF NOT EXISTS team_name VARCHAR(150);")
        conn.commit()
    except Exception:
        pass
    
    # If 'all', query all team IDs in newsletter
    if str(fpl_team_id).lower() == 'all':
        cur.execute("SELECT fpl_team_id, manager_name FROM newsletter;")
        targets = cur.fetchall()
    else:
        cur.execute("SELECT fpl_team_id, manager_name FROM newsletter WHERE fpl_team_id = %s;", (int(fpl_team_id),))
        targets = cur.fetchall()
        if not targets:
            targets = [(int(fpl_team_id), "Unknown")]
            
    print(f"--> Syncing leagues and team names for {len(targets)} manager(s)...")
    for tid, m_name in targets:
        try:
            print(f"Fetching data from FPL for Team ID {tid} ({m_name})...")
            url = f"https://fantasy.premierleague.com/api/entry/{tid}/"
            data = fetch_json(url)
            fpl_team_name = data.get("name", "")
            classic_leagues = data.get("leagues", {}).get("classic", [])
            h2h_leagues = data.get("leagues", {}).get("h2h", [])
            
            leagues_payload = {
                "classic": [{"id": l["id"], "name": l["name"], "entry_rank": l.get("entry_rank")} for l in classic_leagues],
                "h2h": [{"id": l["id"], "name": l["name"], "entry_rank": l.get("entry_rank")} for l in h2h_leagues]
            }
            leagues_json = json.dumps(leagues_payload)
            
            # Update the newsletter table
            cur.execute("""
                UPDATE newsletter 
                SET leagues = %s,
                    team_name = COALESCE(NULLIF(%s, ''), team_name)
                WHERE fpl_team_id = %s;
            """, (leagues_json, fpl_team_name, tid))
            print(f"✅ Updated {m_name} (Team: '{fpl_team_name}', ID: {tid}): {len(classic_leagues)} Classic, {len(h2h_leagues)} H2H.")
        except Exception as e:
            print(f"❌ Failed to fetch/update leagues for Team ID {tid}: {e}")
            
    conn.commit()
    cur.close()
    conn.close()
    print("League and team name synchronization complete!")
    return True

def seed_toxic90_managers():
    """
    Fetches all Toxic 90 league managers from FPL API and populates the Neon DB 'newsletter' table
    with manager_name, fpl_team_id, and email as NULL so the user can easily fill in emails.
    """
    if not DATABASE_URL:
        print("❌ DATABASE_URL or NEON_DB_URL is not configured in environment.")
        return False
        
    print("--> Fetching all Toxic 90 managers from official FPL API (Classic: 19441, H2H: 1069869)...")
    all_mgrs = {}
    for lid in [CLASSIC_LEAGUE_ID, H2H_LEAGUE_ID]:
        is_h2h = (lid == H2H_LEAGUE_ID)
        endpoint = f"https://fantasy.premierleague.com/api/leagues-h2h/{lid}/standings/" if is_h2h else f"https://fantasy.premierleague.com/api/leagues-classic/{lid}/standings/"
        try:
            data = fetch_json(endpoint)
            for r in data.get("standings", {}).get("results", []):
                eid = r.get("entry")
                if not eid: continue
                if eid not in all_mgrs:
                    all_mgrs[eid] = {
                        "team_id": eid,
                        "name": r["player_name"],
                        "entry_name": r["entry_name"]
                    }
        except Exception as e:
            print(f"Warning fetching league {lid}: {e}")
            
    print(f"--> Found {len(all_mgrs)} unique managers across Toxic 90.")
    try:
        conn = get_db_connection(DATABASE_URL)
        cur = conn.cursor()
        # 1. Create trimmed table if needed
        cur.execute("""
            CREATE TABLE IF NOT EXISTS newsletter (
                id SERIAL PRIMARY KEY,
                manager_name VARCHAR(150),
                fpl_team_id INTEGER NOT NULL UNIQUE,
                email VARCHAR(255) UNIQUE,
                leagues JSONB DEFAULT '[]'::jsonb
            );
        """)
        # 2. Relax email constraint if it had NOT NULL
        try:
            cur.execute("ALTER TABLE newsletter ALTER COLUMN email DROP NOT NULL;")
        except Exception:
            pass
        # 3. Ensure fpl_team_id is UNIQUE
        try:
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'newsletter_fpl_team_id_key') THEN
                        ALTER TABLE newsletter ADD CONSTRAINT newsletter_fpl_team_id_key UNIQUE (fpl_team_id);
                    END IF;
                END $$;
            """)
        except Exception:
            pass
            
        inserted_count = 0
        for eid, m in sorted(all_mgrs.items(), key=lambda x: x[1]["name"].lower()):
            cur.execute("""
                INSERT INTO newsletter (manager_name, fpl_team_id, email)
                VALUES (%s, %s, NULL)
                ON CONFLICT (fpl_team_id) DO UPDATE
                SET manager_name = EXCLUDED.manager_name;
            """, (m["name"], eid))
            inserted_count += 1
            
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Successfully seeded {inserted_count} Toxic 90 managers into Neon DB 'newsletter' table!")
        print("All managers staged with email=NULL. You can now edit their email addresses in the Neon Console.")
        return True
    except Exception as e:
        print(f"❌ Error seeding managers into Neon DB: {e}")
        return False

def register_subscriber_in_db(email, fpl_team_id):
    """
    Registers a manager in Neon DB with live FPL API validation, duplicate prevention, and 50-subscriber global cap.
    """
    email = str(email).strip().lower()
    # 1. Validate Email format
    import re
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        print(f"❌ Invalid email format: '{email}'. Submission rejected.")
        return False

    # 2. Validate Team ID
    try:
        fpl_team_id_int = int(str(fpl_team_id).strip())
        if fpl_team_id_int <= 0:
            raise ValueError()
    except Exception:
        print(f"❌ Invalid FPL Team ID: '{fpl_team_id}'. Must be a positive integer.")
        return False
        
    # 3. Verify with official FPL API
    print(f"--> Validating FPL Team ID {fpl_team_id_int} with official Premier League API...")
    try:
        entry_data = fetch_json(f"https://fantasy.premierleague.com/api/entry/{fpl_team_id_int}/")
        first_name = entry_data.get("player_first_name", "")
        last_name = entry_data.get("player_last_name", "")
        manager_name = f"{first_name} {last_name}".strip() or entry_data.get("name", "FPL Manager")
        team_name = entry_data.get("name", "")
        leagues = entry_data.get("leagues", {}).get("classic", [])
        leagues_json = json.dumps([{"id": l["id"], "name": l["name"]} for l in leagues[:10]])
    except Exception as e:
        print(f"❌ FPL Team ID {fpl_team_id_int} does not exist on Fantasy Premier League: {e}")
        return False

    print(f"✅ Verified FPL Manager: '{manager_name}' (Team: '{team_name}', ID: {fpl_team_id_int})")

    if not DATABASE_URL:
        print("❌ DATABASE_URL or NEON_DB_URL is not configured in environment.")
        return False

    # 4. Check Database: 50 Cap & Duplicate Handling
    try:
        conn = get_db_connection(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS newsletter (
                id SERIAL PRIMARY KEY,
                manager_name VARCHAR(150),
                team_name VARCHAR(150),
                fpl_team_id INTEGER NOT NULL UNIQUE,
                email VARCHAR(255) UNIQUE,
                leagues JSONB DEFAULT '[]'::jsonb
            );
        """)
        
        # Scenario 2: Strict Duplicate Handling (Check Email, Team ID, AND Team Name)
        cur.execute("""
            SELECT id, manager_name, team_name, email, fpl_team_id 
            FROM newsletter 
            WHERE LOWER(TRIM(COALESCE(email, ''))) = LOWER(TRIM(%s))
               OR fpl_team_id = %s
               OR (team_name IS NOT NULL AND team_name != '' AND LOWER(TRIM(team_name)) = LOWER(TRIM(%s)));
        """, (email, fpl_team_id_int, team_name))
        existing = cur.fetchone()
        if existing:
            ex_id, ex_mgr, ex_team, ex_email, ex_tid = existing
            reasons = []
            if ex_email and ex_email.strip().lower() == email:
                reasons.append(f"email '{email}' is already registered to manager '{ex_mgr}'")
            if ex_tid == fpl_team_id_int:
                reasons.append(f"FPL Team ID '{fpl_team_id_int}' is already registered to manager '{ex_mgr}'")
            if ex_team and team_name and ex_team.strip().lower() == team_name.strip().lower():
                reasons.append(f"team name '{team_name}' is already registered to manager '{ex_mgr}'")
            
            reason_str = " and ".join(reasons) if reasons else f"a matching record already exists for '{ex_mgr}'"
            print(f"❌ REGISTRATION REJECTED: {reason_str.capitalize()}. Duplicate entries are strictly prohibited.")
            cur.close()
            conn.close()
            return False

        # Check Global 50-Submissions Cap
        cur.execute("SELECT COUNT(*) FROM newsletter WHERE email IS NOT NULL AND email != '';")
        active_count = cur.fetchone()[0]
        if active_count >= 50:
            print(f"🔒 Submission cap of 50 subscribers reached ({active_count}/50). New registration rejected.")
            cur.close()
            conn.close()
            return False

        # Scenario 3: New User Registration
        cur.execute("""
            INSERT INTO newsletter (manager_name, team_name, fpl_team_id, email, leagues)
            VALUES (%s, %s, %s, %s, %s);
        """, (manager_name, team_name, fpl_team_id_int, email, leagues_json))
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Successfully registered new subscriber: '{manager_name}' (Team: '{team_name}', ID: {fpl_team_id_int}) <{email}> [{active_count + 1}/50]!")
        return True
    except Exception as e:
        print(f"❌ Database error registering subscriber: {e}")
        return False
        print(f"❌ Database error registering subscriber: {e}")
        return False

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
    recipients = get_newsletter_recipients()
    print(f"--> Initiating Outbound Email Dispatch...")
    print(f"  SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"  SMTP Username: '{SMTP_USERNAME}'")
    print(f"  SMTP Password configured: {'YES' if SMTP_PASSWORD else 'NO (EMPTY SECRET!)'}")
    print(f"  Recipient Count: {len(recipients)}")
    
    if not SMTP_PASSWORD or not SMTP_USERNAME:
        print("[EMAIL DRY RUN] SMTP credentials not fully configured; skipping email transport.")
        return True
        
    if not recipients:
        print("⚠️ Warning: No email recipients found in Neon DB or EMAIL_RECIPIENT secret.")
        return False

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
            print(f"✅ Email successfully delivered to {len(recipients)} recipient(s): {recipients}")
            return True
    except Exception as e:
        print(f"❌ SMTP Dispatch Failed: {e}")
        raise e

def send_email_with_card_attachments(subject, caption, image_paths):
    if not SMTP_PASSWORD or not SMTP_USERNAME:
        print(f"[EMAIL CARDS DRY RUN] Subject: {subject} | Images: {image_paths}")
        return True
    recipients = get_newsletter_recipients()
    if not recipients:
        return True
        
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
            print(f"Cards email delivered to {len(recipients)} recipient(s).")
            return True
    except Exception as e:
        print(f"Cards email error: {e}")
        return False

# ==========================================
# TRIGGER 0: PRE-DEADLINE SCOUT NEWSLETTER (T - 3 HOURS)
# STRICT CHANNEL SEPARATION: EMAIL ONLY + GITHUB PAGES ARCHIVE
# ==========================================
def trigger_newsletter(gw=10):
    print(f"\n--> Executing Trigger 0: GW{gw} 3-HOUR PRE-DEADLINE SCOUT NEWSLETTER...")
    data = run_recommendation_engine()
    html_content = render_newsletter_html(data)
    
    # 1. Update Layer 2: GitHub Pages & Vercel Web Archive
    index_path = os.path.join(DOCS_DIR, "index.html")
    archive_path = os.path.join(DOCS_DIR, "archive", f"gw{gw}.html")
    pub_index = os.path.join(PUBLIC_DIR, "index.html")
    pub_archive = os.path.join(PUBLIC_DIR, "archive", f"gw{gw}.html")
    for p in (index_path, archive_path, pub_index, pub_archive):
        with open(p, "w", encoding="utf-8") as f:
            f.write(html_content)
    print(f"Updated Web archive in {DOCS_DIR} and {PUBLIC_DIR}")
    
    # 2. Dispatch Layer 1: Email Newsletter (Email ONLY - NOT Telegram)
    subject = f"Toxic 90 Scout: Game Week {gw} Final Briefing (3 Hours to Lock)"
    dispatched = send_html_email(subject, html_content)
    if dispatched:
        st = load_state()
        st["newsletter_gw"] = gw
        st["newsletter_sent"] = True
        st["newsletter_sent_at"] = datetime.now(timezone.utc).isoformat()
        save_state(st)
        print(f"✅ Verified & Recorded in State: GW {gw} Newsletter marked as SENT at {st['newsletter_sent_at']}")

# ==========================================
# TRIGGER 1: POST-DEADLINE ARTIFACTS 1 & 2 (T + 20 MINS)
# STRICT CHANNEL RULE: POST HIGH-RES IMAGES TO TELEGRAM
# ==========================================
def trigger_deadline(gw, bs=None):
    print(f"\n--> Executing Trigger 1: GW{gw} LOCKED (20 mins post-deadline)...")
    if bs is None:
        bs = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
    elements_map = {el["id"]: el["web_name"] for el in bs["elements"]}
    
    # 1. Artifact 1: Top 5 & Captains
    c_url = f"https://fantasy.premierleague.com/api/leagues-classic/{CLASSIC_LEAGUE_ID}/standings/"
    c_data = fetch_json(c_url)
    top5 = c_data["standings"]["results"][:5]
    
    valid_picks_count = 0
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
            valid_picks_count += 1
        except Exception as e:
            print(f"Could not fetch picks for {mgr_name}: {e}")
            
        art1_rows.append([str(rank), mgr_name, entry_name, cap_name, vc_name, chip_str])
        
    if top5 and valid_picks_count == 0:
        raise RuntimeError(f"FPL servers are still updating (HTTP 503 / game update). Picks for GW {gw} are locked. Deferring card generation until unlocked.")
        
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
    
    # Dispatch Email with Attached Cards
    try:
        send_email_with_card_attachments(
            f"[Toxic 90] Game Week {gw} Locked: Top 5 Captains & H2H Matchups",
            f"Game Week {gw} has locked! Here are the Top 5 Managers, Captain selections, and H2H Matchups:",
            [png_1, png_2]
        )
    except Exception as e:
        print(f"Email dispatch note (Telegram was delivered): {e}")

    # Record verified locked dispatch state
    st = load_state()
    st["locked_gw"] = gw
    st["locked_sent"] = True
    st["locked_sent_at"] = datetime.now(timezone.utc).isoformat()
    save_state(st)
    print(f"✅ Verified & Recorded in State: GW {gw} Post-Deadline Cards marked as SENT at {st['locked_sent_at']}")

# ==========================================
# TRIGGER 2: POST-GAMEWEEK FINAL SETTLEMENT (ARTIFACTS 3 & 4)
# CONDITION: finished == True AND data_checked == True
# ==========================================
def trigger_over(gw, bs=None):
    print(f"\n--> Executing Trigger 2: GW{gw} CONCLUDED (Official settlement complete)...")
    if bs is None:
        bs = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
    
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
    
    # Dispatch Email with Attached Cards
    try:
        send_email_with_card_attachments(
            f"[Toxic 90] Game Week {gw} Final Standings & H2H Results",
            f"Game Week {gw} is officially settled! Find the updated Classic and H2H tables below:",
            [png_3, png_4]
        )
    except Exception as e:
        print(f"Email dispatch note (Telegram was delivered): {e}")

    # Record verified concluded dispatch state
    st = load_state()
    st["concluded_gw"] = gw
    st["over_gw"] = gw
    st["concluded_sent"] = True
    st["concluded_sent_at"] = datetime.now(timezone.utc).isoformat()
    save_state(st)
    print(f"✅ Verified & Recorded in State: GW {gw} Final Settlement Cards marked as SENT at {st['concluded_sent_at']}")

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
    
    # ========================================================
    # TRIGGER 0: PRE-DEADLINE SCOUT NEWSLETTER (EMAIL ONLY)
    # TWO-COUNTER ARCHITECTURE WITH VERIFIED 'SENT' CATCH-UP
    # ========================================================
    target_dl_ev = next_ev or current_ev
    if target_dl_ev and not target_dl_ev.get("finished"):
        gw_id = target_dl_ev["id"]
        dl_str = target_dl_ev["deadline_time"]
        dl_dt = datetime.strptime(dl_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        
        # Counter 1: Minutes until lock (positive = pre-deadline, negative = post-deadline)
        diff_minutes = (dl_dt - now).total_seconds() / 60.0
        diff_hours = diff_minutes / 60.0
        
        # Counter 2: Verified Sent Status in persistent state
        is_sent = (state.get("newsletter_gw", 0) >= gw_id and state.get("newsletter_sent") is True)
        
        print(f"[Countdown Layer] GW {gw_id} Deadline: in {diff_hours:.2f} hrs ({int(diff_minutes)} mins). Verified Sent: {is_sent}")
        
        # Primary window: 4 to 5 hours (up to 300 mins) down to 0 mins before deadline.
        # If GitHub Actions is delayed by queues, this catch-up layer guarantees that whenever
        # any run wakes up between T-300m and T-0m, the newsletter WILL be sent if not yet marked sent.
        if 0.0 <= diff_minutes <= 300.0 and not is_sent:
            print(f"--> [TRIGGER 0 ACTIVATED] Catch-up check: GW {gw_id} deadline in {int(diff_minutes)} mins. State is NOT sent. Dispatching newsletter...")
            try:
                trigger_newsletter(gw_id)
            except Exception as e:
                print(f"Error in Trigger 0 (Newsletter GW{gw_id}): {e}")
        elif is_sent:
            print(f"✅ Verified: GW {gw_id} newsletter already sent (recorded at {state.get('newsletter_sent_at', 'earlier run')}).")
        elif diff_minutes > 300.0:
            print(f"GW {gw_id} deadline is more than 5 hours away ({diff_hours:.2f} hrs / {int(diff_minutes)} mins). Standing by.")

    # ========================================================
    # TRIGGER 1: POST-DEADLINE ARTIFACTS 1 & 2 (TELEGRAM + EMAIL CARDS)
    # CATCH-UP ARCHITECTURE: FIRES 20+ MINS AFTER DEADLINE
    # ========================================================
    eval_lock_ev = current_ev if (current_ev and not current_ev.get("finished")) else next_ev
    if eval_lock_ev:
        gw_id = eval_lock_ev["id"]
        dl_epoch = eval_lock_ev["deadline_time_epoch"]
        is_locked_sent = (state.get("locked_gw", 0) >= gw_id and state.get("locked_sent") is True)
        minutes_past_dl = (now_epoch - dl_epoch) / 60.0
        
        print(f"[Post-Deadline Layer] GW {gw_id} elapsed since deadline: {minutes_past_dl:.1f} mins. Verified Sent: {is_locked_sent}")
        
        if now_epoch >= (dl_epoch + 1200): # 20 minutes (1200s) post-deadline
            if not is_locked_sent:
                print(f"--> [TRIGGER 1 ACTIVATED] GW {gw_id} locked ({int(minutes_past_dl)} mins elapsed). Dispatching Artifacts 1 & 2...")
                try:
                    trigger_deadline(gw_id, bs)
                except Exception as e:
                    print(f"Error in Trigger 1 (Locked GW{gw_id}): {e}")
            else:
                print(f"✅ Verified: GW {gw_id} post-deadline cards already sent (recorded at {state.get('locked_sent_at', 'earlier run')}).")
        else:
            time_left = (dl_epoch + 1200) - now_epoch
            print(f"GW {gw_id} deadline + 20m threshold in {time_left // 60} mins.")

    # ========================================================
    # TRIGGER 2: POST-GAMEWEEK FINAL SETTLEMENT (ARTIFACTS 3 & 4)
    # ========================================================
    if current_ev:
        gw_id = current_ev["id"]
        is_finished = current_ev.get("finished", False)
        data_checked = current_ev.get("data_checked", False)
        is_concluded_sent = (state.get("concluded_gw", 0) >= gw_id and state.get("concluded_sent") is True)
        
        print(f"[Settlement Layer] GW {gw_id} Settlement: finished={is_finished}, data_checked={data_checked}. Verified Sent: {is_concluded_sent}")
        if is_finished and data_checked:
            if not is_concluded_sent:
                print(f"--> [TRIGGER 2 ACTIVATED] GW {gw_id} settled. Dispatching Artifacts 3 & 4...")
                try:
                    trigger_over(gw_id, bs)
                except Exception as e:
                    print(f"Error in Trigger 2 (Concluded GW{gw_id}): {e}")
            else:
                print(f"✅ Verified: GW {gw_id} final settlement cards already sent (recorded at {state.get('concluded_sent_at', 'earlier run')}).")
        else:
            print(f"GW {gw_id} awaiting final settlement (auto-subs & bonus points).")

    print("Poll cycle finished.")

# ==========================================
# CLI ENTRY POINT & WORKFLOW RUNNER
# ==========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Toxic 90 FPL Autonomous Engine & CLI")
    parser.add_argument("--mode", "-m", choices=["poll", "scout", "newsletter", "locked", "deadline", "settled", "concluded", "preview", "seed_managers"], default="poll", help="Action mode to execute")
    parser.add_argument("--gw", type=int, default=10, help="Gameweek ID for manual runs")
    parser.add_argument("--add-subscriber", nargs=2, metavar=("EMAIL", "FPL_TEAM_ID"), help="Register a new subscriber in Neon DB")
    parser.add_argument("--seed-managers", action="store_true", help="Fetch all Toxic 90 managers from FPL API and seed into Neon DB")
    parser.add_argument("--sync-leagues", metavar="TEAM_ID", help="Fetch and insert official FPL leagues as JSON into Neon DB for a team ID (or 'all')")
    
    args, unknown = parser.parse_known_args()

    # Priority 0: Sync leagues for a team ID or all teams
    if args.sync_leagues:
        sync_leagues_for_manager(args.sync_leagues)
        sys.exit(0)

    # Priority 1: Seed Toxic 90 managers from FPL API
    if args.seed_managers or args.mode == "seed_managers":
        seed_toxic90_managers()
        sys.exit(0)

    # Priority 2: Direct subscriber addition via CLI
    if args.add_subscriber:
        sub_email, sub_fpl_id = args.add_subscriber
        ok = register_subscriber_in_db(sub_email, int(sub_fpl_id))
        if not ok:
            print("❌ Add subscriber failed. Process aborted.")
            sys.exit(1)
        sys.exit(0)

    # Priority 2: Check FORCE_TRIGGER environment variable (for GitHub Actions backward compatibility)
    force_env = os.environ.get("FORCE_TRIGGER", "").strip().lower()
    selected_mode = args.mode
    if force_env and force_env != "poll_cycle" and force_env != "none":
        selected_mode = force_env

    # Priority 3: Execute selected mode
    if selected_mode in ["scout", "newsletter"]:
        print(f"CLI: Executing Gameweek {args.gw} Pre-Deadline Scout Newsletter...")
        trigger_newsletter(args.gw)
    elif selected_mode in ["locked", "deadline"]:
        print(f"CLI: Executing Gameweek {args.gw} Post-Deadline Cards (Artifacts 1 & 2)...")
        trigger_deadline(args.gw)
    elif selected_mode in ["settled", "concluded"]:
        print(f"CLI: Executing Gameweek {args.gw-1 if args.gw > 1 else 9} Final Settlement Cards (Artifacts 3 & 4)...")
        trigger_over(args.gw - 1 if args.gw > 1 else 9)
    elif selected_mode == "preview":
        print(f"CLI: Generating local preview for GW{args.gw}...")
        data = run_recommendation_engine()
        html = render_newsletter_html(data)
        out_path = f"preview_gw{args.gw}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        # Also sync docs and public index for web archive
        for p in (
            os.path.join(DOCS_DIR, "index.html"),
            os.path.join(DOCS_DIR, "archive", f"gw{args.gw}.html"),
            os.path.join(PUBLIC_DIR, "index.html"),
            os.path.join(PUBLIC_DIR, "archive", f"gw{args.gw}.html")
        ):
            with open(p, "w", encoding="utf-8") as f:
                f.write(html)
        print(f"Preview saved to {out_path} and synced to {DOCS_DIR}/ and {PUBLIC_DIR}/ ({len(html)} bytes).")
    else:
        poll_cycle()
