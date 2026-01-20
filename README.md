# 🏒 NHL Stats Center

Tento projekt je interaktivní webová aplikace postavená na frameworku **Streamlit**, která slouží k přehledné vizualizaci dat hokejové ligy NHL. 
Aplikace využívá oficiální **NHL API** pro získávání statistik a kombinuje je s interní databází historických úspěchů týmů.

---
## Klíčové funkce
1. Živé statistiky: Aktuální data přímo z NHL API. 
2. Interaktivní filtry: Možnost filtrování podle konferencí a jednotlivých teamů.
3. Přehled jednotlivých teamů: Aktuální soupiska, historie trofejí

---
## 📚 Použité knihovny:
🔹[Streamlit](https://streamlit.io/)

🔹[Pandas](https://pandas.pydata.org/)

🔹[Requests](https://pypi.org/project/requests/)

---
## Struktura projektu:
Semestralni-projekt/
├── .devcontainer/           # Konfigurace pro vývoj v Dockeru/Codespaces
├── README.md                # Hlavní dokumentace projektu (popis, instalace)
├── ROZBOR_KODU.md           # Podrobný technický popis fungování kódu
├── nhl_dashboard.py         # Hlavní spouštěcí soubor aplikace (Streamlit)
├── api_manager.py           # Logika pro komunikaci s oficiálním NHL API
├── interni_databze.py       # Soubor obsahující statická data (např. historie trofejí)
└── ui_configs.py            # Konfigurace vzhledu a prvků uživatelského rozhraní

---
## Spuštění projektu:

Projekt je hostován na community cloudu přímo od Streamlitu:
[NHL Stats Center](https://nhlstatscenter.streamlit.app//)

Lokální spuštění projektu:

1.  **Instalace potřebných knihoven**:
    ```bash
    pip install streamlit requests pandas
    ```

2.  **Spuštění aplikace**: 
    ```bash
    py -m streamlit run nhl_dashboard.py
    ```
    ```bash
    python -m streamlit run nhl_dashboard.py
    ```
    ```bash
    streamlit run nhl_dashboard.py
    ```
