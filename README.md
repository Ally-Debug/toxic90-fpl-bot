# Toxic 90 FPL Autonomous Engine ☢️

Autonomous notification, alerting, and pre-deadline tactical intelligence engine for the **Toxic 90** Fantasy Premier League mini-league (Classic ID: `19441`, Head-to-Head ID: `1069869`).

This service operates on a 100% free-tier hourly cron schedule via GitHub Actions, reading official live Premier League API telemetry and distributing matchday intelligence across Telegram, Email, and GitHub Pages.

---

## Architecture & Channels

* **Telegram Channel (`@Toxic_90_bot`):** Delivers **strictly high-resolution PNG visual cards** (Artifacts 1, 2, 3, and 4) at key matchday junctures. Zero textual clutter or newsletter spam is sent to Telegram.
* **Email Channel:** Delivers the **Pre-Deadline Scout Briefing** (responsive HTML/CSS email featuring the 3-4-3 tactical pitch formation, full 15-player specifics table, Golden Run FDR ticker, and medical/suspension bulletins) 3 hours before gameweek lock.
* **Web Archive (GitHub Pages):** Houses the neutral weekly Scout Briefing and an interactive newsletter subscription box on the web:  
  👉 **[https://ally-debug.github.io/toxic90-fpl-bot/](https://ally-debug.github.io/toxic90-fpl-bot/)**

---

## Automated Triggers

| Trigger | Timing | Output Channel | Content Delivered |
| :--- | :--- | :--- | :--- |
| **Trigger 0** | **T - 3 Hours** | **Email Only** | Pre-Deadline Scout Briefing (3-4-3 Pitch TOTW, Golden Run ticker, Captain/VC Matrix, Injury/Suspension Ledger) |
| **Trigger 1** | **T + 20 Mins** | **Telegram** (+ Email backup) | Artifact 1 (Top 5 & Captains) & Artifact 2 (Head-to-Head Matchups) |
| **Trigger 2** | **Post-GW Settlement** | **Telegram** (+ Email backup) | Artifact 3 (Classic Standings 1-14 with rank changes) & Artifact 4 (H2H Table & Results) |

---

## Integrated CLI Usage

You can run the engine directly from the command line, locally or via GitHub Actions:

```bash
# 1. Run the hourly autonomous poll cycle (default)
python main.py --mode poll

# 2. Trigger the Pre-Deadline Scout Newsletter (Generates HTML + sends Email)
python main.py --mode scout --gw 10

# 3. Trigger 20-min Post-Deadline Cards (Artifacts 1 & 2 to Telegram)
python main.py --mode locked --gw 10

# 4. Trigger Post-Gameweek Settlement Cards (Artifacts 3 & 4 to Telegram)
python main.py --mode settled --gw 9

# 5. Generate a local HTML preview without dispatching emails or Telegram photos
python main.py --mode preview --gw 10

# 6. Register a new subscriber directly into Neon DB (verifies Team ID with FPL API)
python main.py --add-subscriber manager@example.com 19441
```

You can also trigger any of these modes from GitHub Actions under the **Actions** tab (`Toxic 90 Interactive CLI` or `Toxic 90 FPL Autonomous Monitor`) or via GitHub CLI:
```bash
gh workflow run fpl_cron.yml -f mode=newsletter -f gameweek=10
```

---

## Neon DB & Subscriber Management

To remove the need for updating comma-separated recipient strings in GitHub Secrets, subscriber management connects to a central Neon PostgreSQL database table:

```sql
CREATE TABLE IF NOT EXISTS newsletter (
    id SERIAL PRIMARY KEY,
    manager_name VARCHAR(150),
    fpl_team_id INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    leagues JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

When a user subscribes with their email and FPL Team ID, the engine queries `https://fantasy.premierleague.com/api/entry/{team_id}/` to verify the team, fetch their official manager name, and record their mini-league affiliations into the `leagues` JSONB field.

---

## Required Environment Secrets

All credentials and sensitive keys are managed strictly via GitHub Repository Secrets:

* `TELEGRAM_BOT_TOKEN`: Telegram Bot API token.
* `TELEGRAM_CHAT_ID`: Destination Telegram chat or group ID.
* `SMTP_SERVER`: Outbound SMTP server (`smtp.gmail.com`).
* `SMTP_PORT`: SMTP port (`587`).
* `SMTP_USERNAME`: Sender email address.
* `SMTP_PASSWORD`: 16-character Google App Password.
* `DATABASE_URL` *(or `NEON_DB_URL`)*: Neon PostgreSQL connection string (e.g. `postgres://user:pass@ep-xyz.neon.tech/neondb?sslmode=require`).
* `EMAIL_RECIPIENT`: Comma-separated fallback email address(es) if Neon DB is not yet connected.
