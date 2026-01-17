import streamlit as st
import requests
import pandas as pd

# 
BASE_URL = "https://api-web.nhle.com/v1"
SEASON = "20252026"  
st.set_page_config(page_title="NHL Stats Center")

# NHL Branding
NHL_LOGO_URL = "https://assets.nhle.com/logos/nhl/svg/NHL_light.svg"
st.logo(NHL_LOGO_URL, size="large")

# Championship History
TEAM_HISTORY = {
    "MTL": [24, 26, 0], "TOR": [13, 0, 0],  "DET": [11, 6, 6], 
    "BOS": [6, 5, 4],   "CHI": [6, 2, 2],   "EDM": [5, 10, 2], 
    "PIT": [5, 6, 1],   "NYR": [4, 4, 4],   "NYI": [4, 6, 0], 
    "NJD": [3, 5, 0],   "COL": [3, 3, 3],   "TBL": [3, 5, 1], 
    "FLA": [2, 4, 1],   "LAK": [2, 3, 0],   "PHI": [2, 8, 0], 
    "DAL": [1, 3, 2],   "STL": [1, 1, 1],   "CAR": [1, 3, 0], 
    "ANA": [1, 2, 0],   "VGK": [1, 2, 0],   "WSH": [1, 2, 3],
    "VAN": [0, 3, 2],   "BUF": [0, 2, 1],   "OTT": [0, 1, 1],
    "SJS": [0, 1, 1],   "NSH": [0, 1, 1],   "WPG": [0, 0, 1],
    "CGY": [1, 3, 2]
}

# Conference Mapping
EAST = ["BOS", "BUF", "DET", "FLA", "MTL", "OTT", "TBL", "TOR", "CAR", "CBJ", "NJD", "NYI", "NYR", "PHI", "PIT", "WSH"]
WEST = ["CHI", "COL", "DAL", "MIN", "NSH", "STL", "WPG", "UTA", "ANA", "CGY", "EDM", "LAK", "SEA", "SJS", "VAN", "VGK"]

# 
def get_logo_url(abbr):
    return f"https://assets.nhle.com/logos/nhl/svg/{abbr}_light.svg"

@st.cache_data
def fetch_api(endpoint, params=None):
    try:
        res = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        return res.json() if res.status_code == 200 else None
    except: return None

@st.cache_data
def get_leader_stats(player_type="skater", category="points", conference=None):
    endpoint = f"{player_type}-stats-leaders/{SEASON}/2"
    limit = 40 if conference else 10
    data = fetch_api(endpoint, {"categories": category, "limit": limit})
    
    if not data or category not in data: return pd.DataFrame()
    
    rows = []
    for p in data[category]:
        abbr = p['teamAbbrev']
        if conference == "Eastern" and abbr not in EAST: continue
        if conference == "Western" and abbr not in WEST: continue
        
        rows.append({
            "Player": f"{p['firstName']['default']} {p['lastName']['default']}",
            "Team": get_logo_url(abbr),
            "Value": p['value']
        })
    return pd.DataFrame(rows).head(10)

@st.cache_data
def get_team_standings(conference=None):
    data = fetch_api("standings/now")
    if not data or 'standings' not in data: return pd.DataFrame()
    
    rows = []
    for t in data['standings']:
        abbr = t['teamAbbrev']['default']
        if conference == "Eastern" and abbr not in EAST: continue
        if conference == "Western" and abbr not in WEST: continue
        
        rows.append({
            "Team": get_logo_url(abbr),
            "Team Name": t['teamName']['default'],
            "Points": t['points'],
            "GP": t['gamesPlayed']
        })
    df = pd.DataFrame(rows).sort_values(by="Points", ascending=False)
    return df

# UI LAYOUT
st.title("NHL Stats Centre")

# SIDEBAR NAVIGATION
view = st.sidebar.radio("Navigation", ["Whole League", "Conference", "Team stats"])

# TABLE CONFIGURATIONS
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
        if not df_save.empty: df_save['Value'] = df_save['Value'].map(lambda x: f"{x:.3f}")
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


