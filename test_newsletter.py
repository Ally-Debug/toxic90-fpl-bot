import urllib.request, json, ssl
from datetime import datetime, timezone

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

CLASSIC_LEAGUE_ID = 19441
H2H_LEAGUE_ID = 1069869

def build_newsletter_content(gw):
    req = urllib.request.Request("https://fantasy.premierleague.com/api/bootstrap-static/", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=12) as r:
        bs = json.loads(r.read().decode())
        
    ev = [e for e in bs['events'] if e['id'] == gw][0]
    deadline_str = ev['deadline_time']
    # Format deadline nicely
    dt = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    time_str = dt.strftime("%A, %b %d at %H:%M UTC")
    
    # Flagged players
    flagged = []
    for el in bs['elements']:
        if el['status'] != 'a' and float(el.get('selected_by_percent', 0)) >= 8.0:
            status_map = {'d': '75% / 50% Doubt', 'i': 'Injured / Ruled Out', 's': 'Suspended', 'u': 'Unavailable'}
            s_label = status_map.get(el['status'], 'Flagged')
            flagged.append(f"• {el['web_name']}: {s_label} ({el.get('news') or 'No details'})")
            
    # H2H Matchups
    req_h2h = urllib.request.Request(f"https://fantasy.premierleague.com/api/leagues-h2h-matches/league/{H2H_LEAGUE_ID}/?event={gw}", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req_h2h, context=CTX, timeout=12) as r:
        h2h_data = json.loads(r.read().decode())
        
    lines = [
        f"📰 TOXIC 90 ☢️ // GAMEWEEK {gw} PRE-DEADLINE BRIEFING",
        "══════════════════════════════════════════════",
        f"⏰ FINAL COUNTDOWN: 3 HOURS TO DEADLINE!",
        f"📅 Deadline Lock: {time_str}",
        "══════════════════════════════════════════════",
        "",
        f"⚔️ TOXIC 90 H2H MATCHUPS (GW{gw}):"
    ]
    for idx, m in enumerate(h2h_data.get('results', []), 1):
        lines.append(f" {idx}. {m['entry_1_player_name'][:16]:16s} vs {m['entry_2_player_name'][:16]:16s}")
        
    lines.append("")
    lines.append("🚑 KEY INJURY & SUSPENSION WATCH:")
    for f in flagged[:6]:
        lines.append(f)
        
    lines.append("")
    lines.append("══════════════════════════════════════════════")
    lines.append("🎯 PRE-DEADLINE CHECKLIST:")
    lines.append("  [x] Check your captain & vice-captain selections")
    lines.append("  [x] Verify your bench order in case of late benchings")
    lines.append("  [x] Check chip activation (cannot be cancelled once locked)")
    lines.append("══════════════════════════════════════════════")
    lines.append("Good luck to all managers! May the arrows be green 🟢")
    
    return "\n".join(lines)

if __name__ == "__main__":
    msg = build_newsletter_content(10)
    print(msg)
