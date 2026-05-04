import requests
import csv
import os

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

def retrieve_event_data(encoded_id):
    """
    Fetches match data for a given encoded event ID and saves it to a CSV.
    Returns the filepath of the saved CSV, or None if it fails/finds nothing.
    """
    base_url = "https://results.advancedeventsystems.com/api/event"
    
    # 1. Headers must be defined INSIDE so the referer updates for each ID
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "referer": f"https://results.advancedeventsystems.com/event/{encoded_id}/home"
    }
    
    # 2. State variables must reset every time the function is called
    session = requests.Session()
    session.headers.update(headers)
    all_matches = []
    seen_match_ids = set()

    try:
        print(f"Connecting to AES Event API for ID: {encoded_id}...")
        event_data = session.get(f"{base_url}/{encoded_id}").json()
        divisions = event_data.get('Divisions', [])
        
        event_name = event_data.get('Name', 'Unknown Event')
        print(f"--- {event_name} | {len(divisions)} Divisions ---\n")
        
        for div in divisions:
            div_id = div['DivisionId']
            div_name = div['Name']
            print(f"Processing: {div_name}")
            
            # Extract Teams for the Division
            unique_teams = {}
            pools_data = session.get(f"{base_url}/{encoded_id}/division/{div_id}/pools").json()
            find_teams(pools_data, unique_teams)
            
            # Extract and Flatten Match Data
            for t_id in unique_teams.keys():
                matches_url = f"{base_url}/{encoded_id}/division/{div_id}/team/{t_id}/schedule/past"
                matches = session.get(matches_url).json()
                
                for item in matches:
                    match_info = item.get('Match', {})
                    play_info = item.get('Play', {})
                    
                    if not match_info: continue
                    
                    match_id = match_info.get('MatchId')
                    
                    # Deduplication
                    if match_id in seen_match_ids:
                        continue
                    seen_match_ids.add(match_id)
                    
                    # Flatten the 'Sets' array
                    sets = match_info.get('Sets', [])
                    scores = {
                        'S1A': "", 'S1B': "", 'S1D': False,
                        'S2A': "", 'S2B': "", 'S2D': False,
                        'S3A': "", 'S3B': "", 'S3D': False
                    }
                    
                    for i, s in enumerate(sets[:3]):
                        idx = i + 1
                        scores[f'S{idx}A'] = s.get('FirstTeamScore', '')
                        scores[f'S{idx}B'] = s.get('SecondTeamScore', '')
                        scores[f'S{idx}D'] = s.get('IsDecidingSet', False)
                        
                    time_raw = match_info.get('ScheduledStartDateTime', 'TBD').replace('T', ' ')[:16]
                    
                    all_matches.append({
                        'Match_ID': match_id,
                        'Division': div_name,
                        'Phase_Name': play_info.get('CompleteFullName', match_info.get('MatchFullName', '')),
                        'Time': time_raw,
                        'Court': match_info.get('Court', {}).get('Name', 'Unknown'),
                        
                        'Team_A_ID': match_info.get('FirstTeamId', ''),
                        'Team_A_Name': match_info.get('FirstTeamName', 'Unknown'),
                        'Team_A_Won_Match': match_info.get('FirstTeamWon', False),
                        
                        'Team_B_ID': match_info.get('SecondTeamId', ''),
                        'Team_B_Name': match_info.get('SecondTeamName', 'Unknown'),
                        'Team_B_Won_Match': match_info.get('SecondTeamWon', False),
                        
                        'Set1_TeamA': scores['S1A'], 'Set1_TeamB': scores['S1B'], 'Set1_Deciding': scores['S1D'],
                        'Set2_TeamA': scores['S2A'], 'Set2_TeamB': scores['S2B'], 'Set2_Deciding': scores['S2D'],
                        'Set3_TeamA': scores['S3A'], 'Set3_TeamB': scores['S3B'], 'Set3_Deciding': scores['S3D']
                    })
                    
        # 3. Save Output
        if all_matches:
            # Added a safety check to ensure the "Data" folder exists
            os.makedirs("Data", exist_ok=True)
            
            filename = f"Data/{encoded_id}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_matches[0].keys())
                writer.writeheader()
                writer.writerows(all_matches)
                
            print(f"\n🎉 SUCCESS! Saved {len(all_matches)} unique competitive matches to '{filename}'.")
            return filename
        else:
            print("\nNo match records found.")
            return None
            
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return None

# --- Testing / Execution Guard ---
if __name__ == "__main__":
    test_id = "PTAwMDAwNDEyODc90"
    retrieve_event_data(test_id)
