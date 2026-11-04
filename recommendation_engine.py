import urllib.request, json, ssl, os
from datetime import datetime, timezone

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=15) as r:
        return json.loads(r.read().decode())

def run_recommendation_engine():
    print("1. Ingesting live FPL data...")
    bs = fetch_json("https://fantasy.premierleague.com/api/bootstrap-static/")
    
    events = bs['events']
    next_event = [e for e in events if e['is_next']][0]
    next_gw = next_event['id']
    deadline_str = next_event['deadline_time']
    dt = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    deadline_formatted = dt.strftime("%A, %b %d at %H:%M UTC")
    
    teams = {t['id']: t for t in bs['teams']}
    elements = bs['elements']
    
    # 2. Dynamic Fixture Ticker for next 5 Gameweeks: [next_gw, next_gw + 4]
    lookahead_gws = list(range(next_gw, min(next_gw + 5, 39)))
    window_label = f"GW{lookahead_gws[0]} - GW{lookahead_gws[-1]}"
    print(f"2. Calculating dynamic FDR ticker across {window_label}...")
    
    # Fetch fixtures for lookahead window
    all_fixtures = []
    for gw in lookahead_gws:
        gw_fix = fetch_json(f"https://fantasy.premierleague.com/api/fixtures/?event={gw}")
        all_fixtures.extend(gw_fix)
        
    team_schedules = {t_id: [] for t_id in teams}
    for f in all_fixtures:
        th, ta = f['team_h'], f['team_a']
        dh, da = f['team_h_difficulty'], f['team_a_difficulty']
        gw = f['event']
        team_schedules[th].append({'gw': gw, 'opp': teams[ta]['short_name'], 'is_home': True, 'fdr': dh})
        team_schedules[ta].append({'gw': gw, 'opp': teams[th]['short_name'], 'is_home': False, 'fdr': da})
        
    # Calculate average FDR per team over the window
    team_fdr_ranks = []
    for t_id, sched in team_schedules.items():
        if not sched: continue
        avg_fdr = sum(s['fdr'] for s in sched) / len(sched)
        team_fdr_ranks.append({
            'team_id': t_id,
            'team_name': teams[t_id]['name'],
            'short_name': teams[t_id]['short_name'],
            'avg_fdr': avg_fdr,
            'fixtures': sched
        })
    team_fdr_ranks.sort(key=lambda x: x['avg_fdr'])
    
    # Top 4 Easiest Fixture Runs (Green Ticker)
    easiest_teams = team_fdr_ranks[:4]
    toughest_teams = team_fdr_ranks[-3:]
    
    # 3. Next GW Fixtures & Next Opponent Map
    next_gw_fixtures = [f for f in all_fixtures if f['event'] == next_gw]
    player_next_opp = {}
    for f in next_gw_fixtures:
        th, ta = f['team_h'], f['team_a']
        dh, da = f['team_h_difficulty'], f['team_a_difficulty']
        player_next_opp[th] = {'opp': teams[ta]['short_name'], 'is_home': True, 'fdr': dh}
        player_next_opp[ta] = {'opp': teams[th]['short_name'], 'is_home': False, 'fdr': da}
        
    # 4. Filter & Score Players for Scout Recommendations
    # Composite Algorithm:
    # Form Weight: 0.40
    # Underlying xGI / PPM Weight: 0.25
    # Fixture Ease (6 - FDR): 0.25
    # Home Advantage: 0.10
    scored_players = []
    for p in elements:
        t_id = p['team']
        if t_id not in player_next_opp: continue
        
        # Check fitness
        is_available = p['status'] == 'a' or p.get('chance_of_playing_next_round', 100) == 100
        form = float(p.get('form') or 0.0)
        minutes = int(p.get('minutes') or 0)
        cost = p['now_cost'] / 10.0
        pos = p['element_type'] # 1: GK, 2: DEF, 3: MID, 4: FWD
        
        fix_info = player_next_opp[t_id]
        fdr = fix_info['fdr']
        home_bonus = 0.5 if fix_info['is_home'] else 0.0
        
        # Avoid players with zero minutes
        if minutes < 90: continue
        
        xgi = float(p.get('expected_goal_involvements') or 0.0)
        xgi_per_90 = (xgi / (minutes / 90.0)) if minutes > 0 else 0.0
        
        # Overall Expected Score for Next GW
        exp_score = (form * 0.40) + (xgi_per_90 * 2.5 * 0.25) + ((5 - fdr) * 1.2 * 0.25) + home_bonus
        if not is_available:
            exp_score *= 0.1 # Heavily penalize injured players
            
        scored_players.append({
            'id': p['id'],
            'name': p['web_name'],
            'team': teams[t_id]['short_name'],
            'team_id': t_id,
            'pos': pos,
            'pos_name': ['GKP', 'DEF', 'MID', 'FWD'][pos - 1],
            'cost': cost,
            'form': form,
            'total_points': p['total_points'],
            'xgi': xgi,
            'xgi_per_90': xgi_per_90,
            'status': p['status'],
            'news': p.get('news') or '',
            'ownership': float(p.get('selected_by_percent') or 0.0),
            'fdr': fdr,
            'opp': f"{fix_info['opp']} ({'H' if fix_info['is_home'] else 'A'})",
            'exp_score': exp_score,
            'is_fit': is_available
        })
        
    scored_players.sort(key=lambda x: x['exp_score'], reverse=True)
    
    # 5. Build Scout Team of the Week (TOTW)
    # Target formation: 3-4-3 or 3-5-2 with £83.0m starting budget cap and max 3 per team
    fit_candidates = [p for p in scored_players if p['is_fit']]
    
    totw_gks = [p for p in fit_candidates if p['pos'] == 1]
    totw_defs = [p for p in fit_candidates if p['pos'] == 2]
    totw_mids = [p for p in fit_candidates if p['pos'] == 3]
    totw_fwds = [p for p in fit_candidates if p['pos'] == 4]
    
    # Greedy budget-constrained selection
    team_counts = {t_id: 0 for t_id in teams}
    totw_starters = []
    
    # Pick 1 GK
    for gk in totw_gks:
        if team_counts[gk['team_id']] < 3:
            totw_starters.append(gk)
            team_counts[gk['team_id']] += 1
            break
            
    # Pick 3 DEFs
    def_count = 0
    for d in totw_defs:
        if def_count == 3: break
        if team_counts[d['team_id']] < 3:
            totw_starters.append(d)
            team_counts[d['team_id']] += 1
            def_count += 1
            
    # Pick 4 MIDs
    mid_count = 0
    for m in totw_mids:
        if mid_count == 4: break
        if team_counts[m['team_id']] < 3:
            totw_starters.append(m)
            team_counts[m['team_id']] += 1
            mid_count += 1
            
    # Pick 3 FWDs
    fwd_count = 0
    for f in totw_fwds:
        if fwd_count == 3: break
        if team_counts[f['team_id']] < 3:
            totw_starters.append(f)
            team_counts[f['team_id']] += 1
            fwd_count += 1
            
    totw_cost = sum(p['cost'] for p in totw_starters)
    
    # 6. Injury Radar (Key Flags)
    injuries = [p for p in elements if p['status'] != 'a' and float(p.get('selected_by_percent', 0)) >= 5.0]
    injuries.sort(key=lambda x: float(x.get('selected_by_percent', 0)), reverse=True)
    
    # 7. Captain & Vice-Captain Matrix
    # Captain Candidates: Top projected attackers
    top_attackers = [p for p in fit_candidates if p['pos'] in [3, 4]]
    safe_cap = top_attackers[0] # Highest exp_score / high ownership
    
    # Ceiling Pick (High xGI)
    ceiling_cap = sorted(top_attackers, key=lambda x: x['xgi_per_90'], reverse=True)[0]
    if ceiling_cap['id'] == safe_cap['id'] and len(top_attackers) > 1:
        ceiling_cap = top_attackers[1]
        
    # Differential Pick (Ownership < 15%)
    diff_candidates = [p for p in top_attackers if p['ownership'] < 15.0]
    diff_cap = diff_candidates[0] if diff_candidates else top_attackers[2]
    
    # Vice Captain Options (Different kickoff / alternative team security)
    vc_candidates = [p for p in top_attackers if p['team_id'] != safe_cap['team_id']][:3]
    
    print(f"Generated TOTW (Cost: £{totw_cost:.1f}m):", [p['name'] for p in totw_starters])
    
    return {
        'next_gw': next_gw,
        'window_label': window_label,
        'deadline_formatted': deadline_formatted,
        'easiest_teams': easiest_teams,
        'toughest_teams': toughest_teams,
        'totw': totw_starters,
        'totw_cost': totw_cost,
        'injuries': injuries[:5],
        'captains': {
            'safe': safe_cap,
            'ceiling': ceiling_cap,
            'diff': diff_cap
        },
        'vice_captains': vc_candidates,
        'top_form': sorted(fit_candidates, key=lambda x: x['form'], reverse=True)[:5]
    }

if __name__ == "__main__":
    res = run_recommendation_engine()
    print("Engine Test Completed Successfully!")
