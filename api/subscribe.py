from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, urllib.parse, ssl, re

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        clean_path = self.path.split('?')[0]
        if clean_path in ('/api/subscribe', '/api/subscribe/'):
            spots_remaining = 50
            total_active = 0
            db_url = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DB_URL")
            if db_url:
                try:
                    clean_url = db_url.replace("&channel_binding=require", "").replace("channel_binding=require&", "").replace("?channel_binding=require", "")
                    p = urllib.parse.urlparse(clean_url)
                    neon_url = f"https://{p.hostname}/sql"
                    req_headers = {
                        "Neon-Connection-String": clean_url,
                        "Content-Type": "application/json"
                    }
                    body_payload = json.dumps({"query": "SELECT COUNT(*) FROM newsletter WHERE id > 37 AND email IS NOT NULL AND email != '';"}).encode("utf-8")
                    req = urllib.request.Request(neon_url, data=body_payload, headers=req_headers)
                    with urllib.request.urlopen(req, context=CTX, timeout=5) as r:
                        c_res = json.loads(r.read().decode("utf-8"))
                        total_active = int(c_res["rows"][0]["count"])
                        spots_remaining = max(0, 50 - total_active)
                except Exception:
                    pass
            self._respond(200, {
                "status": "ok",
                "service": "Toxic 90 FPL Subscription API",
                "spots_remaining": spots_remaining,
                "total_active": total_active,
                "total_cap": 50
            })
            return

        # Serve static docs (index.html or archive)
        clean_path = self.path.split('?')[0]
        if clean_path in ('', '/'):
            clean_path = '/index.html'

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'docs', clean_path.lstrip('/'))
        if os.path.isfile(file_path):
            self.send_response(200)
            if file_path.endswith('.html'):
                self.send_header('Content-Type', 'text/html; charset=utf-8')
            elif file_path.endswith('.json'):
                self.send_header('Content-Type', 'application/json')
            elif file_path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif file_path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            else:
                self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            index_path = os.path.join(base_dir, 'docs', 'index.html')
            if os.path.isfile(index_path):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(index_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            req_json = json.loads(post_data.decode('utf-8'))
            email = str(req_json.get('email', '')).strip().lower()
            team_id = str(req_json.get('team_id', '')).strip()

            # 1. Validate Email format
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                self._respond(400, {"success": False, "error": "Invalid email address format."})
                return

            # 2. Validate Team ID
            if not team_id.isdigit():
                self._respond(400, {"success": False, "error": "Team ID must be a positive integer."})
                return
            team_id_int = int(team_id)

            # 3. Verify with official FPL API
            fpl_url = f"https://fantasy.premierleague.com/api/entry/{team_id_int}/"
            fpl_req = urllib.request.Request(fpl_url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(fpl_req, context=CTX, timeout=10) as r:
                    entry_data = json.loads(r.read().decode('utf-8'))
            except Exception:
                self._respond(404, {"success": False, "error": f"FPL Team ID '{team_id_int}' does not exist on Fantasy Premier League."})
                return

            first_name = entry_data.get("player_first_name", "")
            last_name = entry_data.get("player_last_name", "")
            manager_name = f"{first_name} {last_name}".strip() or entry_data.get("name", "FPL Manager")
            team_name = entry_data.get("name", "")
            leagues = entry_data.get("leagues", {}).get("classic", [])
            leagues_json = json.dumps([{"id": l["id"], "name": l["name"]} for l in leagues[:10]])

            # 4. Connect to Neon DB via Neon Serverless HTTP API
            db_url = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DB_URL")
            if not db_url:
                self._respond(500, {
                    "success": False,
                    "error": "DATABASE_URL is not configured in Vercel environment. Please add DATABASE_URL under Vercel Settings -> Environment Variables."
                })
                return

            clean_url = db_url.replace("&channel_binding=require", "").replace("channel_binding=require&", "").replace("?channel_binding=require", "")
            
            def run_neon_query(sql_str):
                p = urllib.parse.urlparse(clean_url)
                neon_url = f"https://{p.hostname}/sql"
                req_headers = {
                    "Neon-Connection-String": clean_url,
                    "Content-Type": "application/json"
                }
                body_payload = json.dumps({"query": sql_str}).encode("utf-8")
                req = urllib.request.Request(neon_url, data=body_payload, headers=req_headers)
                with urllib.request.urlopen(req, context=CTX, timeout=10) as r:
                    return json.loads(r.read().decode("utf-8"))

            # Ensure table structure
            run_neon_query("""
                CREATE TABLE IF NOT EXISTS newsletter (
                    id SERIAL PRIMARY KEY,
                    manager_name VARCHAR(150),
                    team_name VARCHAR(150),
                    fpl_team_id INTEGER NOT NULL UNIQUE,
                    email VARCHAR(255) UNIQUE,
                    leagues JSONB DEFAULT '[]'::jsonb
                );
            """)

            # 5. Check Global 50-Submissions Cap (Starts fresh from row 38 onwards)
            count_res = run_neon_query("SELECT COUNT(*) FROM newsletter WHERE id > 37 AND email IS NOT NULL AND email != '';")
            total_active = int(count_res["rows"][0]["count"])
            if total_active >= 50:
                self._respond(403, {"success": False, "error": "Submission cap of 50 subscribers has been reached. Form is now closed."})
                return

            # 6. Check Duplicate: If email, team ID, or team name already exists, REJECT
            email_esc = email.replace("'", "''")
            team_name_esc = team_name.replace("'", "''") if team_name else ""
            dup_sql = f"""
                SELECT id, manager_name, team_name, email, fpl_team_id 
                FROM newsletter 
                WHERE LOWER(TRIM(COALESCE(email, ''))) = '{email_esc}'
                   OR fpl_team_id = {team_id_int}
                   OR (team_name IS NOT NULL AND team_name != '' AND LOWER(TRIM(team_name)) = '{team_name_esc}');
            """
            dup_res = run_neon_query(dup_sql)
            if dup_res.get("rows"):
                existing = dup_res["rows"][0]
                ex_mgr = existing.get("manager_name", "Manager")
                ex_email = existing.get("email") or ""
                ex_tid = existing.get("fpl_team_id")
                ex_team = existing.get("team_name") or ""
                reasons = []
                if ex_email and ex_email.strip().lower() == email:
                    reasons.append(f"email '{email}' is already registered to manager '{ex_mgr}'")
                if ex_tid == team_id_int:
                    reasons.append(f"FPL Team ID '{team_id_int}' is already registered to manager '{ex_mgr}'")
                if ex_team and team_name and ex_team.strip().lower() == team_name.strip().lower():
                    reasons.append(f"team name '{team_name}' is already registered to manager '{ex_mgr}'")
                reason_str = " and ".join(reasons) if reasons else f"a record already exists for '{ex_mgr}'"
                self._respond(409, {
                    "success": False,
                    "duplicate": True,
                    "error": f"Registration Blocked: {reason_str.capitalize()}. Duplicate entries are strictly prohibited.",
                    "manager_name": ex_mgr
                })
                return

            # 7. Insert New Verified User
            mgr_esc = manager_name.replace("'", "''")
            leagues_esc = leagues_json.replace("'", "''")
            insert_sql = f"""
                INSERT INTO newsletter (manager_name, team_name, fpl_team_id, email, leagues)
                VALUES ('{mgr_esc}', '{team_name_esc}', {team_id_int}, '{email_esc}', '{leagues_esc}'::jsonb);
            """
            run_neon_query(insert_sql)

            self._respond(200, {
                "success": True,
                "duplicate": False,
                "manager_name": manager_name,
                "team_name": team_name,
                "spots_remaining": max(0, 50 - (total_active + 1)),
                "total_active": total_active + 1,
                "total_cap": 50,
                "message": f"Welcome, {manager_name} ({team_name})! Your subscription is confirmed."
            })

        except Exception as e:
            self._respond(500, {"success": False, "error": str(e)})

    def _respond(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(body).encode('utf-8'))

try:
    from app import app as app, application as application
except Exception:
    app = None
    application = None
