import streamlit as st
from sqlalchemy import create_engine, text
from pathlib import Path


def get_connection():
    """Get a database connection using Streamlit's connection system."""
    # Try to get DATABASE_URL from Streamlit secrets
    try:
        if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
            # Production: Use the database URL from secrets
            database_url = st.secrets['DATABASE_URL']
            engine = create_engine(database_url)
            return engine.connect()
    except Exception:
        # If secrets access fails or doesn't exist, fall through to SQLite
        pass

    # Local development: Use SQLite file
    db_path = Path(__file__).parent / "dwts.db"
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(database_url)
    return engine.connect()


def init_db():
    """Initialize the database with the schema."""
    conn = get_connection()

    # Players table (Leo, Abby, Taylor, Turner)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            team_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    conn.commit()

    # DWTS teams (actual contestants on the show)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS dwts_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contestant_name TEXT NOT NULL,
            partner_name TEXT,
            division TEXT NOT NULL CHECK(division IN ('mens', 'womens')),
            is_eliminated BOOLEAN DEFAULT 0,
            elimination_week INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    conn.commit()

    # Player picks (which DWTS teams each player has picked)
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS player_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            dwts_team_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (dwts_team_id) REFERENCES dwts_teams(id),
            UNIQUE(player_id, dwts_team_id)
        )
    """))
    conn.commit()

    # Weekly scores table
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS weekly_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dwts_team_id INTEGER NOT NULL,
            week_number INTEGER NOT NULL,
            judge_name TEXT NOT NULL,
            score INTEGER NOT NULL CHECK(score >= 0 AND score <= 10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dwts_team_id) REFERENCES dwts_teams(id),
            UNIQUE(dwts_team_id, week_number, judge_name)
        )
    """))
    conn.commit()

    # Insert the 4 players if they don't exist
    players = [
        ('Leo', ''),
        ('Abby', ''),
        ('Taylor', ''),
        ('Turner', '')
    ]

    for name, team_name in players:
        conn.execute(text("""
            INSERT OR IGNORE INTO players (name, team_name)
            VALUES (:name, :team_name)
        """), {"name": name, "team_name": team_name})

    conn.commit()
    conn.close()


def get_all_players():
    """Get all players."""
    conn = get_connection()
    result = conn.execute(text("SELECT * FROM players ORDER BY name"))
    players = [dict(row._mapping) for row in result]
    conn.close()
    return players


def get_all_dwts_teams():
    """Get all DWTS teams."""
    conn = get_connection()
    result = conn.execute(text("""
        SELECT * FROM dwts_teams
        ORDER BY division, contestant_name
    """))
    teams = [dict(row._mapping) for row in result]
    conn.close()
    return teams


def add_dwts_team(contestant_name: str, partner_name: str, division: str):
    """Add a new DWTS team."""
    conn = get_connection()
    result = conn.execute(text("""
        INSERT INTO dwts_teams (contestant_name, partner_name, division)
        VALUES (:contestant_name, :partner_name, :division)
    """), {"contestant_name": contestant_name, "partner_name": partner_name, "division": division})
    team_id = result.lastrowid
    conn.commit()
    conn.close()
    return team_id


def update_player_team_name(player_id: int, team_name: str):
    """Update a player's team name."""
    conn = get_connection()
    conn.execute(text("""
        UPDATE players SET team_name = :team_name WHERE id = :player_id
    """), {"team_name": team_name, "player_id": player_id})
    conn.commit()
    conn.close()


def add_player_pick(player_id: int, dwts_team_id: int):
    """Assign a DWTS team to a player."""
    conn = get_connection()
    conn.execute(text("""
        INSERT OR REPLACE INTO player_picks (player_id, dwts_team_id)
        VALUES (:player_id, :dwts_team_id)
    """), {"player_id": player_id, "dwts_team_id": dwts_team_id})
    conn.commit()
    conn.close()


def get_player_picks(player_id: int):
    """Get all DWTS teams picked by a player."""
    conn = get_connection()
    result = conn.execute(text("""
        SELECT dt.*
        FROM dwts_teams dt
        JOIN player_picks pp ON dt.id = pp.dwts_team_id
        WHERE pp.player_id = :player_id
    """), {"player_id": player_id})
    picks = [dict(row._mapping) for row in result]
    conn.close()
    return picks


def add_weekly_score(dwts_team_id: int, week_number: int, judge_name: str, score: int):
    """Add or update a weekly score."""
    conn = get_connection()
    conn.execute(text("""
        INSERT OR REPLACE INTO weekly_scores
        (dwts_team_id, week_number, judge_name, score)
        VALUES (:dwts_team_id, :week_number, :judge_name, :score)
    """), {"dwts_team_id": dwts_team_id, "week_number": week_number, "judge_name": judge_name, "score": score})
    conn.commit()
    conn.close()


def get_team_total_score(dwts_team_id: int) -> int:
    """Get the total score for a DWTS team across all weeks."""
    conn = get_connection()
    result = conn.execute(text("""
        SELECT COALESCE(SUM(score), 0) as total
        FROM weekly_scores
        WHERE dwts_team_id = :dwts_team_id
    """), {"dwts_team_id": dwts_team_id})
    total = result.fetchone()[0]
    conn.close()
    return total


def get_player_total_score(player_id: int) -> int:
    """Get the total score for a player (sum of their picked teams' scores)."""
    conn = get_connection()
    result = conn.execute(text("""
        SELECT COALESCE(SUM(ws.score), 0) as total
        FROM weekly_scores ws
        JOIN player_picks pp ON ws.dwts_team_id = pp.dwts_team_id
        WHERE pp.player_id = :player_id
    """), {"player_id": player_id})
    total = result.fetchone()[0]
    conn.close()
    return total


def eliminate_team(dwts_team_id: int, week_number: int):
    """Mark a DWTS team as eliminated."""
    conn = get_connection()
    conn.execute(text("""
        UPDATE dwts_teams
        SET is_eliminated = 1, elimination_week = :week_number
        WHERE id = :dwts_team_id
    """), {"week_number": week_number, "dwts_team_id": dwts_team_id})
    conn.commit()
    conn.close()


def is_player_eliminated(player_id: int) -> bool:
    """Check if a player is eliminated (all their picks are eliminated)."""
    conn = get_connection()

    # First check if player has any picks at all
    result = conn.execute(text("""
        SELECT COUNT(*) as total_picks
        FROM player_picks
        WHERE player_id = :player_id
    """), {"player_id": player_id})
    total = result.fetchone()[0]

    # If no picks, player is not eliminated (just hasn't picked yet)
    if total == 0:
        conn.close()
        return False

    # Check if all picks are eliminated
    result = conn.execute(text("""
        SELECT COUNT(*) as active_count
        FROM dwts_teams dt
        JOIN player_picks pp ON dt.id = pp.dwts_team_id
        WHERE pp.player_id = :player_id AND dt.is_eliminated = 0
    """), {"player_id": player_id})
    active_count = result.fetchone()[0]
    conn.close()
    return active_count == 0


def get_leaderboard():
    """Get the leaderboard with player rankings."""
    conn = get_connection()
    result = conn.execute(text("""
        SELECT
            p.id,
            p.name,
            p.team_name,
            COALESCE(SUM(ws.score), 0) as total_score,
            COUNT(DISTINCT pp.dwts_team_id) as total_picks,
            COUNT(DISTINCT CASE WHEN dt.is_eliminated = 1 THEN dt.id END) as eliminated_picks
        FROM players p
        LEFT JOIN player_picks pp ON p.id = pp.player_id
        LEFT JOIN dwts_teams dt ON pp.dwts_team_id = dt.id
        LEFT JOIN weekly_scores ws ON dt.id = ws.dwts_team_id
        GROUP BY p.id, p.name, p.team_name
        ORDER BY total_score DESC
    """))
    leaderboard = [dict(row._mapping) for row in result]
    conn.close()
    return leaderboard


def get_weekly_scores_for_team(dwts_team_id: int, week_number: int):
    """Get all scores for a team in a specific week."""
    conn = get_connection()
    result = conn.execute(text("""
        SELECT judge_name, score
        FROM weekly_scores
        WHERE dwts_team_id = :dwts_team_id AND week_number = :week_number
        ORDER BY judge_name
    """), {"dwts_team_id": dwts_team_id, "week_number": week_number})
    scores = [dict(row._mapping) for row in result]
    conn.close()
    return scores


def get_latest_week() -> int:
    """Get the latest week number that has scores."""
    conn = get_connection()
    result = conn.execute(text("SELECT COALESCE(MAX(week_number), 0) as max_week FROM weekly_scores"))
    max_week = result.fetchone()[0]
    conn.close()
    return max_week
