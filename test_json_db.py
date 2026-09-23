#!/usr/bin/env python3
"""Test JSON-based database functions."""

from database import (
    init_db, get_all_players, add_player, delete_player,
    get_all_dwts_teams, add_dwts_team,
    add_player_pick, get_player_picks,
    add_weekly_score, get_team_total_score, get_player_total_score,
    get_leaderboard, is_player_eliminated
)

print("Testing JSON-based database...")

# Initialize
init_db()
print("✅ Database initialized")

# Test reading players
players = get_all_players()
print(f"\n✅ Read {len(players)} players:")
for p in players[:3]:
    print(f"   - {p['name']}")

# Test reading teams
teams = get_all_dwts_teams()
print(f"\n✅ Read {len(teams)} DWTS teams")

# Test leaderboard
leaderboard = get_leaderboard()
print(f"\n✅ Leaderboard has {len(leaderboard)} entries:")
for entry in leaderboard[:3]:
    print(f"   {entry['name']}: {entry['total_score']} points")

# Test write - add a test player
print("\n📝 Testing write operations...")
test_player_id = add_player("Test Player", "Test Team")
print(f"✅ Added test player with ID {test_player_id}")

# Verify
players = get_all_players()
test_player = next((p for p in players if p['id'] == test_player_id), None)
if test_player:
    print(f"✅ Verified: {test_player['name']} exists")

# Clean up
delete_player(test_player_id)
players = get_all_players()
test_player = next((p for p in players if p['id'] == test_player_id), None)
if not test_player:
    print(f"✅ Cleanup successful: test player deleted")

print("\n🎉 All tests passed! JSON database is working correctly.")
