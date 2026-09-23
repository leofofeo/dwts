import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import threading

# Thread lock for file operations to prevent race conditions
_lock = threading.Lock()

# Data directory
DATA_DIR = Path(__file__).parent / "data"


def _load_json(filename: str) -> list:
    """Load data from a JSON file."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return []
    with open(filepath, 'r') as f:
        return json.load(f)


def _save_json(filename: str, data: list):
    """Save data to a JSON file."""
    filepath = DATA_DIR / filename
    DATA_DIR.mkdir(exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def _get_next_id(data: list) -> int:
    """Get the next available ID."""
    if not data:
        return 1
    return max(item['id'] for item in data) + 1


def init_db():
    """Initialize the database with default data if needed."""
    with _lock:
        players = _load_json('players.json')

        # Add default players if none exist
        if not players:
            default_players = [
                {'id': 1, 'name': 'Leo', 'team_name': '', 'created_at': datetime.now().isoformat()},
                {'id': 2, 'name': 'Abby', 'team_name': '', 'created_at': datetime.now().isoformat()},
                {'id': 3, 'name': 'Taylor', 'team_name': '', 'created_at': datetime.now().isoformat()},
                {'id': 4, 'name': 'Turner', 'team_name': '', 'created_at': datetime.now().isoformat()},
            ]
            _save_json('players.json', default_players)

        # Ensure other files exist
        for filename in ['dwts_teams.json', 'player_picks.json', 'weekly_scores.json']:
            if not (DATA_DIR / filename).exists():
                _save_json(filename, [])


def get_all_players() -> List[Dict]:
    """Get all players."""
    with _lock:
        return _load_json('players.json')


def get_all_dwts_teams() -> List[Dict]:
    """Get all DWTS teams."""
    with _lock:
        return _load_json('dwts_teams.json')


def add_dwts_team(contestant_name: str, partner_name: str, division: str) -> int:
    """Add a new DWTS team."""
    with _lock:
        teams = _load_json('dwts_teams.json')
        team_id = _get_next_id(teams)
        new_team = {
            'id': team_id,
            'contestant_name': contestant_name,
            'partner_name': partner_name,
            'division': division,
            'is_eliminated': False,
            'elimination_week': None,
            'created_at': datetime.now().isoformat()
        }
        teams.append(new_team)
        _save_json('dwts_teams.json', teams)
        return team_id


def update_player_team_name(player_id: int, team_name: str):
    """Update a player's team name."""
    with _lock:
        players = _load_json('players.json')
        for player in players:
            if player['id'] == player_id:
                player['team_name'] = team_name
                break
        _save_json('players.json', players)


def add_player_pick(player_id: int, dwts_team_id: int):
    """Assign a DWTS team to a player."""
    with _lock:
        picks = _load_json('player_picks.json')

        # Remove existing pick if it exists (INSERT OR REPLACE behavior)
        picks = [p for p in picks if not (p['player_id'] == player_id and p['dwts_team_id'] == dwts_team_id)]

        pick_id = _get_next_id(picks)
        new_pick = {
            'id': pick_id,
            'player_id': player_id,
            'dwts_team_id': dwts_team_id,
            'created_at': datetime.now().isoformat()
        }
        picks.append(new_pick)
        _save_json('player_picks.json', picks)


def get_player_picks(player_id: int) -> List[Dict]:
    """Get all DWTS teams picked by a player."""
    with _lock:
        picks = _load_json('player_picks.json')
        teams = _load_json('dwts_teams.json')

        # Get team IDs for this player
        team_ids = [p['dwts_team_id'] for p in picks if p['player_id'] == player_id]

        # Return matching teams
        return [t for t in teams if t['id'] in team_ids]


def add_weekly_score(dwts_team_id: int, week_number: int, judge_name: str, score: int):
    """Add or update a weekly score."""
    with _lock:
        scores = _load_json('weekly_scores.json')

        # Remove existing score for this team/week/judge (INSERT OR REPLACE)
        scores = [s for s in scores if not (
            s['dwts_team_id'] == dwts_team_id and
            s['week_number'] == week_number and
            s['judge_name'] == judge_name
        )]

        score_id = _get_next_id(scores)
        new_score = {
            'id': score_id,
            'dwts_team_id': dwts_team_id,
            'week_number': week_number,
            'judge_name': judge_name,
            'score': score,
            'created_at': datetime.now().isoformat()
        }
        scores.append(new_score)
        _save_json('weekly_scores.json', scores)


def get_team_total_score(dwts_team_id: int) -> int:
    """Get the total score for a DWTS team across all weeks."""
    with _lock:
        scores = _load_json('weekly_scores.json')
        team_scores = [s['score'] for s in scores if s['dwts_team_id'] == dwts_team_id]
        return sum(team_scores)


def get_player_total_score(player_id: int) -> int:
    """Get the total score for a player (sum of their picked teams' scores)."""
    with _lock:
        picks = _load_json('player_picks.json')
        scores = _load_json('weekly_scores.json')

        # Get team IDs for this player
        team_ids = [p['dwts_team_id'] for p in picks if p['player_id'] == player_id]

        # Sum scores for those teams
        total = sum(s['score'] for s in scores if s['dwts_team_id'] in team_ids)
        return total


def eliminate_team(dwts_team_id: int, week_number: int):
    """Mark a DWTS team as eliminated."""
    with _lock:
        teams = _load_json('dwts_teams.json')
        for team in teams:
            if team['id'] == dwts_team_id:
                team['is_eliminated'] = True
                team['elimination_week'] = week_number
                break
        _save_json('dwts_teams.json', teams)


def is_player_eliminated(player_id: int) -> bool:
    """Check if a player is eliminated (all their picks are eliminated)."""
    with _lock:
        picks = _load_json('player_picks.json')
        teams = _load_json('dwts_teams.json')

        # Get team IDs for this player
        team_ids = [p['dwts_team_id'] for p in picks if p['player_id'] == player_id]

        # If no picks, not eliminated
        if not team_ids:
            return False

        # Check if any teams are still active
        active_teams = [t for t in teams if t['id'] in team_ids and not t['is_eliminated']]
        return len(active_teams) == 0


def get_leaderboard() -> List[Dict]:
    """Get the leaderboard with player rankings."""
    with _lock:
        players = _load_json('players.json')
        picks = _load_json('player_picks.json')
        teams = _load_json('dwts_teams.json')
        scores = _load_json('weekly_scores.json')

        leaderboard = []
        for player in players:
            player_id = player['id']

            # Get picks for this player
            player_picks = [p for p in picks if p['player_id'] == player_id]
            team_ids = [p['dwts_team_id'] for p in player_picks]

            # Get teams for this player
            player_teams = [t for t in teams if t['id'] in team_ids]

            # Calculate total score
            total_score = sum(s['score'] for s in scores if s['dwts_team_id'] in team_ids)

            # Count eliminated picks
            eliminated_picks = sum(1 for t in player_teams if t['is_eliminated'])

            leaderboard.append({
                'id': player_id,
                'name': player['name'],
                'team_name': player['team_name'],
                'total_score': total_score,
                'total_picks': len(player_picks),
                'eliminated_picks': eliminated_picks
            })

        # Sort by score descending
        leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
        return leaderboard


def get_weekly_scores_for_team(dwts_team_id: int, week_number: int) -> List[Dict]:
    """Get all scores for a team in a specific week."""
    with _lock:
        scores = _load_json('weekly_scores.json')
        team_scores = [
            {'judge_name': s['judge_name'], 'score': s['score']}
            for s in scores
            if s['dwts_team_id'] == dwts_team_id and s['week_number'] == week_number
        ]
        team_scores.sort(key=lambda x: x['judge_name'])
        return team_scores


def get_latest_week() -> int:
    """Get the latest week number that has scores."""
    with _lock:
        scores = _load_json('weekly_scores.json')
        if not scores:
            return 0
        return max(s['week_number'] for s in scores)


def add_player(name: str, team_name: str = "") -> int:
    """Add a new player."""
    with _lock:
        players = _load_json('players.json')
        player_id = _get_next_id(players)
        new_player = {
            'id': player_id,
            'name': name,
            'team_name': team_name,
            'created_at': datetime.now().isoformat()
        }
        players.append(new_player)
        _save_json('players.json', players)
        return player_id


def delete_player(player_id: int):
    """Delete a player and all their picks."""
    with _lock:
        # Delete player picks
        picks = _load_json('player_picks.json')
        picks = [p for p in picks if p['player_id'] != player_id]
        _save_json('player_picks.json', picks)

        # Delete player
        players = _load_json('players.json')
        players = [p for p in players if p['id'] != player_id]
        _save_json('players.json', players)
