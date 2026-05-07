import requests
import json
import time
from pathlib import Path

class AESClient:
    def __init__(self, raw_data_dir='../Data/raw/aes_api'):
        self.raw_data_dir = Path(raw_data_dir).resolve()
        self.base_api = "https://advancedeventsystems.com/api/ranking"
        self.main_page = "https://advancedeventsystems.com/rankings"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        }
        self.session = requests.Session()

    def _bypass_firewall(self, team_id):
        referer_url = f"{self.main_page}/{team_id}"
        self.session.get(referer_url, headers={'User-Agent': self.headers['User-Agent']}, timeout=10)
        self.headers['Referer'] = referer_url

    def _fetch_and_save(self, url, team_id, filename):
        self._bypass_firewall(team_id)
        team_dir = self.raw_data_dir / f"team_{team_id}"
        team_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                file_path = team_dir / filename
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                return data
            return None
        except Exception:
            return None

    def get_team_metadata(self, team_id):
        return self._fetch_and_save(f"{self.base_api}/{team_id}", team_id, 'metadata.json')

    def get_schedule(self, team_id):
        return self._fetch_and_save(f"{self.base_api}/{team_id}/events", team_id, 'schedule.json')

    def get_finishes(self, team_id):
        return self._fetch_and_save(f"{self.base_api}/{team_id}/finishes", team_id, 'finishes.json')

    def get_roster(self, team_id):
        return self._fetch_and_save(f"{self.base_api}/{team_id}/members", team_id, 'roster.json')

    def get_match_results(self, team_id, event_id):
        return self._fetch_and_save(f"{self.base_api}/{team_id}/events/{event_id}/matches", team_id, f'matches_event_{event_id}.json')
    
    def get_all_team_data(self, team_id):
        self.get_team_metadata(team_id)
        self.get_finishes(team_id)
        self.get_roster(team_id)
        schedule = self.get_schedule(team_id)
        if schedule:
            tournaments = schedule.get('value', schedule) if isinstance(schedule, dict) else schedule
            for tourney in tournaments:
                e_id = tourney.get('eventId')
                if e_id:
                    self.get_match_results(team_id, e_id)
                    time.sleep(0.5)
