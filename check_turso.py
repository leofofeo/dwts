#!/usr/bin/env python3
"""Check what's in the Turso database."""

from sqlalchemy import create_engine, text
import toml
import sqlalchemy_libsql  # Import to register the dialect

# Load secrets
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

turso_url = secrets['TURBO_URL']
turso_token = secrets['TURBO_TOKEN']

# Connect to Turso - convert libsql:// to sqlite+libsql://
# Try a different approach - don't URL encode the token, pass it directly
database_url = turso_url.replace('libsql://', 'sqlite+libsql://')
print(f"Token present: {bool(turso_token)}, length: {len(turso_token)}")
print(f"URL before auth: {database_url}")
final_url = f"{database_url}?authToken={turso_token}&secure=true"
print(f"Final URL (first 80 chars): {final_url[:80]}...")
engine = create_engine(final_url, connect_args={'check_same_thread': False}, echo=False)

with engine.connect() as conn:
    print("=== TABLES ===")
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    tables = result.fetchall()
    for table in tables:
        print(f"  - {table[0]}")

    print("\n=== PLAYERS ===")
    try:
        result = conn.execute(text("SELECT * FROM players"))
        players = result.fetchall()
        if players:
            for player in players:
                print(f"  {player}")
        else:
            print("  (empty)")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== DWTS TEAMS ===")
    try:
        result = conn.execute(text("SELECT * FROM dwts_teams"))
        teams = result.fetchall()
        if teams:
            for team in teams:
                print(f"  {team}")
        else:
            print("  (empty)")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n=== WEEKLY SCORES ===")
    try:
        result = conn.execute(text("SELECT COUNT(*) as count FROM weekly_scores"))
        count = result.fetchone()[0]
        print(f"  Total scores: {count}")
    except Exception as e:
        print(f"  Error: {e}")
