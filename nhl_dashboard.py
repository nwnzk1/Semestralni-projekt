import streamlit as st
import pandas as pd
from interni_databze import SEASON, TEAM_HISTORY, NHL_LOGO_URL
from api_manager import fetch_api, get_logo_url, get_leader_stats, get_team_standings
from ui_configs import main_config, standings_config

st.set_page_config(page_title="NHL Stats Center", layout="wide")
st.logo(NHL_LOGO_URL, size="large")

st.title("NHL Stats Centre")

view = st.sidebar.radio("Navigation", ["Whole League", "Conference", "Team stats"])

if view == "Whole League" or view == "Conference":
    conf_name = None
    if view == "Conference":
        conf_name = st.sidebar.selectbox("Select Conference", ["Eastern", "Western"])
        st.header(f"{conf_name} Conference")
    else:
        st.header("League Overview")

    st.subheader("Team standings")
    standings_df = get_team_standings(conf_name)
    st.dataframe(standings_df, column_config=standings_config, hide_index=True, use_container_width=True)

    st.write("---")
    st.subheader("Players")
    s_tabs = st.tabs(["Points", "Goals", "Assists"])
    with s_tabs[0]: st.dataframe(get_leader_stats("skater", "points", conf_name), column_config=main_config, hide_index=True, use_container_width=True)
    with s_tabs[1]: st.dataframe(get_leader_stats("skater", "goals", conf_name), column_config=main_config, hide_index=True, use_container_width=True)
    with s_tabs[2]: st.dataframe(get_leader_stats("skater", "assists", conf_name), column_config=main_config, hide_index=True, use_container_width=True)

    st.subheader("Goalies")
    g_tabs = st.tabs(["Wins", "Save %"])
    with g_tabs[0]: st.dataframe(get_leader_stats("goalie", "wins", conf_name), column_config=main_config, hide_index=True, use_container_width=True)
    with g_tabs[1]: 
        df_save = get_leader_stats("goalie", "savePctg", conf_name)
        if not df_save.empty: df_save['Value'] = df_save['Value'].map(lambda x: f"{(x * 100):.2f}")
        st.dataframe(df_save, column_config=main_config, hide_index=True, use_container_width=True)

elif view == "Team stats":
    teams_res = fetch_api("standings/now")
    if teams_res:
        team_map = {t['teamName']['default']: t['teamAbbrev']['default'] for t in teams_res['standings']}
        selected_team = st.sidebar.selectbox("Pick Team", list(team_map.keys()))
        abbr = team_map[selected_team]
        
        c1, c2 = st.columns([1, 4])
        with c1: st.image(get_logo_url(abbr), width=120)
        with c2:
            st.header(selected_team)
            h_col1, h_col2, h_col3 = st.columns(3)
            history = TEAM_HISTORY.get(abbr, [0, 0, 0])
            h_col1.metric("Stanley Cups", history[0])
            h_col2.metric("Conference Titles", history[1])
            h_col3.metric("Presidents' Trophies", history[2])

        stats = fetch_api(f"club-stats/{abbr}/{SEASON}/2")
        if stats:
            st.write("---")
            st.subheader("Top 3 Team Leaders")
            t_col1, t_col2, t_col3 = st.columns(3)
            skaters_raw = pd.DataFrame(stats.get('skaters', []))
            
            def fmt_name(row): return f"{row['firstName']['default']} {row['lastName']['default']}"
            if not skaters_raw.empty:
                skaters_raw['FullName'] = skaters_raw.apply(fmt_name, axis=1)

                with t_col1:
                    st.write("**Top 3 Goals**")
                    st.dataframe(skaters_raw.sort_values("goals", ascending=False)[['FullName', 'goals']].head(3), hide_index=True)
                with t_col2:
                    st.write("**Top 3 Assists**")
                    st.dataframe(skaters_raw.sort_values("assists", ascending=False)[['FullName', 'assists']].head(3), hide_index=True)
                with t_col3:
                    st.write("**Top 3 Points**")
                    st.dataframe(skaters_raw.sort_values("points", ascending=False)[['FullName', 'points']].head(3), hide_index=True)

            st.write("---")
            
            st.subheader("Skaters roster")
            if not skaters_raw.empty:
                sk_df = pd.DataFrame([{
                    "Player": f"{p['firstName']['default']} {p['lastName']['default']}",
                    "G": p.get('goals', 0), "A": p.get('assists', 0), "P": p.get('points', 0)
                } for p in stats.get('skaters', [])])
                st.dataframe(sk_df.sort_values("P", ascending=False), hide_index=True, use_container_width=True)

            st.subheader("Goalies roster")
            goalies_raw = pd.DataFrame(stats.get('goalies', []))
            if not goalies_raw.empty:
                gl_df = pd.DataFrame([{
                    "Player": f"{p['firstName']['default']} {p['lastName']['default']}",
                    "Wins": p.get('wins', 0),
                    "Save %": f"{p.get('savePercentage', 0):.3f}"
                } for p in stats.get('goalies', [])])
                st.dataframe(gl_df.sort_values("Wins", ascending=False), hide_index=True, use_container_width=True)






