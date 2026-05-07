# volleyball_st_james
For processing data on the AES Event System website

## Environment Preparation
Ensure that you have Python 3.x installed along with the necessary data manipulation and geocoding libraries. You can install the dependencies via pip using the following command:

```bash```
pip install pandas geopy
pip install thefuzz
pip install networkx pyvis


## Links
- https://www.advancedeventsystems.com/events
    - Find events through GUI
- https://www.advancedeventsystems.com/events/44496
    - Shows information about individual events (here EventID = 44496
- https://results.advancedeventsystems.com/event/PTAwMDAwNDEzNzk90/home
    - Results for a particular event
- https://advancedeventsystems.com/rankings/3472
    - Shows particular club
- https://advancedeventsystems.com/rank/185651

- https://advancedeventsystems.com/api/ranking/185651

- https://advancedeventsystems.com/api/ranking/185651/events

- https://advancedeventsystems.com/api/ranking/185651/finishes

- https://advancedeventsystems.com/api/ranking/185651/members

- https://advancedeventsystems.com/api/ranking/185651/events/40917/matches

# Volleyball Analytics Data Pipeline

This repository contains an ELT (Extract, Load, Transform) data pipeline designed to merge offline tournament data (JSON/CSV) with live national rankings and match data from the Advanced Event Systems (AES) API.

## 1. Project Structure

The project relies on a strict directory structure to separate raw data from analytical outputs.

```text
volleyball_st_james/
├── Data/
│   ├── raw/
│   │   ├── events/           # Offline JSON files of tournaments
│   │   ├── event_results/    # Offline JSON files of match results 
│   │   └── aes_api/          # Raw JSON payloads downloaded directly from AES
│   ├── processed/            
│   │   ├── events/           # Consolidated offline data
│   │   ├── clubs/            # Consolidated offline data
│   │   ├── teams/            # Cleaned, individual CSVs per team (from AES)
│   │   └── aes_master_*.csv  # The final, aggregated master databases
├── notebooks/                # Jupyter Notebooks for analysis and visualization
├── src/                      # Core Python modules (API Client, Transformer, Watchlist)
└── README.md                 # You are here
```

## 2. The Extraction & Transformation Pipeline
The data pipeline operates in three distinct phases:

### Phase 1: Local Data Consolidation (Detailed)

**The Objective:** 
The pipeline begins with approximately 4,000 raw files offline: ~2,000 JSON files containing event/tournament metadata and ~2,000 CSV files containing the actual match results. The goal of this phase is to parse, link, and flatten these unstructured files into a relational database format.

**Input Data Requirements:**
*   **Event JSONs:** Located in `Data/raw/events/`. Each file contains a unique `Key`, an `EventId`, and nested lists of `Clubs` and `Divisions`.
*   **Result CSVs:** Located in `Data/raw/event_results/`. The filenames correspond to the `Key` found in the Event JSONs. These files contain granular match data (Team A vs Team B, scores, etc.).

**The Consolidation Process:**
The initial Python script (executed via Jupyter Notebook) performs the following operations:
1.  **Ingestion:** Iterates through every JSON file in the raw events directory.
2.  **Relational Mapping:** Extracts the nested `Clubs` and `Divisions` lists and appends the parent `EventId` to them so they can be joined later.
3.  **Result Linking:** Uses the `Key` from the JSON to locate the matching `.csv` file in the results directory. It utilizes Pandas' dynamic separator engine (`sep=None`) to safely parse the CSVs, handling spaces and tabs correctly.
4.  **Mismatch Handling:** Because some tournaments have not published their results yet, there are more JSON files than CSV files. The script automatically detects missing CSVs and logs them.

**Generated Outputs:**
Running the consolidation script creates the foundational relational database in the `Data/processed/` directory:

1.  `events/master_events.csv`: High-level metadata for every tournament (Name, Date, Location).
2.  `events/master_match_results.csv`: The core dataset. Every single match played, linked to its parent EventId.
3.  `clubs/master_clubs.csv`: A list of all clubs that participated in each event.
4.  `divisions/master_divisions.csv`: Age and skill bracket metadata per event.
5.  `mismatch_report.csv`: An operational "To-Do" list showing exactly which events are still awaiting published CSV results.

*Note: You must successfully complete Phase 1 before attempting to run the AES API Network 

### Phase 2: Live AES Network Extraction (The Concentric Circles)
Instead of blindly downloading data for every team in the country, we use a Breadth-First Search (BFS) "Concentric Circle" approach to map the network of teams relevant to a specific target (e.g., Team X).

Tool Used: src/api_client.py (AESClient)

Action: We input a Target Team ID into the extraction notebook. The script finds all direct opponents (Degree 1), and then opponents of those opponents (Degree 2).

Execution: The AESClient automatically bypasses the AES Web Application Firewall (WAF) using stealth headers and downloads the raw metadata, schedule, roster, and matches JSON payloads for every team in that network into Data/raw/aes_api/.

### Phase 3: Transformation & Aggregation (ELT)
Once the raw data lake is populated, we must flatten the highly nested JSON (e.g., extracting individual set scores from arrays) and stitch the teams together.

Tool Used: src/transformer.py (AESTransformer)

Action: Run the Batch Transformation script. It reads the raw JSON offline and outputs clean CSVs for every team into Data/processed/teams/.

Aggregation: Run the Aggregation script to roll up the hundreds of individual CSVs into three master files:

aes_master_matches.csv (Granular match-by-match scores)

aes_master_finishes.csv (Overall tournament placements)

aes_master_rosters.csv (Player and staff demographics)

## 3. Analytical Capabilities
With the master databases built, the following analytical views can be generated in the notebooks/ directory:

The Common Opponent Matrix: Isolates two teams and compares their Win/Loss records against only the opponents they have both played.

Regional Dominance Leaderboard: Calculates the "Average Top % Placement" across all tournaments to find the most consistently dominant teams in the region.

Interactive Network Visualization: Uses NetworkX and PyVis to render a physics-based, color-coded HTML map of the regional team ecosystem based on how frequently they play each other.

