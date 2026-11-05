from http.server import BaseHTTPRequestHandler
import json, os, urllib.request, ssl, re

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
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

            # 4. Connect to Neon DB
            db_url = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DB_URL")
            if not db_url:
                # If database is not configured in serverless env, return verified FPL response
                self._respond(200, {
                    "success": True,
                    "duplicate": False,
                    "manager_name": manager_name,
                    "team_name": team_name,
                    "message": f"Verified manager {manager_name} ({team_name})!"
                })
                return

            clean_url = db_url.replace("&channel_binding=require", "").replace("channel_binding=require&", "").replace("?channel_binding=require", "")
            try:
                import psycopg2
                conn = psycopg2.connect(clean_url)
            except Exception:
                import pg8000.dbapi, urllib.parse
                p = urllib.parse.urlparse(clean_url)
                conn = pg8000.dbapi.connect(
                    user=p.username, password=p.password, host=p.hostname,
                    port=p.port or 5432, database=p.path.lstrip("/"),
                    ssl_context=ssl.create_default_context()
                )

            cur = conn.cursor()

            # Ensure table structure
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

            # 5. Check Global 50-Submissions Cap
            cur.execute("SELECT COUNT(*) FROM newsletter WHERE email IS NOT NULL AND email != '';")
            count = cur.fetchone()[0]
            if count >= 50:
                cur.close()
                conn.close()
                self._respond(403, {"success": False, "error": "Submission cap of 50 subscribers has been reached. Form is now closed."})
                return

            # 6. Check Duplicate: If data already exists, do not duplicate; keep existing
            cur.execute("""
                SELECT id, manager_name, team_name, email 
                FROM newsletter 
                WHERE fpl_team_id = %s OR email = %s;
            """, (team_id_int, email))
            existing = cur.fetchone()
            if existing:
                cur.close()
                conn.close()
                self._respond(200, {
                    "success": True,
                    "duplicate": True,
                    "manager_name": existing[1],
                    "team_name": existing[2] or team_name,
                    "message": f"Manager '{existing[1]}' is already registered in the system!"
                })
                return

            # 7. Insert New Verified User
            cur.execute("""
                INSERT INTO newsletter (manager_name, team_name, fpl_team_id, email, leagues)
                VALUES (%s, %s, %s, %s, %s);
            """, (manager_name, team_name, team_id_int, email, leagues_json))
            conn.commit()
            cur.close()
            conn.close()

            self._respond(200, {
                "success": True,
                "duplicate": False,
                "manager_name": manager_name,
                "team_name": team_name,
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
