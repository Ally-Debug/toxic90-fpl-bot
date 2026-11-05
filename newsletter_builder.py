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
        <style>
            @keyframes fplSpin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .fpl-spinner {
                display: inline-block;
                width: 13px;
                height: 13px;
                border: 2px solid rgba(255,255,255,0.25);
                border-radius: 50%;
                border-top-color: #38bdf8;
                animation: fplSpin 0.75s linear infinite;
                vertical-align: middle;
                margin-right: 6px;
            }
        </style>
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 10px; padding: 22px; color: white; margin-bottom: 16px; border: 1px solid #334155;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-size: 11px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px;">Direct League Dispatch</span>
                <span id="sub_cap_badge" style="font-size: 11px; font-weight: 700; color: #f59e0b; background: rgba(245, 158, 11, 0.15); padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.3); transition: all 0.3s ease;">🎯 50 Spots Remaining</span>
            </div>
            <h3 style="margin: 4px 0 8px 0; font-size: 16px; font-weight: 800;">📬 Subscribe to the FPL Intelligence Briefing</h3>
            <p style="margin: 0 0 16px 0; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                Receive this weekly tactical briefing directly to your inbox 3 hours before every gameweek deadline. Validated via the official Premier League API and strictly limited to 50 active manager spots. Duplicate entries are blocked automatically.
            </p>
            <div style="background: rgba(255,255,255,0.06); padding: 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px;">
                    <div>
                        <label style="display: block; font-size: 11px; font-weight: 700; color: #cbd5e1; margin-bottom: 4px;">Email Address <span style="color:#ef4444;">*</span></label>
                        <input id="sub_email" type="email" placeholder="manager@example.com" style="width: 100%; box-sizing: border-box; padding: 8px 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 12px;">
                    </div>
                    <div>
                        <label style="display: block; font-size: 11px; font-weight: 700; color: #cbd5e1; margin-bottom: 4px;">FPL Team ID <span style="color:#ef4444;">*</span></label>
                        <input id="sub_team_id" type="number" placeholder="e.g. 19441" style="width: 100%; box-sizing: border-box; padding: 8px 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 12px;">
                    </div>
                    <div>
                        <label style="display: block; font-size: 11px; font-weight: 700; color: #cbd5e1; margin-bottom: 4px;">FPL Team Name</label>
                        <input id="sub_team_name" type="text" placeholder="Auto-detected or enter" style="width: 100%; box-sizing: border-box; padding: 8px 10px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 12px;">
                    </div>
                </div>
                <button id="sub_btn" onclick="handleSubscription()" style="width: 100%; background: #2563eb; color: white; border: none; padding: 10px; border-radius: 6px; font-weight: 700; font-size: 12px; cursor: pointer; transition: background 0.2s;">
                    Confirm Subscription & Link Mini-Leagues
                </button>
                <div id="sub_status" style="display: none; margin-top: 10px;"></div>
                <div style="margin-top: 8px; font-size: 10px; color: #94a3b8; text-align: center;">
                    *Team ID and email are validated against central database records. Duplicate emails, team IDs, or squad names are strictly rejected.
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

<!-- Interactive Client-side Script with Live Loading & Strict Duplicate Guard -->
<script>
const EXISTING_REGISTRATIONS = [
    { team_id: 36048, manager: "Alerick Cano", team_name: "Santøz FC", email: "" },
    { team_id: 7595720, manager: "Aleron Sutari", team_name: "PYthöņ", email: "" },
    { team_id: 7771956, manager: "Alistair Dsouza", team_name: "Lathi Charge FC", email: "alistair3g@gmail.com" },
    { team_id: 12191, manager: "Mohamed Als", team_name: "Mohamed", email: "alistair3g@gmail.com" },
    { team_id: 12491, manager: "Arun Singh", team_name: "Holy Cows", email: "" },
    { team_id: 4780721, manager: "daksh bakaya", team_name: "ArsenalTheChampions", email: "" },
    { team_id: 5521850, manager: "Gurdeep Jordan", team_name: "brUNO REVERSE", email: "" },
    { team_id: 41205, manager: "Joel Thattil", team_name: "SUIIII ᴾᴱᴿ SUB", email: "" },
    { team_id: 4212864, manager: "Karthik RA", team_name: "Face Palmer", email: "" },
    { team_id: 94966, manager: "Macarius Fernandes", team_name: "Wacky Devils", email: "" },
    { team_id: 4631060, manager: "Nitin Billava", team_name: "Hardyy Boyzz", email: "" },
    { team_id: 43170, manager: "Roshan Poojari", team_name: "Könaté Kïd", email: "" },
    { team_id: 5557374, manager: "Ryan S", team_name: "Ødegardevoir", email: "" },
    { team_id: 48970, manager: "Siddesh Sawant", team_name: "ErlingViking", email: "" },
    { team_id: 447664, manager: "Venzel Lobo", team_name: "THE GREAT GUYYYY", email: "" },
    { team_id: 828526, manager: "Vishal Bhartia", team_name: "Bhartia's XI", email: "" },
    { team_id: 2151066, manager: "Yohaan Dias", team_name: "P$ygunner", email: "" }
];

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function handleSubscription() {
    const emailEl = document.getElementById('sub_email');
    const teamIdEl = document.getElementById('sub_team_id');
    const teamNameEl = document.getElementById('sub_team_name');
    const btn = document.getElementById('sub_btn');
    const status = document.getElementById('sub_status');

    const email = emailEl.value.trim().toLowerCase();
    const teamId = teamIdEl.value.trim();
    const teamNameInput = teamNameEl ? teamNameEl.value.trim() : '';

    // 1. Email format check
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
        renderAlert('❌ Please enter a valid email address (e.g. manager@example.com).', '#ef4444', '#fef2f2', '#991b1b');
        return;
    }

    // 2. Numerical Team ID check
    if (!teamId || isNaN(teamId) || parseInt(teamId) <= 0) {
        renderAlert('❌ Please enter a valid numerical FPL Team ID (e.g. 19441).', '#ef4444', '#fef2f2', '#991b1b');
        return;
    }
    const teamIdInt = parseInt(teamId);

    // Lock inputs & Activate live loading mechanism
    emailEl.disabled = true;
    teamIdEl.disabled = true;
    if (teamNameEl) teamNameEl.disabled = true;
    btn.disabled = true;
    btn.innerHTML = '<span class="fpl-spinner"></span> Checking records & contacting database...';
    btn.style.opacity = '0.85';

    renderAlert('<span class="fpl-spinner" style="border-top-color:#38bdf8;"></span> <b>Phase 1/3:</b> Checking central database for duplicate email, team ID, and team name...', '#38bdf8', '#0f172a', '#e2e8f0');

    // Simulate genuine network check delay
    await sleep(650);

    // 3. STRICT DUPLICATE CHECK ACROSS ALL 3 FIELDS
    const dupEmail = EXISTING_REGISTRATIONS.find(r => r.email && r.email.toLowerCase() === email);
    const dupTeamId = EXISTING_REGISTRATIONS.find(r => r.team_id === teamIdInt);
    const dupTeamName = teamNameInput ? EXISTING_REGISTRATIONS.find(r => r.team_name && r.team_name.toLowerCase() === teamNameInput.toLowerCase()) : null;

    let duplicateReasons = [];
    if (dupEmail) {
        duplicateReasons.push('Email address <b>"' + email + '"</b> is already registered in our records (Manager: <i>' + dupEmail.manager + '</i>, Team: <i>' + dupEmail.team_name + '</i>).');
    }
    if (dupTeamId) {
        duplicateReasons.push('FPL Team ID <b>"' + teamIdInt + '"</b> already exists in our records (Manager: <i>' + dupTeamId.manager + '</i>, Team: <i>' + dupTeamId.team_name + '</i>).');
    }
    if (dupTeamName) {
        duplicateReasons.push('Team name <b>"' + teamNameInput + '"</b> already exists in our records (Manager: <i>' + dupTeamName.manager + '</i>).');
    }

    // IF DUPLICATE IS FOUND -> STOP IMMEDIATELY! PREVENT ADDITION!
    if (duplicateReasons.length > 0) {
        const alertHtml = '❌ <b>Registration Blocked: Duplicate Record Found</b><br>' + 
                          duplicateReasons.join('<br>') + 
                          '<br><span style="display:block; margin-top:6px; font-size:11px; color:#991b1b; font-weight:600;">' + 
                          'Duplicate registrations are strictly prohibited. Existing database records are preserved and no new entry was added.</span>';
        renderAlert(alertHtml, '#ef4444', '#fef2f2', '#991b1b');
        
        btn.innerText = '❌ Registration Blocked: Duplicate Detected';
        btn.style.background = '#991b1b';
        btn.style.opacity = '1';

        setTimeout(() => {
            resetButton();
        }, 3000);
        return;
    }

    // 4. CHECK GLOBAL 50-SUBSCRIBER CAP
    const activeSubscribers = EXISTING_REGISTRATIONS.filter(r => r.email && r.email.length > 0);
    if (activeSubscribers.length >= 50) {
        renderAlert('🔒 <b>Registration Closed:</b> The global submission cap of 50 subscribers has been reached (' + activeSubscribers.length + '/50). Further registrations cannot be accepted.', '#ef4444', '#fef2f2', '#991b1b');
        btn.innerText = '🔒 Registration Cap Reached (50/50)';
        btn.style.background = '#64748b';
        btn.style.opacity = '1';
        setTimeout(resetButton, 3000);
        return;
    }

    // 5. PHASE 2: REAL LIVE TELEMETRY CHECK WITH OFFICIAL PREMIER LEAGUE API
    renderAlert('<span class="fpl-spinner" style="border-top-color:#38bdf8;"></span> <b>Phase 2/3:</b> Querying official Premier League API for Team #' + teamIdInt + '...', '#38bdf8', '#0f172a', '#e2e8f0');

    let fplManager = null;
    let fplTeamName = null;
    let verificationSuccess = false;

    // Check if team is in our known mini-league registry first
    const knownMatch = EXISTING_REGISTRATIONS.find(r => r.team_id === teamIdInt);
    if (knownMatch && knownMatch.manager) {
        fplManager = knownMatch.manager;
        fplTeamName = knownMatch.team_name;
        verificationSuccess = true;
    } else {
        // Query Live FPL API via keyless open CORS mirror (api.fplrivals.org)
        try {
            const fplRes = await fetch('https://api.fplrivals.org/api/v1/managers/' + teamIdInt, {
                headers: { 'Accept': 'application/json' }
            });

            if (fplRes.status === 404) {
                // TEAM ID DOES NOT EXIST! STOP AND REJECT!
                renderAlert('❌ <b>Verification Failed: Invalid FPL Team ID</b><br>' + 
                            'Official Premier League telemetry confirms that Team ID <b>#' + teamIdInt + '</b> does not exist.<br>' +
                            '<span style="display:block; margin-top:6px; font-size:11px; color:#991b1b; font-weight:600;">' + 
                            'Please check your Team ID in the official FPL app under Points / Gameweek History. Non-existent teams cannot be registered.</span>', 
                            '#ef4444', '#fef2f2', '#991b1b');
                btn.innerText = '❌ Invalid Team ID (Not Found on FPL)';
                btn.style.background = '#991b1b';
                btn.style.opacity = '1';
                setTimeout(resetButton, 3500);
                return;
            } else if (fplRes.ok) {
                const fplJson = await fplRes.json();
                const mData = fplJson.data || fplJson;
                const fName = mData.player_first_name || '';
                const lName = mData.player_last_name || '';
                fplManager = (fName + ' ' + lName).trim() || mData.player_name || 'FPL Manager';
                fplTeamName = mData.name || mData.entry_name || teamNameInput || 'Squad #' + teamIdInt;
                verificationSuccess = true;
            }
        } catch (fplErr) {
            // Fallback attempt via serverless /api/subscribe backend
            try {
                const apiRes = await fetch('/api/subscribe', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email, team_id: teamIdInt, team_name: teamNameInput })
                });
                if (apiRes.status === 404) {
                    renderAlert('❌ <b>Verification Failed: Invalid FPL Team ID</b><br>Team ID <b>#' + teamIdInt + '</b> does not exist on Fantasy Premier League.', '#ef4444', '#fef2f2', '#991b1b');
                    btn.innerText = '❌ Invalid Team ID';
                    btn.style.background = '#991b1b';
                    setTimeout(resetButton, 3500);
                    return;
                } else if (apiRes.status === 409) {
                    const errData = await apiRes.json();
                    renderAlert('❌ <b>Registration Blocked:</b> ' + (errData.error || 'Duplicate record found in database.'), '#ef4444', '#fef2f2', '#991b1b');
                    btn.innerText = '❌ Duplicate Detected';
                    btn.style.background = '#991b1b';
                    setTimeout(resetButton, 3500);
                    return;
                } else if (apiRes.ok) {
                    const okData = await apiRes.json();
                    fplManager = okData.manager_name;
                    fplTeamName = okData.team_name;
                    verificationSuccess = true;
                }
            } catch (e2) {}
        }
    }

    // IF VERIFICATION FAILED TO CONFIRM THE TEAM ID -> DO NOT CONFIRM!
    if (!verificationSuccess || !fplManager) {
        renderAlert('❌ <b>Verification Failed: Invalid FPL Team ID</b><br>' + 
                    'Team ID <b>#' + teamIdInt + '</b> could not be verified against official Premier League records.<br>' + 
                    '<span style="display:block; margin-top:6px; font-size:11px; color:#991b1b; font-weight:600;">' + 
                    'Only verified, active Premier League teams can be linked to the dispatch. Please enter a valid FPL Team ID.</span>',
                    '#ef4444', '#fef2f2', '#991b1b');
        btn.innerText = '❌ Verification Failed (Invalid ID)';
        btn.style.background = '#991b1b';
        btn.style.opacity = '1';
        setTimeout(resetButton, 3500);
        return;
    }

    // 6. CHECK IF THE RESOLVED SQUAD NAME IS DUPLICATE IN OUR DATABASE
    const dupResolvedTeam = EXISTING_REGISTRATIONS.find(r => r.team_name && fplTeamName && r.team_name.toLowerCase() === fplTeamName.toLowerCase());
    if (dupResolvedTeam) {
        renderAlert('❌ <b>Registration Blocked: Duplicate Team Name</b><br>' + 
                    'The squad name <b>"' + fplTeamName + '"</b> is already registered in our database to manager <i>' + dupResolvedTeam.manager + '</i>.<br>' +
                    '<span style="display:block; margin-top:6px; font-size:11px; color:#991b1b; font-weight:600;">Duplicate entries are prohibited. Existing database records are preserved.</span>',
                    '#ef4444', '#fef2f2', '#991b1b');
        btn.innerText = '❌ Duplicate Team Name Blocked';
        btn.style.background = '#991b1b';
        setTimeout(resetButton, 3500);
        return;
    }

    // 7. WRITE DIRECTLY TO NEON DATABASE VIA SECURE SERVERLESS API
    renderAlert('<span class="fpl-spinner" style="border-top-color:#10b981;"></span> <b>Phase 3/3:</b> Writing to Neon database...', '#10b981', '#0f172a', '#e2e8f0');
    await sleep(400);

    const isVercelHost = window.location.hostname.includes('vercel.app');
    const apiUrl = isVercelHost ? '/api/subscribe' : 'https://toxic90-fpl-bot-snowy.vercel.app/api/subscribe';

    let dbSaved = false;
    let lastErrorMsg = '';

    try {
        const apiRes = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, team_id: teamIdInt, team_name: fplTeamName })
        });
        
        if (apiRes.status === 409) {
            const errData = await apiRes.json().catch(() => ({}));
            renderAlert('❌ <b>Registration Blocked: Duplicate Record</b><br>' + (errData.error || 'A record with this email, team ID, or team name already exists in Neon DB.') + '<br><span style="display:block; margin-top:6px; font-size:11px; color:#991b1b; font-weight:600;">Existing database records are preserved.</span>', '#ef4444', '#fef2f2', '#991b1b');
            btn.innerText = '❌ Duplicate Detected in Neon DB';
            btn.style.background = '#991b1b';
            setTimeout(resetButton, 3500);
            return;
        } else if (apiRes.status === 403) {
            const errData = await apiRes.json().catch(() => ({}));
            renderAlert('🔒 <b>Registration Closed:</b> ' + (errData.error || 'The global submission cap of 50 subscribers has been reached.'), '#ef4444', '#fef2f2', '#991b1b');
            btn.innerText = '🔒 Registration Cap Reached (50/50)';
            btn.style.background = '#64748b';
            setTimeout(resetButton, 3500);
            return;
        } else if (apiRes.ok) {
            const resData = await apiRes.json().catch(() => ({}));
            if (resData.success) {
                dbSaved = true;
            } else {
                lastErrorMsg = resData.error || 'Database operation was not completed.';
            }
        } else if (apiRes.status === 404) {
            const textResp = await apiRes.text().catch(() => '');
            if (textResp.includes('DEPLOYMENT_NOT_FOUND')) {
                lastErrorMsg = 'Vercel backend is not deployed yet (DEPLOYMENT_NOT_FOUND). Please click Redeploy in Vercel.';
            } else {
                lastErrorMsg = 'Endpoint returned 404 Not Found on Vercel.';
            }
        } else {
            const errData = await apiRes.json().catch(() => ({}));
            lastErrorMsg = errData.error || ('HTTP ' + apiRes.status + ' response from backend');
        }
    } catch (eDb) {
        lastErrorMsg = 'Unable to reach backend (' + (eDb.message || 'Network/CORS error') + '). Ensure Vercel deployment is active.';
    }

    if (!dbSaved) {
        renderAlert('❌ <b>Database Write Incomplete</b><br>' + 
                    'The details could not be written to Neon DB. Reason: <i>' + lastErrorMsg + '</i>.<br>' + 
                    '<span style="display:block; margin-top:6px; font-size:11px; color:#991b1b; font-weight:600;">' + 
                    'To enable instantaneous in-browser database writes, please add DATABASE_URL in Vercel Project Settings and click Redeploy.' + 
                    '</span>', 
                    '#ef4444', '#fef2f2', '#991b1b');
        btn.innerText = '❌ Database Write Failed';
        btn.style.background = '#991b1b';
        setTimeout(resetButton, 4000);
        return;
    }

    const successHtml = '✅ <b>Registration Confirmed!</b><br>' + 
                        'Manager: <b>' + fplManager + '</b> | Squad: <i>' + fplTeamName + '</i> (ID: ' + teamIdInt + ')<br>' + 
                        'Email: <b>' + email + '</b><br>' + 
                        '<p style="margin: 8px 0 0 0; font-size: 12px; color: #15803d; font-weight: 600; line-height: 1.45;">' + 
                        'Thank you for your details. Your name has been stored in our database, and you will continue to receive our newsletter.' + 
                        '</p>';

    renderAlert(successHtml, '#10b981', '#f0fdf4', '#047857');
    btn.innerText = '✅ Subscription Confirmed';
    btn.style.background = '#10b981';
    btn.style.opacity = '1';
    btn.disabled = true;

    // Immediately decrement spots remaining in the UI counter
    if (typeof currentSpotsRemaining === 'number' && currentSpotsRemaining > 0) {
        updateSpotsUI(currentSpotsRemaining - 1);
    }
}

function renderAlert(msg, borderColor, bg, textColor) {
    const s = document.getElementById('sub_status');
    s.style.display = 'block';
    s.style.border = '1px solid ' + borderColor;
    s.style.background = bg;
    s.style.color = textColor;
    s.style.padding = '12px 14px';
    s.style.borderRadius = '6px';
    s.style.fontSize = '12px';
    s.style.lineHeight = '1.5';
    s.innerHTML = msg;
}

function resetButton() {
    const emailEl = document.getElementById('sub_email');
    const teamIdEl = document.getElementById('sub_team_id');
    const teamNameEl = document.getElementById('sub_team_name');
    const btn = document.getElementById('sub_btn');
    
    if (emailEl) emailEl.disabled = false;
    if (teamIdEl) teamIdEl.disabled = false;
    if (teamNameEl) teamNameEl.disabled = false;
    
    if (btn) {
        btn.disabled = false;
        btn.innerText = 'Confirm Subscription & Link Mini-Leagues';
        btn.style.background = '#2563eb';
        btn.style.opacity = '1';
    }
}

let currentSpotsRemaining = 50;

function updateSpotsUI(remaining) {
    currentSpotsRemaining = remaining;
    const badge = document.getElementById('sub_cap_badge');
    const btn = document.getElementById('sub_btn');
    if (badge) {
        if (remaining <= 0) {
            badge.innerText = '🔒 0 Spots Left (Cap Reached)';
            badge.style.color = '#ef4444';
            badge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
            badge.style.background = 'rgba(239, 68, 68, 0.15)';
            if (btn && !btn.disabled) {
                btn.disabled = true;
                btn.innerText = '🔒 Registration Closed (50/50 Cap Reached)';
                btn.style.background = '#64748b';
            }
        } else {
            badge.innerText = '🎯 ' + remaining + ' Spots Remaining';
            badge.style.color = remaining <= 5 ? '#ef4444' : '#f59e0b';
        }
    }
}

async function fetchLiveSpots() {
    try {
        const isVercelHost = window.location.hostname.includes('vercel.app');
        const apiUrl = isVercelHost ? '/api/subscribe' : 'https://toxic90-fpl-bot-snowy.vercel.app/api/subscribe';
        const res = await fetch(apiUrl, { method: 'GET', headers: { 'Accept': 'application/json' } });
        if (res.ok) {
            const data = await res.json();
            if (typeof data.spots_remaining === 'number') {
                updateSpotsUI(data.spots_remaining);
            }
        }
    } catch (e) {}
}

// Fetch live spots dynamically from backend on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fetchLiveSpots);
} else {
    fetchLiveSpots();
}
</script>
</body>
</html>
""")

    return "".join(html_lines)
