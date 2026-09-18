import streamlit as st
from database import (
    get_all_players,
    get_all_dwts_teams,
    add_dwts_team,
    update_player_team_name,
    add_player_pick,
    get_player_picks,
    eliminate_team
)


def render():
    """Render the admin page."""

    tab1, tab2, tab3, tab4 = st.tabs([
        "Manage DWTS Teams",
        "Assign Teams to Players",
        "Update Player Team Names",
        "Eliminate Teams"
    ])

    with tab1:
        st.subheader("Add DWTS Contestant Team")

        with st.form("add_dwts_team"):
            contestant_name = st.text_input("Contestant Name*", placeholder="e.g., Chandler")
            partner_name = st.text_input("Professional Partner Name*", placeholder="e.g., Brandon")
            division = st.selectbox("Division*", ["mens", "womens"])

            submitted = st.form_submit_button("Add Team")

            if submitted:
                if not contestant_name or not partner_name:
                    st.error("Please fill in all required fields")
                else:
                    try:
                        add_dwts_team(contestant_name, partner_name, division)
                        st.success(f"Added {contestant_name} & {partner_name} to {division} division!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding team: {e}")

        st.divider()
        st.subheader("Existing DWTS Teams")

        teams = get_all_dwts_teams()
        if teams:
            mens_teams = [t for t in teams if t['division'] == 'mens']
            womens_teams = [t for t in teams if t['division'] == 'womens']

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Men's Division**")
                for team in mens_teams:
                    status = "❌ Eliminated" if team['is_eliminated'] else "✅ Active"
                    st.write(f"#{team['id']} - {team['contestant_name']} & {team['partner_name']} ({status})")

            with col2:
                st.markdown("**Women's Division**")
                for team in womens_teams:
                    status = "❌ Eliminated" if team['is_eliminated'] else "✅ Active"
                    st.write(f"#{team['id']} - {team['contestant_name']} & {team['partner_name']} ({status})")
        else:
            st.info("No DWTS teams added yet.")

    with tab2:
        st.subheader("Assign DWTS Teams to Players")

        players = get_all_players()
        dwts_teams = get_all_dwts_teams()

        if not dwts_teams:
            st.warning("No DWTS teams available. Add teams first in the 'Manage DWTS Teams' tab.")
        else:
            selected_player = st.selectbox(
                "Select Player",
                options=[(p['id'], p['name']) for p in players],
                format_func=lambda x: x[1]
            )

            if selected_player:
                player_id = selected_player[0]
                player_name = selected_player[1]

                st.write(f"**Current picks for {player_name}:**")
                current_picks = get_player_picks(player_id)

                if current_picks:
                    for pick in current_picks:
                        st.write(f"- {pick['contestant_name']} & {pick['partner_name']} ({pick['division']})")
                else:
                    st.info("No picks yet")

                st.divider()

                # Separate by division
                mens_teams = [t for t in dwts_teams if t['division'] == 'mens']
                womens_teams = [t for t in dwts_teams if t['division'] == 'womens']

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Men's Division**")
                    if mens_teams:
                        selected_mens = st.selectbox(
                            "Select Men's Team",
                            options=[(t['id'], f"{t['contestant_name']} & {t['partner_name']}") for t in mens_teams],
                            format_func=lambda x: x[1],
                            key="mens_select"
                        )
                        if st.button("Assign Men's Team"):
                            try:
                                add_player_pick(player_id, selected_mens[0])
                                st.success(f"Assigned {selected_mens[1]} to {player_name}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

                with col2:
                    st.markdown("**Women's Division**")
                    if womens_teams:
                        selected_womens = st.selectbox(
                            "Select Women's Team",
                            options=[(t['id'], f"{t['contestant_name']} & {t['partner_name']}") for t in womens_teams],
                            format_func=lambda x: x[1],
                            key="womens_select"
                        )
                        if st.button("Assign Women's Team"):
                            try:
                                add_player_pick(player_id, selected_womens[0])
                                st.success(f"Assigned {selected_womens[1]} to {player_name}!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

    with tab3:
        st.subheader("Update Player Team Names")
        st.caption("Give each player a fun team name that will be displayed on the leaderboard")

        players = get_all_players()

        for player in players:
            with st.form(f"update_name_{player['id']}"):
                current_name = player['team_name'] if player['team_name'] else ""
                new_name = st.text_input(
                    f"{player['name']}'s Team Name",
                    value=current_name,
                    placeholder="e.g., Team Awesome"
                )
                submitted = st.form_submit_button(f"Update {player['name']}")

                if submitted:
                    try:
                        update_player_team_name(player['id'], new_name)
                        st.success(f"Updated team name for {player['name']}!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab4:
        st.subheader("Eliminate Teams")
        st.caption("Mark teams as eliminated when they're voted off")

        dwts_teams = get_all_dwts_teams()
        active_teams = [t for t in dwts_teams if not t['is_eliminated']]

        if not active_teams:
            st.info("No active teams to eliminate")
        else:
            with st.form("eliminate_team"):
                team_to_eliminate = st.selectbox(
                    "Select Team to Eliminate",
                    options=[(t['id'], f"{t['contestant_name']} & {t['partner_name']} ({t['division']})") for t in active_teams],
                    format_func=lambda x: x[1]
                )

                week_number = st.number_input("Elimination Week", min_value=1, value=1, step=1)

                submitted = st.form_submit_button("Eliminate Team")

                if submitted:
                    try:
                        eliminate_team(team_to_eliminate[0], week_number)
                        st.success(f"Eliminated {team_to_eliminate[1]} in week {week_number}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
