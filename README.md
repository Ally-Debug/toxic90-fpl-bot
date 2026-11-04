# Toxic 90 FPL Autonomous Engine ☢️

Autonomous notification and pre-deadline intelligence engine for the **Toxic 90** Fantasy Premier League mini-league (Classic ID: `19441`, Head-to-Head ID: `1069869`).

This service operates on a free-tier hourly cron schedule via GitHub Actions, reading official live Premier League API telemetry and distributing matchday intelligence across Telegram and Email.

---

## Architecture & Channels

* **Telegram Channel:** Delivers **strictly high-resolution PNG table cards** (Artifacts 1, 2, 3, and 4) at key matchday junctures.
* **Email Channel:** Delivers the **Pre-Deadline Scout Briefing** (responsive HTML/CSS email featuring Team of the Week, dynamic FDR runs, captaincy matrix, and manager press quotes) 3 hours before gameweek lock.
* **Web Archive (GitHub Pages):** Houses the neutral weekly Scout Briefing on the web.

---

## Automated Triggers

| Trigger | Timing | Output Channel | Content Delivered |
| :--- | :--- | :--- | :--- |
| **Trigger 0** | **T - 3 Hours** | **Email Only** | Pre-Deadline Scout Briefing (TOTW, dynamic FDR ticker, Captain/VC Matrix, Injury Watch) |
| **Trigger 1** | **T + 20 Mins** | **Telegram** (+ Email backup) | Artifact 1 (Top 5 & Captains) & Artifact 2 (Head-to-Head Matchups) |
| **Trigger 2** | **Post-GW Settlement** | **Telegram** (+ Email backup) | Artifact 3 (Classic Standings 1-14 with rank changes) & Artifact 4 (H2H Table & Results) |

---

## Required Environment Secrets

All credentials and sensitive keys are managed strictly via GitHub Repository Secrets:

* `TELEGRAM_BOT_TOKEN`: Telegram Bot API token.
* `TELEGRAM_CHAT_ID`: Destination Telegram chat or group ID.
* `SMTP_USERNAME`: Sender email address.
* `SMTP_PASSWORD`: Outbound mail app password.
* `EMAIL_RECIPIENT`: Recipient email distribution address(es).
