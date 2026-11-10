import os

import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Portfolio Tracker", layout="wide")
st.title("Portfolio Tracker")
st.caption(
    "ETF monde (DCA) + sélection thématique d'actions. "
    "Valeurs en USD. Données de démonstration si aucun fichier personnel n'est présent."
)

REAL_FILE = "data/positions.csv"
DEMO_FILE = "data/positions_demo.csv"


@st.cache_data(ttl=900)
def get_price(ticker: str) -> float:
    try:
        hist = yf.Ticker(ticker).history(period="5d")
        return float(hist["Close"].iloc[-1])
    except Exception:
        return float("nan")


path = REAL_FILE if os.path.exists(REAL_FILE) else DEMO_FILE
df = pd.read_csv(path)

df["prix_actuel"] = df["ticker"].map(get_price)
df["valeur"] = df["quantite"] * df["prix_actuel"]
df["cout"] = df["quantite"] * df["prix_achat"]
df["perf_%"] = (df["valeur"] / df["cout"] - 1) * 100

total_valeur = df["valeur"].sum()
total_cout = df["cout"].sum()
perf_totale = (total_valeur / total_cout - 1) * 100

c1, c2, c3 = st.columns(3)
c1.metric("Valeur totale", f"{total_valeur:,.0f} $")
c2.metric("Coût total", f"{total_cout:,.0f} $")
c3.metric("Performance totale", f"{perf_totale:+.1f} %")

st.subheader("Positions")
st.dataframe(
    df[["ticker", "nom", "type", "quantite", "prix_achat", "prix_actuel", "valeur", "perf_%"]]
    .round(2)
    .sort_values("valeur", ascending=False),
    use_container_width=True,
    hide_index=True,
)

left, right = st.columns(2)
with left:
    st.subheader("Répartition par ligne")
    st.plotly_chart(px.pie(df, names="ticker", values="valeur"), use_container_width=True)
with right:
    st.subheader("Répartition ETF vs actions")
    by_type = df.groupby("type", as_index=False)["valeur"].sum()
    st.plotly_chart(px.pie(by_type, names="type", values="valeur"), use_container_width=True)
