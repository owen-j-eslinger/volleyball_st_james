import pandas as pd
import json
from pathlib import Path

class AESTransformer:
    def __init__(self, raw_data_dir='../Data/raw/aes_api', processed_dir='../Data/processed/teams'):
        self.raw_dir = Path(raw_data_dir).resolve()
        self.processed_dir = Path(processed_dir).resolve()
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _load_json(self, filepath):
        try:
            if filepath.exists() and filepath.stat().st_size > 5:
                with open(filepath, 'r') as f:
                    return json.load(f)
            return None
        except Exception:
            return None

    def transform_roster(self, team_id):
        filepath = self.raw_dir / f"team_{team_id}/roster.json"
        data = self._load_json(filepath)
        if not data: return None
        df = pd.json_normalize(data)
        if df.empty: return None

        df = df.rename(columns={
            'memberFirstName': 'First_Name', 'memberLastName': 'Last_Name',
            'jerseyNumber': 'Jersey', 'position': 'Position',
            'gradYear': 'Class', 'teamUserType.isPlayer': 'Is_Player'
        })
        
        cols = [c for c in ['First_Name', 'Last_Name', 'Jersey', 'Position', 'Class', 'Is_Player'] if c in df.columns]
        df = df[cols]
        out_path = self.processed_dir / f"team_{team_id}_roster.csv"
        df.to_csv(out_path, index=False)
        return out_path

    def transform_matches(self, team_id):
        team_folder = self.raw_dir / f"team_{team_id}"
        match_files = list(team_folder.glob("matches_event_*.json"))
        if not match_files: return None

        all_matches = []
        for mf in match_files:
            data = self._load_json(mf)
            if not data: continue
            if isinstance(data, dict):
                data = data.get('value', data.get('data', data))
            if isinstance(data, list):
                all_matches.extend(data)

        if not all_matches: return None
        df = pd.json_normalize(all_matches)

        def extract_sets(scores_list):
            if not isinstance(scores_list, list) or len(scores_list) == 0:
                return pd.Series([None, None, None, None, None, None])
            s1_t = scores_list[0].get('teamScore') if len(scores_list) > 0 else None
            s1_o = scores_list[0].get('opponentScore') if len(scores_list) > 0 else None
            s2_t = scores_list[1].get('teamScore') if len(scores_list) > 1 else None
            s2_o = scores_list[1].get('opponentScore') if len(scores_list) > 1 else None
            s3_t = scores_list[2].get('teamScore') if len(scores_list) > 2 else None
            s3_o = scores_list[2].get('opponentScore') if len(scores_list) > 2 else None
            return pd.Series([s1_t, s1_o, s2_t, s2_o, s3_t, s3_o])

        if 'scores' in df.columns:
            df[['S1_T', 'S1_O', 'S2_T', 'S2_O', 'S3_T', 'S3_O']] = df['scores'].apply(extract_sets)

        df = df.rename(columns={'opponentName': 'Opponent', 'opponentCode': 'Opp_Code', 'matchOutcomeType.displayName': 'Result'})
        cols = ['Opponent', 'Opp_Code', 'Result', 'S1_T', 'S1_O', 'S2_T', 'S2_O', 'S3_T', 'S3_O']
        df = df[[c for c in cols if c in df.columns]]
        
        out_path = self.processed_dir / f"team_{team_id}_matches.csv"
        df.to_csv(out_path, index=False)
        return out_path

    def process_all(self, team_id):
        self.transform_roster(team_id)
        self.transform_matches(team_id)
