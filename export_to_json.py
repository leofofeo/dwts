#!/usr/bin/env python3
"""Export Turso database to JSON files."""

import json
import libsql_experimental as libsql
import toml
from pathlib import Path

# Load secrets
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

turso_url = secrets['TURBO_URL'].replace('libsql://', 'https://')
turso_token = secrets['TURBO_TOKEN']

# Connect to Turso
print(f"Connecting to Turso...")
conn = libsql.connect(database=turso_url, auth_token=turso_token)
cursor = conn.cursor()

# Create data directory
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

# Export players
print("\nExporting players...")
cursor.execute("SELECT * FROM players")
players = []
for row in cursor.fetchall():
    players.append({
        "id": row[0],
        "name": row[1],
        "team_name": row[2],
        "created_at": row[3]
    })
print(f"  Found {len(players)} players")

with open(data_dir / "players.json", "w") as f:
    json.dump(players, f, indent=2)

# Export dwts_teams
print("\nExporting DWTS teams...")
cursor.execute("SELECT * FROM dwts_teams")
teams = []
for row in cursor.fetchall():
    teams.append({
        "id": row[0],
        "contestant_name": row[1],
        "partner_name": row[2],
        "division": row[3],
        "is_eliminated": bool(row[4]),
        "elimination_week": row[5],
        "created_at": row[6]
    })
print(f"  Found {len(teams)} teams")

with open(data_dir / "dwts_teams.json", "w") as f:
    json.dump(teams, f, indent=2)

# Export player_picks
print("\nExporting player picks...")
cursor.execute("SELECT * FROM player_picks")
picks = []
for row in cursor.fetchall():
    picks.append({
        "id": row[0],
        "player_id": row[1],
        "dwts_team_id": row[2],
        "created_at": row[3]
    })
print(f"  Found {len(picks)} picks")

with open(data_dir / "player_picks.json", "w") as f:
    json.dump(picks, f, indent=2)

# Export weekly_scores
print("\nExporting weekly scores...")
cursor.execute("SELECT * FROM weekly_scores")
scores = []
for row in cursor.fetchall():
    scores.append({
        "id": row[0],
        "dwts_team_id": row[1],
        "week_number": row[2],
        "judge_name": row[3],
        "score": row[4],
        "created_at": row[5]
    })
print(f"  Found {len(scores)} scores")

with open(data_dir / "weekly_scores.json", "w") as f:
    json.dump(scores, f, indent=2)

conn.close()

print("\n✅ Export complete! JSON files created in data/")
print("  - data/players.json")
print("  - data/dwts_teams.json")
print("  - data/player_picks.json")
print("  - data/weekly_scores.json")
