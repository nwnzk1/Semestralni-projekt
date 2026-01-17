import streamlit as st

main_config = {
    "Player": st.column_config.TextColumn("Player"),
    "Team": st.column_config.ImageColumn("Team", width="small"),
    "Value": st.column_config.NumberColumn("Stat")
}

standings_config = {
    "Team": st.column_config.ImageColumn("Logo", width="small"),
    "Team Name": st.column_config.TextColumn("Team"),
    "Points": st.column_config.NumberColumn("Points"),
    "GP": st.column_config.NumberColumn("Games Played")
}
