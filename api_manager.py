import requests
import streamlit as st
import pandas as pd
from interni_databze import BASE_URL, SEASON, EAST, WEST

@st.cache_data
def fetch_api(endpoint, params=None):
    try:
        res = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        return res.json() if res.status_code == 200 else None
    except: return None

def get_logo_url(abbr):
    return f"https://assets.nhle.com/logos/nhl/svg/{abbr}_light.svg"

@st.cache_data
def get_leader_stats(player_type, category, conference):
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
