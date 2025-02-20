import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px
import random

# Functie om data op te slaan
DATA_FILE = "medewerkers.csv"
PLANNING_FILE = "planning.csv"
ZIEKE_MEDEWERKERS_FILE = "zieke_medewerkers.csv"

def save_data(df, filename):
    df.to_csv(filename, index=False)

# Functie om data te laden
def load_data(filename, columns):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=columns)

# Laad medewerkers en planning
if "medewerkers" not in st.session_state:
    st.session_state.medewerkers = load_data(DATA_FILE, [
        "Naam", "Functie", "Contracturen", "Harde wens", "Zachte wens", 
        "Voorkeursdiensten", "Gemaakte afspraken", "Verantwoordelijke dienst"
    ])

if "planning" not in st.session_state:
    st.session_state.planning = load_data(PLANNING_FILE, [
        "Datum", "Dienst", "Medewerker", "Status"
    ])

if "zieke_medewerkers" not in st.session_state:
    st.session_state.zieke_medewerkers = load_data(ZIEKE_MEDEWERKERS_FILE, ["Naam", "Ziek vanaf", "Ziek tot"])

st.title("Zorginstelling 24-uurs Planningstool")

# Sidebar voor maandselectie
st.sidebar.header("Planning genereren")
maand_selectie = st.sidebar.selectbox("Selecteer maand", ["Januari", "Februari", "Maart", "April", "Mei", "Juni", "Juli", "Augustus", "September", "Oktober", "November", "December"])

# Functie om een planning te genereren
def genereer_planning(maand):
    startdatum = datetime(datetime.today().year, maand, 1)
    einddatum = startdatum + timedelta(days=30)
    diensten = {"Ochtend": 4, "Middag": 6, "Avond": 8, "Nacht": 8}
    planning = []
    medewerkers = st.session_state.medewerkers.copy()
    medewerkers["Uren_ingeroosterd"] = 0
    
    for dag in range((einddatum - startdatum).days):
        datum = (startdatum + timedelta(days=dag)).strftime("%Y-%m-%d")
        for dienst, uren in diensten.items():
            beschikbare_medewerkers = medewerkers[(medewerkers["Uren_ingeroosterd"] + uren <= medewerkers["Contracturen"]) & ~medewerkers["Naam"].isin(st.session_state.zieke_medewerkers["Naam"])]
            if not beschikbare_medewerkers.empty:
                medewerker = beschikbare_medewerkers.sample(1).iloc[0]
                medewerkers.loc[medewerkers["Naam"] == medewerker["Naam"], "Uren_ingeroosterd"] += uren
                planning.append([datum, dienst, medewerker["Naam"], "Ingevuld"])
            else:
                planning.append([datum, dienst, "", "Open"])
    
    return pd.DataFrame(planning, columns=["Datum", "Dienst", "Medewerker", "Status"])

if st.sidebar.button("Genereer planning voor " + maand_selectie):
    maand_nummer = datetime.strptime(maand_selectie, "%B").month
    st.session_state.planning = genereer_planning(maand_nummer)
    save_data(st.session_state.planning, PLANNING_FILE)
    st.sidebar.success(f"Planning voor {maand_selectie} gegenereerd!")

# Functie om een medewerker ziek te melden
st.sidebar.header("Ziekmelding")
ziek_medewerker = st.sidebar.selectbox("Selecteer medewerker", st.session_state.medewerkers["Naam"].tolist())
ziek_vanaf = st.sidebar.date_input("Ziek vanaf")
ziek_tot = st.sidebar.date_input("Ziek tot")
if st.sidebar.button("Medewerker ziek melden"):
    nieuwe_ziekmelding = pd.DataFrame([[ziek_medewerker, ziek_vanaf, ziek_tot]], columns=["Naam", "Ziek vanaf", "Ziek tot"])
    st.session_state.zieke_medewerkers = pd.concat([st.session_state.zieke_medewerkers, nieuwe_ziekmelding], ignore_index=True)
    save_data(st.session_state.zieke_medewerkers, ZIEKE_MEDEWERKERS_FILE)
    st.sidebar.success(f"{ziek_medewerker} is ziek gemeld!")

st.header("Planningsoverzicht")
st.selectbox("Weergave", ["Dag", "Week", "Maand"], key="view_option")
kleuren = {"Ingevuld": "#90EE90", "Open": "#FF6347"}
st.session_state.planning["Kleur"] = st.session_state.planning["Status"].map(kleuren)
fig = px.timeline(st.session_state.planning, x_start="Datum", x_end="Datum", y="Medewerker", color="Status", color_discrete_map=kleuren, title="Roosteroverzicht")
st.plotly_chart(fig)

st.header("Exporteer planning")
st.download_button(
    label="Download Planning CSV",
    data=st.session_state.planning.to_csv(index=False).encode("utf-8"),
    file_name="planning_export.csv",
    mime="text/csv"
)
