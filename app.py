import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Functie om data op te slaan
DATA_FILE = "medewerkers.csv"
PLANNING_FILE = "planning.csv"

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

st.title("Zorginstelling 24-uurs Planningstool")

# Sidebar voor medewerkersbeheer
st.sidebar.header("Admin: Beheer Medewerkers")
naam = st.sidebar.text_input("Naam")
functie = st.sidebar.selectbox("Functie", ["Verpleegkundige", "Verzorgende IG", "EVV", "Helpende", "Anders"])
contracturen = st.sidebar.number_input("Contracturen per week", 0, 40, 36)
harde_wens = st.sidebar.text_area("Harde wens (bv. nooit nachtdiensten)")
zachte_wens = st.sidebar.text_area("Zachte wens (bv. liever avonddiensten)")
voorkeursdiensten = st.sidebar.multiselect("Voorkeursdiensten", ["Ochtend", "Middag", "Avond", "Nacht"])
gemaakte_afspraken = st.sidebar.text_area("Gemaakte afspraken (bv. woensdag alleen ochtend)")
verantwoordelijk_dienst = st.sidebar.checkbox("Bekwaam als verantwoordelijke dienst", value=False)

if st.sidebar.button("Medewerker toevoegen"):
    nieuwe_medewerker = pd.DataFrame([[
        naam, functie, contracturen, harde_wens, zachte_wens, ", ".join(voorkeursdiensten), gemaakte_afspraken, verantwoordelijk_dienst
    ]], columns=st.session_state.medewerkers.columns)
    
    st.session_state.medewerkers = pd.concat([st.session_state.medewerkers, nieuwe_medewerker], ignore_index=True)
    save_data(st.session_state.medewerkers, DATA_FILE)
    st.sidebar.success(f"{naam} toegevoegd!")

st.sidebar.write("Huidige medewerkers:")
st.sidebar.dataframe(st.session_state.medewerkers)

# Functie om een basisrooster te genereren
def genereer_planning():
    startdatum = datetime.today()
    einddatum = startdatum + timedelta(days=30)
    diensten = ["Ochtend", "Middag", "Avond", "Nacht"]
    planning = []
    
    for dag in range((einddatum - startdatum).days):
        datum = (startdatum + timedelta(days=dag)).strftime("%Y-%m-%d")
        for dienst in diensten:
            planning.append([datum, dienst, "", "Concept"])
    
    return pd.DataFrame(planning, columns=["Datum", "Dienst", "Medewerker", "Status"])

if st.sidebar.button("Genereer planning"):
    st.session_state.planning = genereer_planning()
    save_data(st.session_state.planning, PLANNING_FILE)
    st.sidebar.success("Conceptplanning gegenereerd!")

st.header("Planningsoverzicht")
st.dataframe(st.session_state.planning)

# Medewerkers kunnen zich inschrijven voor open diensten
st.header("Beschikbare diensten")
open_diensten = st.session_state.planning[st.session_state.planning["Medewerker"] == ""]
if not open_diensten.empty:
    for index, row in open_diensten.iterrows():
        if st.button(f"Inschrijven voor {row['Dienst']} op {row['Datum']}"):
            st.session_state.planning.at[index, "Medewerker"] = st.session_state.get("gebruikersnaam", "Onbekend")
            st.session_state.planning.at[index, "Status"] = "Ingevuld"
            save_data(st.session_state.planning, PLANNING_FILE)
            st.success("Je hebt je ingeschreven voor deze dienst!")

# Medewerkers kunnen hun planning inzien
st.header("Mijn Planning")
gebruikersnaam = st.text_input("Vul je naam in om je planning te bekijken")
mijn_planning = st.session_state.planning[st.session_state.planning["Medewerker"] == gebruikersnaam]
st.dataframe(mijn_planning)

# Exporteren van de planning
st.header("Exporteer planning")
st.download_button(
    label="Download Planning CSV",
    data=st.session_state.planning.to_csv(index=False).encode("utf-8"),
    file_name="planning_export.csv",
    mime="text/csv"
)
