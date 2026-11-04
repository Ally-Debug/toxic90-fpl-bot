from recommendation_engine import run_recommendation_engine

def render_newsletter_html(data):
    gw = data['next_gw']
    window = data['window_label']
    deadline = data['deadline_formatted']
    
    # 1. Easiest FDR Table Rows
    fdr_rows = []
    for t in data['easiest_teams']:
        runs = []
        for fix in t['fixtures']:
            color = "#16a34a" if fix['fdr'] <= 2 else ("#ca8a04" if fix['fdr'] == 3 else "#dc2626")
            loc = "H" if fix['is_home'] else "A"
            runs.append(f"<span style='background:{color}; color:white; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:600;'>{fix['opp']}({loc})</span>")
        fdr_rows.append(f"""
        <tr>
            <td style='padding:8px 12px; font-weight:600; border-bottom:1px solid #e5e7eb;'>{t['team_name']}</td>
            <td style='padding:8px 12px; text-align:center; font-weight:700; color:#16a34a; border-bottom:1px solid #e5e7eb;'>{t['avg_fdr']:.2f}</td>
            <td style='padding:8px 12px; border-bottom:1px solid #e5e7eb;'>{' '.join(runs)}</td>
        </tr>
        """)
        
    # 2. Top Form Players Rows
    form_rows = []
    for p in data['top_form']:
        form_rows.append(f"""
        <tr>
            <td style='padding:8px 12px; font-weight:600; border-bottom:1px solid #e5e7eb;'>{p['name']} <span style='font-size:11px; color:#6b7280;'>({p['team']} - {p['pos_name']})</span></td>
            <td style='padding:8px 12px; text-align:center; font-weight:700; color:#2563eb; border-bottom:1px solid #e5e7eb;'>{p['form']}</td>
            <td style='padding:8px 12px; text-align:center; border-bottom:1px solid #e5e7eb;'>£{p['cost']:.1f}m</td>
            <td style='padding:8px 12px; text-align:center; border-bottom:1px solid #e5e7eb;'>{p['xgi']:.2f}</td>
            <td style='padding:8px 12px; text-align:center; font-weight:600; border-bottom:1px solid #e5e7eb;'>{p['opp']}</td>
        </tr>
        """)

    # 3. Injury Rows
    injury_rows = []
    for p in data['injuries']:
        chance = f"{p.get('chance_of_playing_next_round')}%" if p.get('chance_of_playing_next_round') is not None else "Ruled Out"
        color = "#dc2626" if chance == "0%" or chance == "Ruled Out" else "#d97706"
        injury_rows.append(f"""
        <tr>
            <td style='padding:8px 12px; font-weight:600; border-bottom:1px solid #e5e7eb;'>{p['web_name']}</td>
            <td style='padding:8px 12px; text-align:center; border-bottom:1px solid #e5e7eb;'><span style='background:{color}; color:white; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;'>{chance}</span></td>
            <td style='padding:8px 12px; font-size:12px; color:#4b5563; border-bottom:1px solid #e5e7eb;'>{p.get('news') or 'Awaiting assessment'}</td>
        </tr>
        """)

    # 4. TOTW Rows
    totw_rows = []
    for p in data['totw']:
        totw_rows.append(f"""
        <tr>
            <td style='padding:7px 12px; font-size:12px; font-weight:700; color:#374151; border-bottom:1px solid #e5e7eb;'>{p['pos_name']}</td>
            <td style='padding:7px 12px; font-weight:600; border-bottom:1px solid #e5e7eb;'>{p['name']} <span style='font-size:11px; color:#6b7280;'>({p['team']})</span></td>
            <td style='padding:7px 12px; text-align:center; border-bottom:1px solid #e5e7eb;'>{p['opp']}</td>
            <td style='padding:7px 12px; text-align:center; border-bottom:1px solid #e5e7eb;'>£{p['cost']:.1f}m</td>
            <td style='padding:7px 12px; text-align:center; font-weight:700; color:#16a34a; border-bottom:1px solid #e5e7eb;'>{p['exp_score']:.1f}</td>
        </tr>
        """)

    # Captains
    caps = data['captains']
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toxic 90 Intelligence Briefing - Game Week {gw}</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 24px 10px; color: #1e293b;">
    <div style="max-width: 660px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07); border: 1px solid #e2e8f0;">
        
        <!-- Header Banner -->
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 28px 24px; color: #ffffff;">
            <div style="background: rgba(255,255,255,0.15); display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 10px;">PRE-DEADLINE INTELLIGENCE</div>
            <h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px;">TOXIC 90 ☢️ // GAME WEEK {gw} SCOUT BRIEFING</h1>
            <p style="margin: 6px 0 0 0; color: #cbd5e1; font-size: 13px;">Automated Recommendation Engine & Fixture Intelligence</p>
        </div>

        <!-- Deadline Alert Bar -->
        <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 14px 20px; display: flex; align-items: center;">
            <span style="font-size: 20px; margin-right: 12px;">⏰</span>
            <div>
                <div style="font-weight: 800; color: #991b1b; font-size: 14px;">FINAL 3-HOUR DEADLINE WARNING</div>
                <div style="color: #7f1d1d; font-size: 12.5px; margin-top: 2px;">Lock Time: <b>{deadline}</b>. Transfers & chips freeze strictly at deadline.</div>
            </div>
        </div>

        <div style="padding: 24px;">

            <!-- Section 1: Captaincy Matrix -->
            <div style="margin-bottom: 28px;">
                <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 12px; border-bottom: 2px solid #3b82f6; padding-bottom: 6px;">
                    👑 Captain & Vice-Captain Decision Matrix
                </h3>
                <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
                        <span style="background: #2563eb; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;">SAFE SHIELD</span>
                        <b style="margin-left: 6px; font-size: 14px; color: #0f172a;">{caps['safe']['name']}</b> ({caps['safe']['team']} - £{caps['safe']['cost']:.1f}m) vs {caps['safe']['opp']}
                        <div style="font-size: 12px; color: #475569; margin-top: 4px;">Top algorithm pick with {caps['safe']['ownership']:.1f}% ownership. High floor to guard your mini-league rank.</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
                        <span style="background: #16a34a; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;">EXPLOSIVE CEILING</span>
                        <b style="margin-left: 6px; font-size: 14px; color: #0f172a;">{caps['ceiling']['name']}</b> ({caps['ceiling']['team']} - £{caps['ceiling']['cost']:.1f}m) vs {caps['ceiling']['opp']}
                        <div style="font-size: 12px; color: #475569; margin-top: 4px;">Dominant underlying threat (xGI/90: {caps['ceiling']['xgi_per_90']:.2f}). Peak hat-trick potential.</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px;">
                        <span style="background: #d97706; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;">BOLD DIFFERENTIAL</span>
                        <b style="margin-left: 6px; font-size: 14px; color: #0f172a;">{caps['diff']['name']}</b> ({caps['diff']['team']} - £{caps['diff']['cost']:.1f}m) vs {caps['diff']['opp']}
                        <div style="font-size: 12px; color: #475569; margin-top: 4px;">Sub-15% ownership differential ({caps['diff']['ownership']:.1f}%). The ultimate rank-climber for chasers.</div>
                    </div>
                </div>
            </div>

            <!-- Section 2: Dynamic FDR Fixture Ticker -->
            <div style="margin-bottom: 28px;">
                <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 8px; border-bottom: 2px solid #10b981; padding-bottom: 6px;">
                    🗓️ Dynamic Fixture Ticker: Top 4 Green Runs ({window})
                </h3>
                <p style="font-size: 12px; color: #64748b; margin-top: 0; margin-bottom: 10px;">Calculated live across all 20 Premier League clubs over the next 5 gameweeks:</p>
                <table style="width: 100%; border-collapse: collapse; font-size: 12.5px; text-align: left;">
                    <thead>
                        <tr style="background: #f8fafc; color: #475569;">
                            <th style="padding: 8px 12px; border-bottom: 2px solid #e2e8f0;">Club</th>
                            <th style="padding: 8px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">Avg FDR</th>
                            <th style="padding: 8px 12px; border-bottom: 2px solid #e2e8f0;">Upcoming Match Run</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(fdr_rows)}
                    </tbody>
                </table>
            </div>

            <!-- Section 3: Scout Team of the Week (TOTW) -->
            <div style="margin-bottom: 28px;">
                <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 8px; border-bottom: 2px solid #8b5cf6; padding-bottom: 6px;">
                    🏆 Scout "Team of the Week" (Optimal XI for GW{gw})
                </h3>
                <p style="font-size: 12px; color: #64748b; margin-top: 0; margin-bottom: 10px;">Solved via linear optimization (Form + xGI + FDR), respecting £100m budget and max 3 players per club:</p>
                <table style="width: 100%; border-collapse: collapse; font-size: 12.5px;">
                    <thead>
                        <tr style="background: #f8fafc; color: #475569;">
                            <th style="padding: 7px 12px; border-bottom: 2px solid #e2e8f0;">Pos</th>
                            <th style="padding: 7px 12px; border-bottom: 2px solid #e2e8f0;">Player</th>
                            <th style="padding: 7px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">Fixture</th>
                            <th style="padding: 7px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">Cost</th>
                            <th style="padding: 7px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">xP</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(totw_rows)}
                    </tbody>
                </table>
                <div style="text-align: right; font-size: 11.5px; color: #64748b; margin-top: 6px;">Total Starting Cost: <b>£{data['totw_cost']:.1f}m</b> / £83.0m budget</div>
            </div>

            <!-- Section 4: Injury & Suspension Radar -->
            <div style="margin-bottom: 28px;">
                <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 8px; border-bottom: 2px solid #ef4444; padding-bottom: 6px;">
                    🚑 Injury & Suspension Radar (Critical Flags)
                </h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 12.5px;">
                    <thead>
                        <tr style="background: #f8fafc; color: #475569;">
                            <th style="padding: 8px 12px; border-bottom: 2px solid #e2e8f0;">Player</th>
                            <th style="padding: 8px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">Chance</th>
                            <th style="padding: 8px 12px; border-bottom: 2px solid #e2e8f0;">Official Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(injury_rows)}
                    </tbody>
                </table>
            </div>

            <!-- Section 5: Peak Form Guide -->
            <div style="margin-bottom: 20px;">
                <h3 style="font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; color: #0f172a; margin-top: 0; margin-bottom: 8px; border-bottom: 2px solid #0284c7; padding-bottom: 6px;">
                    📈 Form Leaderboard (Highest Rolling 30-Day PPG)
                </h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 12.5px;">
                    <thead>
                        <tr style="background: #f8fafc; color: #475569;">
                            <th style="padding: 8px 12px; border-bottom: 2px solid #e2e8f0;">Player</th>
                            <th style="padding: 8px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">Form</th>
                            <th style="padding: 8px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">Cost</th>
                            <th style="padding: 8px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">xGI</th>
                            <th style="padding: 8px 12px; text-align: center; border-bottom: 2px solid #e2e8f0;">GW{gw} Fixture</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(form_rows)}
                    </tbody>
                </table>
            </div>

        </div>

        <!-- Footer -->
        <div style="background: #f8fafc; padding: 18px 24px; border-top: 1px solid #e2e8f0; font-size: 11.5px; color: #64748b; text-align: center; line-height: 1.5;">
            Sent automatically by the <b>Toxic 90 Autonomous Intelligence Engine</b> 3 hours prior to deadline.<br>
            Data sourced live from official Fantasy Premier League endpoints.
        </div>
    </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    from recommendation_engine import run_recommendation_engine
    data = run_recommendation_engine()
    html_out = render_newsletter_html(data)
    with open("/Users/Alistair_dsouza/.gemini/antigravity/scratch/fpl-diagnostics/sample_newsletter.html", "w") as f:
        f.write(html_out)
    print("Sample Newsletter HTML generated successfully at: sample_newsletter.html")
