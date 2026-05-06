import sys
from pathlib import Path

# ---------------------------------------------------------
# 1. BOOTSTRAP: Add ../src to the path to import config
# This assumes main.py is in a directory like $root/notebooks/
# ---------------------------------------------------------
src_path = str(Path.cwd().parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import config  # This automatically sets the working directory to the project root

# ---------------------------------------------------------
# 2. STANDARD IMPORTS
# ---------------------------------------------------------
import requests
import csv
import os
import time

# Reconfigure standard output to handle special characters without crashing
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def safe_get(data, *keys, default="Unknown"):
    """
    Safely navigates nested dictionaries. 
    Example: safe_get(match_info, 'Court', 'Name', default='TBD')
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return default
    return data if data is not None else default

def find_teams(data, unique_teams_dict):
    """Recursively extracts Team IDs and Names from JSON objects."""
    if isinstance(data, dict):
        t_id = data.get('TeamId')
        t_name = data.get('TeamName')
        if t_id and t_name:
            unique_teams_dict[t_id] = t_name
        for key, value in data.items():
            find_teams(value, unique_teams_dict)
    elif isinstance(data, list):
        for item in data:
            find_teams(item, unique_teams_dict)

def sanitize_team_name(name):
    """Replaces AES internal bracket placeholders with 'TBD'."""
    if not name or not isinstance(name, str): return "TBD"
    if "asc_slot://" in name: return "TBD"
    return name

def retrieve_event_data(encoded_id):
    """Fetches event match data and saves it to a CSV with ultra-defensive parsing."""
    base_url = "https://results.advancedeventsystems.com/api/event"
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "referer": f"https://results.advancedeventsystems.com/event/{encoded_id}/home"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    all_matches = []
    seen_match_ids = set()

    try:
        print(f"Connecting to AES API for ID: {encoded_id}...")
        resp = session.get(f"{base_url}/{encoded_id}")
        if resp.status_code != 200:
            print(f"Error: Server returned status {resp.status_code}")
            return None

        event_data = resp.json()
        divisions = event_data.get('Divisions') or []
        event_name = event_data.get('Name', 'Unknown Event')
        print(f"--- {event_name} | {len(divisions)} Divisions ---\n")
        
        for div in divisions:
            if not isinstance(div, dict): continue
            div_id = div.get('DivisionId')
            div_name = div.get('Name', 'Unknown Division')
            if not div_id: continue
            
            print(f"Processing Division: {div_name}")
            
            unique_teams = {}
            pools_resp = session.get(f"{base_url}/{encoded_id}/division/{div_id}/pools")
            if pools_resp.status_code == 200:
                find_teams(pools_resp.json(), unique_teams)
            
            for t_id in unique_teams.keys():
                for suffix in ["past", "future"]:
                    matches_resp = session.get(f"{base_url}/{encoded_id}/division/{div_id}/team/{t_id}/schedule/{suffix}")
                    if matches_resp.status_code != 200: continue
                        
                    matches = matches_resp.json()
                    if not isinstance(matches, list): continue

                    for item in matches:
                        if not isinstance(item, dict): continue
                        match_info = item.get('Match') or {}
                        play_info = item.get('Play') or {}
                        
                        match_id = match_info.get('MatchId')
                        if not match_id or match_id in seen_match_ids: continue
                        seen_match_ids.add(match_id)
                        
                        # --- SAFE DATA EXTRACTION ---
                        # Time
                        raw_time = match_info.get('ScheduledStartDateTime')
                        time_formatted = raw_time.replace('T', ' ')[:16] if isinstance(raw_time, str) else "TBD"
                        
                        # Court (Uses safe_get to avoid 'NoneType' error)
                        court_name = safe_get(match_info, 'Court', 'Name', default="TBD")
                        
                        # Teams
                        team_a_name = sanitize_team_name(match_info.get('FirstTeamName'))
                        team_b_name = sanitize_team_name(match_info.get('SecondTeamName'))
                        # ----------------------------
                        
                        sets = match_info.get('Sets') or []
                        scores = {f'S{i+1}{k}': v for i in range(3) for k, v in [('A', ""), ('B', ""), ('D', False)]}
                        for i, s in enumerate(sets[:3]):
                            if not isinstance(s, dict): continue
                            idx = i + 1
                            scores[f'S{idx}A'] = s.get('FirstTeamScore', '')
                            scores[f'S{idx}B'] = s.get('SecondTeamScore', '')
                            scores[f'S{idx}D'] = s.get('IsDecidingSet', False)
                            
                        all_matches.append({
                            'Match_ID': match_id,
                            'Division': div_name,
                            'Phase_Name': play_info.get('CompleteFullName', match_info.get('MatchFullName', '')),
                            'Time': time_formatted,
                            'Court': court_name,
                            'Team_A_ID': match_info.get('FirstTeamId', ''),
                            'Team_A_Name': team_a_name,
                            'Team_A_Won_Match': match_info.get('FirstTeamWon', False),
                            'Team_B_ID': match_info.get('SecondTeamId', ''),
                            'Team_B_Name': team_b_name,
                            'Team_B_Won_Match': match_info.get('SecondTeamWon', False),
                            'Set1_TeamA': scores['S1A'], 'Set1_TeamB': scores['S1B'], 'Set1_Deciding': scores['S1D'],
                            'Set2_TeamA': scores['S2A'], 'Set2_TeamB': scores['S2B'], 'Set2_Deciding': scores['S2D'],
                            'Set3_TeamA': scores['S3A'], 'Set3_TeamB': scores['S3B'], 'Set3_Deciding': scores['S3D']
                        })
                time.sleep(0.05) 

        if all_matches:
            os.makedirs("Data/raw/event_results", exist_ok=True)
            filename = f"Data/raw/event_results/{encoded_id}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_matches[0].keys())
                writer.writeheader()
                writer.writerows(all_matches)
            print(f"\nSUCCESS: Saved {len(all_matches)} matches to '{filename}'.")
            return filename
        else:
            print("\nNo matches found.")
            return None
            
    except Exception as e:
        print(f"\nCritical error during execution: {e}")
        return None

if __name__ == "__main__":
    test_id = "PTAwMDAwNDE0OTM90"
    retrieve_event_data(test_id)
