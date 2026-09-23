import streamlit as st
import json
from pathlib import Path

def render():
    """Render the data export page."""

    st.subheader("📥 Data Export/Import")

    st.info("Use this page to backup or restore your data. Download the JSON files before making code changes!")

    data_dir = Path(__file__).parent.parent / "data"

    # Export section
    st.header("Export Data")
    st.write("Download the current data files to save your progress:")

    for filename in ['players.json', 'dwts_teams.json', 'player_picks.json', 'weekly_scores.json']:
        filepath = data_dir / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = f.read()

            st.download_button(
                label=f"📥 Download {filename}",
                data=data,
                file_name=filename,
                mime="application/json",
                key=f"download_{filename}"
            )
        else:
            st.warning(f"{filename} not found")

    st.divider()

    # Import section
    st.header("Import Data")
    st.warning("⚠️ Warning: Uploading files will REPLACE the current data!")

    uploaded_file = st.file_uploader(
        "Upload a JSON data file",
        type=['json'],
        help="Upload a previously downloaded JSON file to restore data"
    )

    if uploaded_file:
        st.write(f"**File:** {uploaded_file.name}")

        # Show preview
        try:
            data = json.loads(uploaded_file.getvalue())
            st.write(f"**Records:** {len(data) if isinstance(data, list) else 'N/A'}")

            with st.expander("Preview data"):
                st.json(data)

            if st.button(f"Replace {uploaded_file.name}", type="primary"):
                # Save the file
                filepath = data_dir / uploaded_file.name
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                st.success(f"✅ {uploaded_file.name} has been updated!")
                st.rerun()

        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.divider()

    # Show current data stats
    st.header("Current Data Summary")

    try:
        with open(data_dir / 'players.json', 'r') as f:
            players = json.load(f)
        with open(data_dir / 'dwts_teams.json', 'r') as f:
            teams = json.load(f)
        with open(data_dir / 'player_picks.json', 'r') as f:
            picks = json.load(f)
        with open(data_dir / 'weekly_scores.json', 'r') as f:
            scores = json.load(f)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Players", len(players))
        with col2:
            st.metric("Teams", len(teams))
        with col3:
            st.metric("Picks", len(picks))
        with col4:
            st.metric("Scores", len(scores))

    except Exception as e:
        st.error(f"Error reading data: {e}")
