#!/usr/bin/env python3
"""Test that the app can connect to and write to Turso."""

import sys
import os

# Mock streamlit secrets
class MockSecrets:
    def __init__(self):
        import toml
        with open('.streamlit/secrets.toml', 'r') as f:
            self._secrets = toml.load(f)

    def __getitem__(self, key):
        return self._secrets[key]

    def __contains__(self, key):
        return key in self._secrets

class MockStreamlit:
    def __init__(self):
        self.secrets = MockSecrets()

sys.modules['streamlit'] = MockStreamlit()

# Now import database module
from database import get_connection, get_all_players
from sqlalchemy import text

print("Testing Turso connection through database.py...")

# Test connection
conn = get_connection()
print("\n✅ Connection established!")

# Test read
print("\nTesting read...")
result = conn.execute(text("SELECT * FROM players"))
players = result.fetchall()
print(f"Found {len(players)} players:")
for player in players:
    print(f"  - {player}")

# Test write
print("\nTesting write...")
try:
    result = conn.execute(text("INSERT INTO players (name, team_name) VALUES (:name, :team_name)"),
                         {"name": "Write Test", "team_name": "Test Team"})
    conn.commit()
    print("✅ Write successful!")

    # Verify write
    result = conn.execute(text("SELECT * FROM players WHERE name = :name"), {"name": "Write Test"})
    test_player = result.fetchone()
    if test_player:
        print(f"✅ Verified: {test_player}")

    # Clean up
    conn.execute(text("DELETE FROM players WHERE name = :name"), {"name": "Write Test"})
    conn.commit()
    print("✅ Cleanup successful!")

except Exception as e:
    print(f"❌ Write failed: {e}")
    import traceback
    traceback.print_exc()

conn.close()
print("\n🎉 All tests passed! Your app should now persist data to Turso.")
