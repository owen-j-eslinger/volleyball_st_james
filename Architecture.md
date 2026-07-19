# AES Volleyball Project Architecture

## Purpose

Collect, preserve, process, and analyze Advanced Event Systems volleyball data.

Primary goals:

- Build national-level standings and comparisons.
- Analyze selected clubs and teams.
- Measure Team X's performance.
- Analyze teams that Team X played.
- Support one-hop and two-hop opponent analysis.
- Preserve 2025–26 season data in a reproducible form.

## Data Sources

### Ranking API

Team-centered data:

- Team metadata
- Schedule
- Match results
- Finishes
- Rosters

### Results API

Event-centered data:

- Events
- Divisions
- Pools
- Schedules
- Matches

## Pipeline

### Event Pipeline

1. Discover events.
2. Save raw event metadata.
3. Download event results.
4. Preserve raw responses.
5. Build normalized event, division, team, and match tables.
6. Deduplicate records.
7. Produce master season tables.

### Team Pipeline

1. Select teams.
2. Download ranking API data.
3. Preserve raw responses.
4. Transform data into normalized tables.
5. Produce master team, match, finish, and roster tables.

## Project Layers

### Collection

Code that talks to AES APIs and saves raw responses.

### Processing

Code that converts raw data into normalized tables.

### Analysis

Code that calculates rankings, team performance, and opponent networks.

### Notebooks

Used for exploration and analysis, not required for routine data collection.

## Data Storage

```text
data/
    raw/
        events/
        teams/
    interim/
    processed/
        events/
        teams/
        season/
