import pandas as pd
import streamlit as st


@st.cache_data
def load_data(path: str = "data/clean/dataset.csv") -> pd.DataFrame:
    """Lê e armazena em cache o dataset já tratado."""
    df = pd.read_csv(path)
    if "total_goals" not in df.columns:
        df["total_goals"] = df["home_team_goal"] + df["away_team_goal"]
    if "match_result" not in df.columns:
        df["match_result"] = "Empate"
        df.loc[df["home_team_goal"] > df["away_team_goal"], "match_result"] = "Vitória Mandante"
        df.loc[df["home_team_goal"] < df["away_team_goal"], "match_result"] = "Vitória Visitante"
    return df

