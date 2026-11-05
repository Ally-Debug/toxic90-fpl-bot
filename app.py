import json, os, urllib.request, ssl, re

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def app(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET')
    path = environ.get('PATH_INFO', '/')

    # Handle CORS OPTIONS
    if method == 'OPTIONS':
        start_response('200 OK', [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type'),
            ('Content-Length', '0')
        ])
        return [b'']

    # POST /api/subscribe -> Register in Neon DB
    if method == 'POST' and (path == '/api/subscribe' or path.endswith('/subscribe')):
        try:
            try:
                content_length = int(environ.get('CONTENT_LENGTH', 0))
            except (ValueError, TypeError):
                content_length = 0
            body_bytes = environ['wsgi.input'].read(content_length) if content_length > 0 else b'{}'
            req_data = json.loads(body_bytes.decode('utf-8'))
            email = str(req_data.get('email', '')).strip().lower()
            team_id = str(req_data.get('team_id', '')).strip()
            team_name_in = str(req_data.get('team_name', '')).strip()

            # 1. Validate email
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                resp = json.dumps({"success": False, "error": "Invalid email address format."}).encode('utf-8')
                start_response('400 Bad Request', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
                return [resp]

            # 2. Validate team ID
            if not team_id.isdigit():
                resp = json.dumps({"success": False, "error": "Team ID must be a positive integer."}).encode('utf-8')
                start_response('400 Bad Request', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
                return [resp]
            team_id_int = int(team_id)

            # 3. Query FPL API
            fpl_url = f"https://fantasy.premierleague.com/api/entry/{team_id_int}/"
            fpl_req = urllib.request.Request(fpl_url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(fpl_req, context=CTX, timeout=10) as r:
                    entry = json.loads(r.read().decode('utf-8'))
            except Exception:
                resp = json.dumps({"success": False, "error": f"FPL Team ID '{team_id_int}' does not exist on Fantasy Premier League."}).encode('utf-8')
                start_response('404 Not Found', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
                return [resp]

            first_name = entry.get("player_first_name", "")
            last_name = entry.get("player_last_name", "")
            manager_name = f"{first_name} {last_name}".strip() or entry.get("name", "FPL Manager")
            team_name = entry.get("name", "") or team_name_in
            leagues = entry.get("leagues", {}).get("classic", [])
            leagues_json = json.dumps([{"id": l["id"], "name": l["name"]} for l in leagues[:10]])

            # 4. Connect to Neon DB
            db_url = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DB_URL")
            if not db_url:
                resp = json.dumps({"success": False, "error": "DATABASE_URL is not configured in Vercel environment."}).encode('utf-8')
                start_response('500 Internal Server Error', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
                return [resp]

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

            # 5. Check 50 Cap
            cur.execute("SELECT COUNT(*) FROM newsletter WHERE email IS NOT NULL AND email != '';")
            count = cur.fetchone()[0]
            if count >= 50:
                cur.close()
                conn.close()
                resp = json.dumps({"success": False, "error": "Cap of 50 subscribers reached."}).encode('utf-8')
                start_response('403 Forbidden', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
                return [resp]

            # 6. Check Duplicate
            cur.execute("""
                SELECT id, manager_name, team_name, email, fpl_team_id 
                FROM newsletter 
                WHERE LOWER(TRIM(COALESCE(email, ''))) = LOWER(TRIM(%s))
                   OR fpl_team_id = %s
                   OR (team_name IS NOT NULL AND team_name != '' AND LOWER(TRIM(team_name)) = LOWER(TRIM(%s)));
            """, (email, team_id_int, team_name))
            existing = cur.fetchone()
            if existing:
                cur.close()
                conn.close()
                resp = json.dumps({
                    "success": False,
                    "duplicate": True,
                    "error": f"Registration Blocked: Record already registered to manager '{existing[1]}'."
                }).encode('utf-8')
                start_response('409 Conflict', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
                return [resp]

            # 7. Insert Row into Neon DB
            cur.execute("""
                INSERT INTO newsletter (manager_name, team_name, fpl_team_id, email, leagues)
                VALUES (%s, %s, %s, %s, %s);
            """, (manager_name, team_name, team_id_int, email, leagues_json))
            conn.commit()
            cur.close()
            conn.close()

            resp = json.dumps({
                "success": True,
                "manager_name": manager_name,
                "team_name": team_name,
                "message": f"Successfully registered {manager_name} in Neon DB!"
            }).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [resp]

        except Exception as e:
            resp = json.dumps({"success": False, "error": str(e)}).encode('utf-8')
            start_response('500 Internal Server Error', [('Content-Type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            return [resp]

    # Serve static files from public/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    clean = path.split('?')[0].lstrip('/')
    if not clean or clean == 'index.html':
        target = os.path.join(base_dir, 'public', 'index.html')
    else:
        target = os.path.join(base_dir, 'public', clean)

    if not os.path.isfile(target):
        target = os.path.join(base_dir, 'public', 'index.html')

    if os.path.isfile(target):
        content_type = 'text/html; charset=utf-8' if target.endswith('.html') else 'application/octet-stream'
        start_response('200 OK', [
            ('Content-Type', content_type),
            ('Access-Control-Allow-Origin', '*')
        ])
        with open(target, 'rb') as f:
            return [f.read()]

    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']

application = app
