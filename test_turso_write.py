#!/usr/bin/env python3
"""Test writing to Turso database."""

import libsql_experimental as libsql
import toml

# Load secrets
with open('.streamlit/secrets.toml', 'r') as f:
    secrets = toml.load(f)

turso_url = secrets['TURBO_URL'].replace('libsql://', 'https://')
turso_token = secrets['TURBO_TOKEN']

print(f"Connecting to: {turso_url}")

conn = libsql.connect(database=turso_url, auth_token=turso_token)
cursor = conn.cursor()

# Check current players
print("\nBefore insert:")
cursor.execute("SELECT * FROM players")
players = cursor.fetchall()
print(f"Players: {len(players)}")
for player in players:
    print(f"  {player}")

# Try to insert a test player
print("\nTrying to insert test player...")
try:
    cursor.execute("INSERT INTO players (name, team_name) VALUES (?, ?)", ("Test Player", "Test Team"))
    conn.commit()
    print("✅ Insert successful!")
except Exception as e:
    print(f"❌ Insert failed: {e}")

# Check again
print("\nAfter insert:")
cursor.execute("SELECT * FROM players")
players = cursor.fetchall()
print(f"Players: {len(players)}")
for player in players:
    print(f"  {player}")

# Clean up - delete test player
print("\nCleaning up...")
cursor.execute("DELETE FROM players WHERE name = ?", ("Test Player",))
conn.commit()

conn.close()
print("\n✅ Write test complete!")
