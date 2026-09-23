import streamlit as st
from database import (
    get_all_dwts_teams,
    add_weekly_score,
    get_weekly_scores_for_team,
    get_latest_week
)


def render():
    """Render the scoring page."""

    st.subheader("Enter Weekly Scores")

    dwts_teams = get_all_dwts_teams()
    active_teams = [t for t in dwts_teams if not t['is_eliminated']]

    if not active_teams:
        st.warning("No active teams available. All teams have been eliminated or none have been added yet.")
        return

    # Week selection with session state to remember last selected week
    latest_week = get_latest_week()

    # Initialize session state for week number if not exists
    if 'selected_week' not in st.session_state:
        st.session_state.selected_week = latest_week if latest_week > 0 else 1

    week_number = st.number_input(
        "Week Number",
        min_value=1,
        value=st.session_state.selected_week,
        step=1,
        help="Enter the week number for these scores",
        key="week_input"
    )

    # Update session state when week changes
    if week_number != st.session_state.selected_week:
        st.session_state.selected_week = week_number

    st.divider()

    # Judge setup
    st.subheader("Judge Configuration")
    num_judges = st.number_input("Number of Judges", min_value=1, max_value=10, value=3, step=1)

    # Default judge names
    default_judges = ["Carrie-Ann", "Derek", "Bruno"]

    judge_names = []
    cols = st.columns(min(num_judges, 4))  # Max 4 columns
    for i in range(num_judges):
        with cols[i % 4]:
            # Use default judge name if available, otherwise "Judge N"
            default_name = default_judges[i] if i < len(default_judges) else f"Judge {i+1}"
            judge_name = st.text_input(
                f"Judge {i+1} Name",
                value=default_name,
                key=f"judge_{i}"
            )
            judge_names.append(judge_name)

    st.divider()
    st.subheader("Score Entry")

    # Organize teams by division
    mens_teams = [t for t in active_teams if t['division'] == 'mens']
    womens_teams = [t for t in active_teams if t['division'] == 'womens']

    # Create tabs for divisions
    div_tab1, div_tab2 = st.tabs(["Men's Division", "Women's Division"])

    def score_entry_for_teams(teams, division_name):
        """Helper function to create score entry UI for a list of teams."""
        for team in teams:
            with st.expander(f"{team['contestant_name']} & {team['partner_name']}", expanded=False):
                team_id = team['id']

                # Check if scores already exist for this week
                existing_scores = get_weekly_scores_for_team(team_id, week_number)
                existing_scores_dict = {s['judge_name']: s['score'] for s in existing_scores}

                # Create form for this team
                with st.form(f"score_form_{team_id}_{week_number}"):
                    st.write(f"**{team['contestant_name']} & {team['partner_name']}**")

                    scores = []
                    judge_cols = st.columns(min(num_judges, 4))

                    for i, judge_name in enumerate(judge_names):
                        with judge_cols[i % 4]:
                            default_score = existing_scores_dict.get(judge_name, 0)
                            score = st.number_input(
                                judge_name,
                                min_value=0,
                                max_value=10,
                                value=default_score,
                                step=1,
                                key=f"score_{team_id}_{week_number}_{judge_name}"
                            )
                            scores.append((judge_name, score))

                    # Calculate total
                    total = sum(s[1] for s in scores)
                    st.metric("Total Score", total)

                    submitted = st.form_submit_button("Save Scores")

                    if submitted:
                        try:
                            for judge_name, score in scores:
                                add_weekly_score(team_id, week_number, judge_name, score)
                            st.success(f"Saved scores for {team['contestant_name']}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving scores: {e}")

    with div_tab1:
        if mens_teams:
            score_entry_for_teams(mens_teams, "Men's")
        else:
            st.info("No active men's teams")

    with div_tab2:
        if womens_teams:
            score_entry_for_teams(womens_teams, "Women's")
        else:
            st.info("No active women's teams")

    # Show summary of scores entered for this week
    st.divider()
    st.subheader(f"Week {week_number} Summary")

    all_teams_with_scores = []
    for team in active_teams:
        team_scores = get_weekly_scores_for_team(team['id'], week_number)
        if team_scores:
            total = sum(s['score'] for s in team_scores)
            all_teams_with_scores.append({
                'name': f"{team['contestant_name']} & {team['partner_name']}",
                'division': team['division'],
                'total': total,
                'num_scores': len(team_scores)
            })

    if all_teams_with_scores:
        # Sort by total score
        all_teams_with_scores.sort(key=lambda x: x['total'], reverse=True)

        for team_data in all_teams_with_scores:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{team_data['name']}** ({team_data['division']})")
            with col2:
                st.write(f"Scores: {team_data['num_scores']}/{num_judges}")
            with col3:
                st.write(f"Total: **{team_data['total']}**")
    else:
        st.info(f"No scores entered for week {week_number} yet")
