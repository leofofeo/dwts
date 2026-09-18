# Dancing With The Stars - Friends Competition Tracker

A Streamlit application to track a friendly DWTS competition among friends.

## Features

- **Leaderboard**: View current standings with rankings, scores, and elimination status
- **Team Details**: See which DWTS teams each player has picked
- **Admin Panel**: Manage DWTS teams, assign picks to players, and eliminate teams (password protected)
- **Scoring Page**: Enter weekly judge scores for each team (password protected)
- **Danger Zone**: Automatically highlights players with only one team remaining
- **Team Names**: Players can have custom team names displayed on the leaderboard

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the application:
   ```bash
   uv run streamlit run main.py
   ```

3. Access the app at `http://localhost:8501`

## Default Password

The admin and scoring pages are protected with the password: `dwts2024`

You can change this in [main.py](main.py) (search for "dwts2024")

## Database Schema

The app uses SQLite with the following tables:

- **players**: The 4 friends competing (Leo, Abby, Taylor, Turner)
- **dwts_teams**: Actual DWTS contestant teams from the show
- **player_picks**: Links players to their chosen DWTS teams (one from men's, one from women's)
- **weekly_scores**: Judge scores for each team by week

## Usage Guide

### Initial Setup (Admin Panel)

1. Go to Admin → "Manage DWTS Teams" tab
2. Add all the contestant teams from this season (specify men's or women's division)
3. Go to "Assign Teams to Players" tab
4. For each player, assign one team from men's and one from women's division
5. (Optional) Go to "Update Player Team Names" to give each player a fun team name

### Weekly Scoring

1. Go to the Scoring page
2. Enter the week number
3. Configure the number of judges (typically 3)
4. For each team, enter the scores from each judge
5. Click "Save Scores" for each team

### Viewing Results

- **Leaderboard**: Shows all players ranked by total score
- **Team Details**: Select a player to see their picked teams and status
- **Danger Zone**: Automatically shows players with only 1 team left

### Eliminations

1. Go to Admin → "Eliminate Teams" tab
2. Select the team that was eliminated
3. Enter the week number
4. Click "Eliminate Team"

Players are automatically marked as eliminated when all their teams are gone.

## Deployment

### Streamlit Community Cloud (Recommended)

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repository
5. Set main file path to: `main.py`
6. Deploy!

Streamlit Cloud will automatically:
- Detect `pyproject.toml` and install dependencies
- Create and persist the SQLite database
- Provide a free public URL

### Other Options

- **Render**: Free tier available, supports Python apps
- **Fly.io**: Free tier with minimal setup

**Note**: The app uses SQLite, so the database file will persist on the server's filesystem. For Streamlit Cloud, the database persists across deploys.

## Future Enhancement Ideas

- Weekly performance graphs
- Average score per team
- Historical week-by-week breakdown
- Prediction/betting features
- Export data to CSV
- More detailed statistics and analytics
