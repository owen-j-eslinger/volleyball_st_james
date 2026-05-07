import sys
import requests
import json
import os
import time
from pathlib import Path

# ---------------------------------------------------------
# 1. BOOTSTRAP
# ---------------------------------------------------------
src_path = str(Path.cwd().parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ---------------------------------------------------------
# 2. UTILITY FUNCTIONS
# ---------------------------------------------------------
def find_teams(data, unique_teams_dict):
    """Recursively extracts Team IDs and Names to build the traversal list."""
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

# ---------------------------------------------------------
# 3. RAW DATA EXTRACTOR (JSON PREFERRED)
# ---------------------------------------------------------
def extract_raw_event_data(encoded_id, output_dir="Data/raw/event_results"):
    """
    Traverses the AES API, collects raw match data, and saves 
    it as a JSON file in the results directory.
    """
    base_url = "https://results.advancedeventsystems.com/api/event"
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0",
        "referer": f"https://results.advancedeventsystems.com/event/{encoded_id}/home"
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    unique_raw_matches = {}
    
    try:
        print(f"Connecting to AES API for ID: {encoded_id}...")
        resp = session.get(f"{base_url}/{encoded_id}")
        
        if resp.status_code != 200:
            print(f"Error: Server returned status {resp.status_code}")
            return None
            
        event_data = resp.json()
        divisions = event_data.get('Divisions') or []
        
        for div in divisions:
            div_id = div.get('DivisionId')
            div_name = div.get('Name', 'Unknown Division')
            if not div_id: continue
            
            print(f"Extracting Division: {div_name}")
            
            unique_teams = {}
            pools_resp = session.get(f"{base_url}/{encoded_id}/division/{div_id}/pools")
            if pools_resp.status_code == 200:
                find_teams(pools_resp.json(), unique_teams)
            
            for t_id in unique_teams.keys():
                for suffix in ["past", "future"]:
                    m_resp = session.get(f"{base_url}/{encoded_id}/division/{div_id}/team/{t_id}/schedule/{suffix}")
                    if m_resp.status_code != 200: continue
                        
                    matches = m_resp.json()
                    if not isinstance(matches, list): continue
                    
                    for item in matches:
                        match_id = item.get('Match', {}).get('MatchId')
                        if match_id and match_id not in unique_raw_matches:
                            item['_Injected_Division'] = div_name 
                            unique_raw_matches[match_id] = item
                            
                time.sleep(random.uniform(1.2, 2.5)) 
                
        if unique_raw_matches:
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{output_dir}/{encoded_id}.json"
            
            final_payload = list(unique_raw_matches.values())
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_payload, f, indent=4)
                
            print(f"\n[SUCCESS] Saved {len(final_payload)} raw matches to '{filename}'.")
            return filename
        
        print("\n[-] No matches found.")
        return None
            
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        return None

if __name__ == "__main__":
    test_id = "PTAwMDAwNDE0OTM90"
    extract_raw_event_data(test_id)
