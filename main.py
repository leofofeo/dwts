import streamlit as st
from database import init_db, get_leaderboard, get_all_players, get_player_picks, is_player_eliminated

# Initialize database
init_db()

st.set_page_config(
    page_title="DWTS Competition Tracker",
    page_icon="💃",
    layout="wide"
)

st.title("💃 Dancing With The Stars - Friends Competition")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Leaderboard", "Team Details", "Admin", "Scoring", "Data Export"])

if page == "Leaderboard":
    st.header("Current Standings")

    leaderboard = get_leaderboard()

    if not leaderboard:
        st.info("No data yet. Add teams and scores in the Admin and Scoring pages.")
    else:
        # Create columns for better display
        for idx, row in enumerate(leaderboard, 1):
            player_eliminated = is_player_eliminated(row['id'])

            # Determine medal/position emoji
            if idx == 1:
                position = "🥇"
            elif idx == 2:
                position = "🥈"
            elif idx == 3:
                position = "🥉"
            else:
                position = f"#{idx}"

            # Create a card for each player
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])

            with col1:
                st.markdown(f"### {position}")

            with col2:
                display_name = row['team_name'] if row['team_name'] else row['name']
                if player_eliminated:
                    st.markdown(f"### ~~{display_name}~~ ❌")
                    st.caption("ELIMINATED")
                else:
                    st.markdown(f"### {display_name}")
                st.caption(f"Player: {row['name']}")

            with col3:
                st.metric("Total Score", row['total_score'])

            with col4:
                active_picks = row['total_picks'] - row['eliminated_picks']
                st.metric("Active Picks", f"{active_picks}/{row['total_picks']}")

            st.divider()

        # Show danger zone (players with only 1 team left)
        st.header("⚠️ Danger Zone")
        danger_players = [
            row for row in leaderboard
            if (row['total_picks'] - row['eliminated_picks']) == 1 and not is_player_eliminated(row['id'])
        ]

        if danger_players:
            for row in danger_players:
                display_name = row['team_name'] if row['team_name'] else row['name']
                st.warning(f"**{display_name}** ({row['name']}) - Only 1 team remaining!")
        else:
            st.success("No one in the danger zone yet!")

elif page == "Team Details":
    st.header("Team Details")

    players = get_all_players()

    if not players:
        st.info("No players found.")
    else:
        selected_player = st.selectbox(
            "Select a player",
            options=[(p['id'], p['team_name'] if p['team_name'] else p['name']) for p in players],
            format_func=lambda x: x[1]
        )

        if selected_player:
            player_id = selected_player[0]
            picks = get_player_picks(player_id)

            if not picks:
                st.info("This player hasn't picked any teams yet.")
            else:
                st.subheader("Picked Teams")

                mens_teams = [p for p in picks if p['division'] == 'mens']
                womens_teams = [p for p in picks if p['division'] == 'womens']

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Men's Division")
                    for team in mens_teams:
                        status = "❌ ELIMINATED" if team['is_eliminated'] else "✅ Active"
                        st.write(f"**{team['contestant_name']}** & {team['partner_name']}")
                        st.caption(status)

                with col2:
                    st.markdown("### Women's Division")
                    for team in womens_teams:
                        status = "❌ ELIMINATED" if team['is_eliminated'] else "✅ Active"
                        st.write(f"**{team['contestant_name']}** & {team['partner_name']}")
                        st.caption(status)

elif page == "Admin":
    st.header("🔒 Admin Panel")

    # Simple password protection
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        password = st.text_input("Enter admin password", type="password", key="admin_password")
        if st.button("Login", key="admin_login"):
            if password == "dwts2024":  # You can change this password
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
    else:
        st.success("Authenticated")

        if st.button("Logout", key="admin_logout"):
            st.session_state.authenticated = False
            st.rerun()

        # Import here to avoid running code before auth
        from pages import admin_page
        admin_page.render()

elif page == "Scoring":
    st.header("🔒 Score Entry")

    # Simple password protection
    if 'authenticated_scoring' not in st.session_state:
        st.session_state.authenticated_scoring = False

    if not st.session_state.authenticated_scoring:
        password = st.text_input("Enter admin password", type="password", key="scoring_password")
        if st.button("Login", key="scoring_login"):
            if password == "dwts2024":  # Same password as admin
                st.session_state.authenticated_scoring = True
                st.rerun()
            else:
                st.error("Incorrect password")
    else:
        st.success("Authenticated")

        if st.button("Logout", key="scoring_logout"):
            st.session_state.authenticated_scoring = False
            st.rerun()

        # Import here to avoid running code before auth
        from pages import scoring_page
        scoring_page.render()

elif page == "Data Export":
    from pages import data_export_page
    data_export_page.render()
