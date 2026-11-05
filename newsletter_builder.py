def render_newsletter_html(data):
    gw = data.get('next_gw', 10)
    deadline = data.get('deadline_formatted', 'Friday, Nov 06 at 18:30 UTC / Saturday, Nov 07 at 12:00 AM IST')

    html_lines = []
    html_lines.append(f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Toxic 90 Intelligence Briefing - Game Week {gw}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px 10px; color: #1e293b;">
<div style="max-width: 680px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07); border: 1px solid #e2e8f0;">
    
    <!-- Header Banner -->
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 28px 24px; color: #ffffff;">
        <div style="background: rgba(255,255,255,0.15); display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 10px;">PRE-DEADLINE INTELLIGENCE</div>
        <h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px;">TOXIC 90 ☢️ // GAME WEEK {gw} SCOUT BRIEFING</h1>
        <p style="margin: 6px 0 0 0; color: #cbd5e1; font-size: 13px;">Alistair's AI Intelligence System & Autonomous Telemetry</p>
    </div>

    <!-- Deadline Alert Bar -->
    <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 14px 20px;">
        <div style="font-weight: 800; color: #991b1b; font-size: 14px;">⏰ FINAL 3-HOUR DEADLINE COUNTDOWN</div>
        <div style="color: #7f1d1d; font-size: 12.5px; margin-top: 2px;">
            <b>Lock Time:</b> {deadline}.<br>
            All transfers, captaincy selections, and chips freeze strictly at deadline.
        </div>
    </div>

    <div style="padding: 24px;">
""")

    # Section 1A: Captains
    html_lines.append(f"""
        <!-- Section 1A: Captain Recommendations -->
        <div style="margin-bottom: 28px;">
            <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #2563eb; padding-bottom: 6px;">
                👑 Captain Recommendations (GW{gw})
            </h3>
            <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
""")
    for c in data['captains']:
        html_lines.append(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
                    <span style="{c['tier_badge']} padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800; text-transform: uppercase;">{c['tier']}</span>
                    <b style="margin-left: 8px; font-size: 14px; color: #0f172a;">{c['player']}</b> ({c['club']} - {c['cost']}) <span style="color:#64748b; font-size:12px;">vs {c['opp']}</span>
                    <div style="font-size: 12.5px; color: #475569; margin-top: 6px; line-height: 1.5;">{c['analysis']}</div>
                </div>
        """)
    html_lines.append("""
            </div>
        </div>
""")

    # Section 1B: Vice Captains
    html_lines.append(f"""
        <!-- Section 1B: Vice-Captain Recommendations -->
        <div style="margin-bottom: 28px;">
            <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #64748b; padding-bottom: 6px;">
                🛡️ Vice-Captain Recommendations (GW{gw} Insurance)
            </h3>
            <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
""")
    for vc in data['vice_captains']:
        html_lines.append(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px;">
                    <span style="{vc['tier_badge']} padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800; text-transform: uppercase;">{vc['tier']}</span>
                    <b style="margin-left: 8px; font-size: 14px; color: #0f172a;">{vc['player']}</b> ({vc['club']} - {vc['cost']}) <span style="color:#64748b; font-size:12px;">vs {vc['opp']}</span>
                    <div style="font-size: 12.5px; color: #475569; margin-top: 6px; line-height: 1.5;">{vc['analysis']}</div>
                </div>
        """)
    html_lines.append("""
            </div>
        </div>
""")

    # Section 2: 5-Gameweek Fixture Ticker & Golden Run
    html_lines.append(f"""
        <!-- Section 2: 5-Gameweek FDR Ticker -->
        <div style="margin-bottom: 28px;">
            <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #16a34a; padding-bottom: 6px;">
                🟢 Dynamic 5-Gameweek Fixture Ticker (GW{gw} – GW{gw+4})
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 12.5px; text-align: left; background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Team</th>
                        <th style="padding: 10px 12px; text-align: center; font-weight: 700; color: #475569;">Avg FDR</th>
                        <th style="padding: 10px 12px; font-weight: 700; color: #475569;">Upcoming 5 Fixtures (FDR Rating)</th>
                    </tr>
                </thead>
                <tbody>
""")
    for t in data['fdr_teams']:
        badges = []
        for opp, loc, fdr in t['runs']:
            bg = "#16a34a" if fdr <= 2 else ("#ca8a04" if fdr == 3 else "#dc2626")
            badges.append(f"<span style='background:{bg}; color:white; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:700;'>{opp}({loc})</span>")
        html_lines.append(f"""
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 10px 12px; font-weight: 700; color: #0f172a;">{t['name']} ({t['short']})</td>
                        <td style="padding: 10px 12px; text-align: center; font-weight: 800; color: #16a34a;">{t['avg']:.2f}</td>
                        <td style="padding: 10px 12px;">{' '.join(badges)}</td>
                    </tr>
        """)
    html_lines.append("""
                </tbody>
            </table>

            <!-- Golden Run Spotlight Box -->
            <div style="margin-top: 12px; background: #fefce8; border: 1px solid #fef08a; border-left: 4px solid #eab308; padding: 14px 16px; border-radius: 6px;">
                <b style="color: #854d0e; font-size: 13.5px;">🏆 The Golden Run Spotlight: Aston Villa (AVL)</b>
                <p style="margin: 4px 0 0 0; color: #713f12; font-size: 12px; line-height: 1.5;">
                    Aston Villa holds the undisputed <b>Golden Run</b> across the next five gameweeks with a league-best <b>2.40 Average FDR</b>. With home matches against Southampton, Everton, and Crystal Palace, targeting Villa attacking and defensive assets—led by <b>Nicolas Jackson</b> (£7.0m, FWD), <b>Johan Manzambi</b> (£6.1m, MID), and <b>Matty Cash</b> (£4.3m, DEF upon return)—provides prime upside for upcoming transfer allocations.
                </p>
            </div>
        </div>
""")

    # Section 3: 15-Player Optimal Scout Squad WITH PITCH GRAPHIC
    html_lines.append(f"""
        <!-- Section 3: 15-Player Optimal Scout Squad -->
        <div style="margin-bottom: 28px;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; border-bottom: 2px solid #8b5cf6; padding-bottom: 6px; margin-bottom: 12px;">
                <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin: 0;">
                    🎯 Optimal Scout Team of the Week (Full 15-Man Squad)
                </h3>
                <span style="font-size: 12px; font-weight: 700; color: #6d28d9; background: #ede9fe; padding: 2px 8px; border-radius: 12px;">Squad Cost: £98.0m / £100.0m</span>
            </div>
            
            <p style="margin: 0 0 14px 0; font-size: 12.5px; color: #475569;">
                ⚡ <b>System Model:</b> The team has been created using <b>Alistair's AI intelligence system</b>. Selected 15 total cost: <b>£98.0m</b> (under the £100.0m FPL budget cap), featuring an optimal 3-4-3 Starting XI supported by high-security bench coverage.
            </p>

            <!-- GRAPHICAL PITCH DEPICTION (3-4-3 Formation) -->
            <div style="background: linear-gradient(180deg, #15803d 0%, #166534 100%); border-radius: 10px; padding: 18px 12px; margin-bottom: 16px; border: 2px solid #14532d; position: relative; box-shadow: inset 0 0 20px rgba(0,0,0,0.2);">
                <div style="text-align: center; color: rgba(255,255,255,0.85); font-size: 11px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 14px; border-bottom: 1px dashed rgba(255,255,255,0.25); padding-bottom: 6px;">
                    ⚽ Tactical Formation: 3-4-3 Starting XI
                </div>

                <!-- FORWARDS ROW (3) -->
                <div style="display: flex; justify-content: space-around; margin-bottom: 16px;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 10px; text-align: center; width: 30%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #dc2626; text-transform: uppercase;">FWD</div>
                        <div style="font-size: 12px; font-weight: 800; color: #0f172a;">N. Jackson</div>
                        <div style="font-size: 10px; color: #64748b; font-weight: 600;">AVL • £7.0m</div>
                    </div>
                    <div style="background: #fef08a; border: 2px solid #eab308; border-radius: 6px; padding: 6px 10px; text-align: center; width: 32%; box-shadow: 0 2px 6px rgba(0,0,0,0.25);">
                        <div style="font-size: 9px; font-weight: 800; color: #854d0e; text-transform: uppercase;">👑 FWD (C)</div>
                        <div style="font-size: 12px; font-weight: 800; color: #0f172a;">Haaland</div>
                        <div style="font-size: 10px; color: #713f12; font-weight: 700;">MCI • £15.8m</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 10px; text-align: center; width: 30%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #dc2626; text-transform: uppercase;">FWD</div>
                        <div style="font-size: 12px; font-weight: 800; color: #0f172a;">Evanilson</div>
                        <div style="font-size: 10px; color: #64748b; font-weight: 600;">BOU • £6.4m</div>
                    </div>
                </div>

                <!-- MIDFIELDERS ROW (4) -->
                <div style="display: flex; justify-content: space-between; margin-bottom: 16px; gap: 6px;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 6px; text-align: center; width: 23%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #2563eb; text-transform: uppercase;">MID</div>
                        <div style="font-size: 11.5px; font-weight: 800; color: #0f172a;">P. Neto</div>
                        <div style="font-size: 9.5px; color: #64748b; font-weight: 600;">CHE • £6.6m</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 6px; text-align: center; width: 23%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #2563eb; text-transform: uppercase;">MID</div>
                        <div style="font-size: 11.5px; font-weight: 800; color: #0f172a;">Rice</div>
                        <div style="font-size: 9.5px; color: #64748b; font-weight: 600;">ARS • £7.4m</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 6px; text-align: center; width: 23%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #2563eb; text-transform: uppercase;">MID</div>
                        <div style="font-size: 11.5px; font-weight: 800; color: #0f172a;">Iwobi</div>
                        <div style="font-size: 9.5px; color: #64748b; font-weight: 600;">FUL • £5.4m</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 6px; text-align: center; width: 23%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #2563eb; text-transform: uppercase;">MID</div>
                        <div style="font-size: 11.5px; font-weight: 800; color: #0f172a;">Tavernier</div>
                        <div style="font-size: 9.5px; color: #64748b; font-weight: 600;">BOU • £6.6m</div>
                    </div>
                </div>

                <!-- DEFENDERS ROW (3) -->
                <div style="display: flex; justify-content: space-around; margin-bottom: 16px;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 10px; text-align: center; width: 30%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #16a34a; text-transform: uppercase;">DEF</div>
                        <div style="font-size: 12px; font-weight: 800; color: #0f172a;">Konsa</div>
                        <div style="font-size: 10px; color: #64748b; font-weight: 600;">ARS • £4.8m</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 10px; text-align: center; width: 30%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #16a34a; text-transform: uppercase;">DEF (VC)</div>
                        <div style="font-size: 12px; font-weight: 800; color: #0f172a;">Gabriel</div>
                        <div style="font-size: 10px; color: #64748b; font-weight: 600;">ARS • £8.0m</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 10px; text-align: center; width: 30%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #16a34a; text-transform: uppercase;">DEF</div>
                        <div style="font-size: 12px; font-weight: 800; color: #0f172a;">De Cuyper</div>
                        <div style="font-size: 10px; color: #64748b; font-weight: 600;">BHA • £5.4m</div>
                    </div>
                </div>

                <!-- GOALKEEPER (1) -->
                <div style="display: flex; justify-content: center; margin-bottom: 12px;">
                    <div style="background: rgba(255,255,255,0.95); border-radius: 6px; padding: 6px 14px; text-align: center; min-width: 140px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <div style="font-size: 9px; font-weight: 800; color: #ea580c; text-transform: uppercase;">GOALKEEPER</div>
                        <div style="font-size: 12px; font-weight: 800; color: #0f172a;">Verbruggen</div>
                        <div style="font-size: 10px; color: #64748b; font-weight: 600;">BHA • £4.6m</div>
                    </div>
                </div>

                <!-- BENCH DUGOUT BAR -->
                <div style="background: rgba(15, 23, 42, 0.85); border-radius: 6px; padding: 8px 10px; color: white; display: flex; justify-content: space-between; align-items: center; font-size: 10.5px;">
                    <span style="font-weight: 800; color: #94a3b8; text-transform: uppercase; font-size: 9.5px;">🪑 BENCH:</span>
                    <span><b>B1:</b> Kinsky (TOT £4.4m)</span>
                    <span><b>B2:</b> Van Hecke (TOT £5.0m)</span>
                    <span><b>B3:</b> Vuskovic (BHA £5.2m)</span>
                    <span><b>B4:</b> Ayari (BHA £5.4m)</span>
                </div>
            </div>

            <!-- DETAILED SPECIFICS TABLE -->
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Player Name</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">GW{gw} Strength</th>
                        <th style="padding: 9px 10px; text-align: center; font-weight: 700; color: #475569;">GW{gw} Creativity</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Remark (Why this pick)</th>
                    </tr>
                </thead>
                <tbody>
""")

    for p in data['squad_15']:
        badge_bg = "#eff6ff" if "XI" in p['type'] else "#f3f4f6"
        badge_color = "#1e40af" if "XI" in p['type'] else "#4b5563"
        html_lines.append(f"""
                    <tr style="border-bottom: 1px solid #e2e8f0; background: {'#ffffff' if 'XI' in p['type'] else '#fafafa'};">
                        <td style="padding: 8px 10px; font-weight: 700; color: #0f172a; white-space: nowrap;">
                            <span style="background:{badge_bg}; color:{badge_color}; font-size:9.5px; font-weight:800; padding:1px 5px; border-radius:3px; margin-right:4px;">{p['type']}</span>
                            {p['name']} <span style="font-size:10.5px; color:#64748b;">({p['club']} - £{p['cost']:.1f}m)</span>
                        </td>
                        <td style="padding: 8px 10px; font-size: 11.5px; color: #334155;">{p['strength']}</td>
                        <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #2563eb;">{p['creativity']}</td>
                        <td style="padding: 8px 10px; font-size: 11.5px; color: #475569; line-height: 1.4;">{p['remark']}</td>
                    </tr>
        """)

    html_lines.append("""
                </tbody>
            </table>

            <!-- Scout Summary Highlight -->
            <div style="margin-top: 12px; background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; padding: 12px 16px; border-radius: 6px;">
                <b style="color: #166534; font-size: 13px;">🧠 Key Analyst Observation & Vital Picks:</b>
                <p style="margin: 4px 0 0 0; color: #14532d; font-size: 12px; line-height: 1.5;">
                    The data highlights significant form surges across select mid-priced assets. <b>Keep an eye on Maxim De Cuyper and Evanilson—these two players are poised to be vital</b> for your squad over this upcoming stretch. De Cuyper's 288.0 creativity delivers assist potential rivaling premium playmakers, while Evanilson spearheads a Bournemouth frontline with immense penalty-box touch volume.
                </p>
            </div>
        </div>
""")

    # Section 4A: Injuries
    html_lines.append("""
        <!-- Section 4A: Key Injury Radar -->
        <div style="margin-bottom: 28px;">
            <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #ef4444; padding-bottom: 6px;">
                🚑 Key Injury Radar (Medical & Press Room Bulletins)
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Player</th>
                        <th style="padding: 9px 10px; text-align: center; font-weight: 700; color: #475569;">Status</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Official Manager / Medical Intelligence</th>
                    </tr>
                </thead>
                <tbody>
""")
    for inj in data['injuries']:
        html_lines.append(f"""
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 10px; font-weight: 700; color: #0f172a; white-space: nowrap;">{inj['name']} <span style="font-size:10.5px; color:#64748b;">({inj['club']})</span></td>
                        <td style="padding: 8px 10px; text-align: center;"><span style="{inj['badge']} padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 800;">{inj['status']}</span></td>
                        <td style="padding: 8px 10px; font-size: 11.5px; color: #475569; line-height: 1.4;">{inj['details']}</td>
                    </tr>
        """)
    html_lines.append("""
                </tbody>
            </table>
        </div>
""")

    # Section 4B: Suspensions
    html_lines.append("""
        <!-- Section 4B: Suspended Players Ledger -->
        <div style="margin-bottom: 28px;">
            <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #991b1b; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #b91c1c; padding-bottom: 6px;">
                🟥 Suspended Players Ledger (Cards & Disciplinary Bans)
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #fef2f2; border-bottom: 1px solid #fecaca;">
                        <th style="padding: 9px 10px; font-weight: 700; color: #991b1b;">Player</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #991b1b;">Disciplinary Reason</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #991b1b;">Expected Return</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #991b1b;">Tactical Squad Impact</th>
                    </tr>
                </thead>
                <tbody>
""")
    for sus in data['suspensions']:
        html_lines.append(f"""
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 10px; font-weight: 700; color: #991b1b; white-space: nowrap;">{sus['name']} <span style="font-size:10.5px; color:#64748b;">({sus['club']})</span></td>
                        <td style="padding: 8px 10px; font-size: 11.5px; color: #b91c1c; font-weight: 600;">{sus['reason']}</td>
                        <td style="padding: 8px 10px; font-size: 11.5px; color: #475569; white-space: nowrap;">{sus['return']}</td>
                        <td style="padding: 8px 10px; font-size: 11.5px; color: #475569; line-height: 1.4;">{sus['impact']}</td>
                    </tr>
        """)
    html_lines.append("""
                </tbody>
            </table>
        </div>
""")

    # Section 5: Form Leaderboard
    html_lines.append("""
        <!-- Section 5: Peak Form Leaderboard -->
        <div style="margin-bottom: 28px;">
            <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #0284c7; padding-bottom: 6px;">
                🔥 Peak Form Leaderboard (Top 15 Assets in FPL)
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <th style="padding: 8px 10px; text-align: center; font-weight: 700; color: #475569;">#</th>
                        <th style="padding: 8px 10px; font-weight: 700; color: #475569;">Player Name</th>
                        <th style="padding: 8px 10px; text-align: center; font-weight: 700; color: #475569;">Cost</th>
                        <th style="padding: 8px 10px; text-align: center; font-weight: 700; color: #475569;">Form</th>
                        <th style="padding: 8px 10px; text-align: center; font-weight: 700; color: #475569;">Threat</th>
                        <th style="padding: 8px 10px; text-align: center; font-weight: 700; color: #475569;">Creativity</th>
                        <th style="padding: 8px 10px; text-align: center; font-weight: 700; color: #475569;">Next Fixture</th>
                    </tr>
                </thead>
                <tbody>
""")
    for idx, fp in enumerate(data['form_players'], 1):
        html_lines.append(f"""
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 7px 10px; text-align: center; font-weight: 700; color: #64748b;">{fp['rank']}</td>
                        <td style="padding: 7px 10px; font-weight: 700; color: #0f172a;">{fp['name']} <span style="font-size:10.5px; color:#64748b;">({fp['club']} - {fp['pos']})</span></td>
                        <td style="padding: 7px 10px; text-align: center; color: #334155;">{fp['cost']}</td>
                        <td style="padding: 7px 10px; text-align: center; font-weight: 800; color: #0284c7;">{fp['form']:.1f}</td>
                        <td style="padding: 7px 10px; text-align: center; color: #475569;">{fp['threat']:.0f}</td>
                        <td style="padding: 7px 10px; text-align: center; color: #475569;">{fp['creat']:.1f}</td>
                        <td style="padding: 7px 10px; text-align: center; font-weight: 600; color: #334155;">{fp['opp']}</td>
                    </tr>
        """)
    html_lines.append("""
                </tbody>
            </table>
        </div>
""")

    # Section 6: Future Scout Watch
    html_lines.append("""
        <!-- Section 6: Future Scout Watch -->
        <div style="margin-bottom: 28px;">
            <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #059669; padding-bottom: 6px;">
                🔭 Future Scout Watch (Top Targets for Next 3–5 Gameweeks)
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Target Player</th>
                        <th style="padding: 9px 10px; text-align: center; font-weight: 700; color: #475569;">Price</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Upcoming Fixture Swing</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Analyst Future Outlook</th>
                    </tr>
                </thead>
                <tbody>
""")
    for fs in data['future_scouts']:
        html_lines.append(f"""
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 10px; font-weight: 700; color: #0f172a; white-space: nowrap;">{fs['name']} <span style="font-size:10.5px; color:#64748b;">({fs['club']} - {fs['pos']})</span></td>
                        <td style="padding: 8px 10px; text-align: center; font-weight: 600; color: #059669;">{fs['cost']}</td>
                        <td style="padding: 8px 10px; font-size: 11.5px; color: #334155; font-weight: 600;">{fs['run']}</td>
                        <td style="padding: 8px 10px; font-size: 11.5px; color: #475569; line-height: 1.4;">{fs['why']}</td>
                    </tr>
        """)
    html_lines.append("""
                </tbody>
            </table>
        </div>
""")

    # Section 7: H2H Fixtures
    html_lines.append(f"""
        <!-- Section 7: Mini-League Head-to-Head Schedule -->
        <div style="margin-bottom: 28px;">
            <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #475569; padding-bottom: 6px;">
                ⚔️ Upcoming Head-to-Head Fixture Schedule (GW{gw})
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; background: white; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                <thead>
                    <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                        <th style="padding: 9px 10px; text-align: center; font-weight: 700; color: #475569;">Match</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Manager 1 (Home)</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Team Name</th>
                        <th style="padding: 9px 10px; text-align: center; font-weight: 700; color: #94a3b8;">VS</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Team Name</th>
                        <th style="padding: 9px 10px; font-weight: 700; color: #475569;">Manager 2 (Away)</th>
                    </tr>
                </thead>
                <tbody>
""")
    for m in data['h2h_matches']:
        html_lines.append(f"""
                    <tr style="border-bottom: 1px solid #e2e8f0;">
                        <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: #64748b;">{m['match']}</td>
                        <td style="padding: 8px 10px; font-weight: 700; color: #0f172a;">{m['mgr1']}</td>
                        <td style="padding: 8px 10px; color: #475569;">{m['team1']}</td>
                        <td style="padding: 8px 10px; text-align: center; font-weight: 800; color: #94a3b8;">vs</td>
                        <td style="padding: 8px 10px; color: #475569;">{m['team2']}</td>
                        <td style="padding: 8px 10px; font-weight: 700; color: #0f172a;">{m['mgr2']}</td>
                    </tr>
        """)
    html_lines.append("""
                </tbody>
            </table>
        </div>

        <!-- Section 8: Interactive Newsletter Subscription Card -->
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 10px; padding: 22px; color: white; margin-bottom: 16px; border: 1px solid #334155;">
            <div style="font-size: 11px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px;">Direct League Dispatch</div>
            <h3 style="margin: 4px 0 8px 0; font-size: 16px; font-weight: 800;">📬 Subscribe to the FPL Intelligence Briefing</h3>
            <p style="margin: 0 0 16px 0; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                Receive this weekly tactical report directly to your inbox 3 hours before every gameweek deadline. Stored securely in our central database without spam.
            </p>
            <div style="background: rgba(255,255,255,0.06); padding: 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                    <div>
                        <label style="display: block; font-size: 11px; font-weight: 700; color: #cbd5e1; margin-bottom: 4px;">Email Address</label>
                        <input type="email" placeholder="manager@example.com" style="width: 100%; box-sizing: border-box; padding: 8px 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 12px;">
                    </div>
                    <div>
                        <label style="display: block; font-size: 11px; font-weight: 700; color: #cbd5e1; margin-bottom: 4px;">FPL Team ID</label>
                        <input type="text" placeholder="e.g. 19441" style="width: 100%; box-sizing: border-box; padding: 8px 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 12px;">
                    </div>
                </div>
                <button style="width: 100%; background: #2563eb; color: white; border: none; padding: 9px; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer;">
                    Confirm Subscription & Link Mini-Leagues
                </button>
                <div style="margin-top: 6px; font-size: 10px; color: #94a3b8; text-align: center;">
                    *Team ID is used to fetch manager name and auto-verify mini-league enrollment via official FPL API.
                </div>
            </div>
        </div>

    </div>

    <!-- Footer -->
    <div style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 20px 24px; text-align: center; font-size: 11.5px; color: #64748b;">
        <p style="margin: 0 0 6px 0;">Generated autonomously by <b>Alistair's AI Intelligence System</b> for FPL managers.</p>
        <p style="margin: 0;">🌐 Web Archive: <a href="https://ally-debug.github.io/toxic90-fpl-bot/" style="color: #2563eb; text-decoration: none;">https://ally-debug.github.io/toxic90-fpl-bot/</a></p>
    </div>

</div>
</body>
</html>
""")

    return "".join(html_lines)
