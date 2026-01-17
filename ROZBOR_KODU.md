## Rozbor kódu

### 1. Interní Databáze (interni_databaze.py)
#### **Načtení dat**:

```python
BASE_URL = "https://api-web.nhle.com/v1"
SEASON = "20252026"
```
Ukládá základní adresu oficiálního webového rozhraní (API) NHL. Z této adresy bude program stahovat data o zápasech a statistiky hráčů.

---
### 2. API Manager (api_manager.py)

```python
@st.cache_data
def fetch_api(endpoint, params=None):
    try:
        res = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=10)
        return res.json() if res.status_code == 200 else None
    except:
        return None
```
`@st.cache_data` slouží k uloží načtených dat do mezipaměti - nemusíme si znovu stahovat data při překliknutí v aplikaci

`def fetch_api(endpoint, params)` načítá data z API, `endpoint` je "cesta" ke specifických datům, `params` jsou doplňující informace, např. `{"categories": category, "limit": limit}`

`requests.get()` je funkce, pomocí které komunikujeme se serverem NHL, `f"{BASE_URL}/{endpoint}"` = sestavení kompletní adresy, `timeout=10` = server má 10s na odpověd, jinak to program vzdá

`res.json()` převedení stažených dat ze serveru NHL (formát JSON) na struktorovaná data, `res.status_code == 200` 200 = "ok", pokud by byl kod např. 404 -> funkce nám nic nevrátí


#### **Příklad získání dat pro jednotlivé hráče**:

```python
@st.cache_data
def get_leader_stats(player_type, category, conference):
    endpoint = f"{player_type}-stats-leaders/{SEASON}/2"
    limit = 40 if conference else 10
    data = fetch_api(endpoint, {"categories": category, "limit": limit})

    if not data or category not in data: return pd.DataFrame()
```
`{SEASON}/2` 2 = regular season, 3 = playoff, `if not data` - fetch_api() nefungovalo, `category not in data` podmínka pro správný balíček dat, `return pd.DataFrame()` = vrátí se prázdná tabulka

```python
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
```
`rows = []` seznam pro uložení dat, `for p in data[category]` projdeme každáho hráče (`p`), který je v balíku dat a vytáhneme si z klíče `teamAbbrev` za jaký team hraje

`if conference == "Eastern" and abbr not in EAST: continue`, `if conference == "Western" and abbr not in WEST: continue` filtrování hráčů podle toho, v jaké konferenci hrají

`"Player": f"{p['firstName']['default']} {p['lastName']['default']}"` spojení jména a příjmení dohromady (`default` = angličtina), protože API posílá zvlášť jméno a příjmení

`pd.DataFrame(rows)` Pandas nám vytvoří "tabulky" s daty, které jsou uloženy v rows, `.head(10)` = pouze hráče, kteří jsou v top10

---
### 3. UI Config (ui.configs.py)

``` python
main_config = {
    "Player": st.column_config.TextColumn("Player"),
    "Team": st.column_config.ImageColumn("Team", width="small"),
    "Value": st.column_config.NumberColumn("Stat")
}
```
`st.column_config.TextColumn` definuje, že sloupec Player obsahuje text, `st.column_config.ImageColumn` upozorňuje streamlit, že v tomto sloupci budou i obrázky

---
### 4. NHL Dashboard (nhl_dashboard.py)

```python
if view == "Whole League" or view == "Conference":
    conf_name = None
    if view == "Conference":
        conf_name = st.sidebar.selectbox("Select Conference", ["Eastern", "Western"])
        st.header(f"{conf_name} Conference")
    else:
        st.header("League Overview")
```

`st.selectbox(label, options)` zápis defaultní funkce selectbox

```python
 st.subheader("Team standings")
    standings_df = get_team_standings(conf_name)
    st.dataframe(standings_df, column_config=standings_config, hide_index=True, use_container_width=True)
```
`hide_index=True` pro schování indexů, které zobrazuje streamlit, `use_container_width=True` pro roztáhnutí tabulky po celé šírce stránky

```python
s_tabs = st.tabs(["Points", "Goals", "Assists"])
    with s_tabs[0]: st.dataframe(get_leader_stats("skater", "points", conf_name), column_config=main_config, hide_index=True, use_container_width=True)
    with s_tabs[1]: st.dataframe(get_leader_stats("skater", "goals", conf_name), column_config=main_config, hide_index=True, use_container_width=True)
    with s_tabs[2]: st.dataframe(get_leader_stats("skater", "assists", conf_name), column_config=main_config, hide_index=True, use_container_width=True)
```
`st.tabs(["Points", "Goals", "Assists"])` vytvoření jednotlivých záložek pro lepší orientaci

```python
st.subheader("Goalies")
    g_tabs = st.tabs(["Wins", "Save %"])
    with g_tabs[0]: st.dataframe(get_leader_stats("goalie", "wins", conf_name), column_config=main_config, hide_index=True, use_container_width=True)
    with g_tabs[1]: 
        df_save = get_leader_stats("goalie", "savePctg", conf_name)
        if not df_save.empty: df_save['Value'] = df_save['Value'].map(lambda x: f"{(x * 100):.2f}")
        st.dataframe(df_save, column_config=main_config, hide_index=True, use_container_width=True)
```
`df_save['Value'] = df_save['Value'].map(lambda x: f"{(x * 100):.2f}")` -> pro data, které jsou v "df_save", prověd pro každé číslo v tomto sloupci (`.map()`) matematickou operaci,
pro úpravu čísla na dvě desetinné místa

```python
elif view == "Team stats":
    teams_res = fetch_api("standings/now")
    if teams_res:
        team_map = {t['teamName']['default']: t['teamAbbrev']['default'] for t in teams_res['standings']}
        selected_team = st.sidebar.selectbox("Pick Team", list(team_map.keys()))
        abbr = team_map[selected_team]
```

`team_map` 

```python
c1, c2 = st.columns([1, 4])
        with c1: st.image(get_logo_url(abbr), width=120)
        with c2:
            st.header(selected_team)
            h_col1, h_col2, h_col3 = st.columns(3)
            history = TEAM_HISTORY.get(abbr, [0, 0, 0])
            h_col1.metric("Stanley Cups", history[0])
            h_col2.metric("Conference Titles", history[1])
            h_col3.metric("Presidents' Trophies", history[2])
```
`c1, c2 = st.columns([1, 4])` = rozložení stránky na dva sloupce v poměru 1:4, `c1` = sloupec pro logo, `c2` = sloupec pro text
`h_col1, h_col2, h_col3 = st.columns(3)` = rozdělení c2 sloupce na 3 stejné sloupce, vytáhneme si historii teamu ze slovníku pomocí funkce `.get()` a poté si pomocí
funkce `st.metric()` zobrazíme důležitá data, pro nás jsou to vyhrané trofeje jednotluvých teamů
```python
stats = fetch_api(f"club-stats/{abbr}/{SEASON}/2")
        if stats:
            st.write("---")
            st.subheader("Top 3 Team Leaders")
            t_col1, t_col2, t_col3 = st.columns(3)
            skaters_raw = pd.DataFrame(stats.get('skaters', []))
```
`skaters_raw = pd.DataFrame(stats.get('skaters', []))`
