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

The app uses **persistent database storage** that works seamlessly in both local development and production:

- **Local Development**: Automatically uses SQLite (`dwts.db` file)
- **Production**: Uses Turso (free serverless SQLite) for permanent data persistence

### Quick Deploy to Streamlit Cloud

1. **Set up Turso database** (5 minutes, free):
   - Sign up at [turso.tech](https://turso.tech)
   - Create a database and get your DATABASE_URL
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

2. **Deploy to Streamlit Cloud**:
   - Push this repo to GitHub
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app" and connect your repo
   - Set main file path: `main.py`
   - In Advanced Settings → Secrets, add:
     ```toml
     DATABASE_URL = "libsql://your-database.turso.io?authToken=your-token"
     ```
   - Click "Deploy"

3. **Done!** Your data persists permanently across all deploys.

### Full Deployment Guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Complete Turso setup instructions
- Alternative database options (PostgreSQL, Neon, Supabase)
- Troubleshooting
- Backup/restore procedures

## Future Enhancement Ideas

- Weekly performance graphs
- Average score per team
- Historical week-by-week breakdown
- Prediction/betting features
- Export data to CSV
- More detailed statistics and analytics
