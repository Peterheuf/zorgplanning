import streamlit as st
import pandas as pd
import os

# Functie om data op te slaan
DATA_FILE = "medewerkers.csv"
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Functie om data te laden
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "Naam", "Functie", "Contracturen", "Harde wens", "Zachte wens", 
            "Voorkeursdiensten", "Gemaakte afspraken", "Verantwoordelijke dienst"
        ])

# Laad bestaande medewerkers of maak een nieuwe dataset
if "medewerkers" not in st.session_state:
    st.session_state.medewerkers = load_data()

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
    save_data(st.session_state.medewerkers)
    st.sidebar.success(f"{naam} toegevoegd!")

st.sidebar.write("Huidige medewerkers:")
st.sidebar.dataframe(st.session_state.medewerkers)

# Functie om medewerkers te bewerken
st.header("Bewerk medewerkers")
medewerker_index = st.selectbox("Selecteer medewerker om te bewerken", st.session_state.medewerkers.index.tolist())

if st.button("Bewerken"):
    medewerker = st.session_state.medewerkers.iloc[medewerker_index]
    naam = st.text_input("Naam", medewerker["Naam"])
    functie = st.selectbox("Functie", ["Verpleegkundige", "Verzorgende IG", "EVV", "Helpende", "Anders"], index=["Verpleegkundige", "Verzorgende IG", "EVV", "Helpende", "Anders"].index(medewerker["Functie"]))
    contracturen = st.number_input("Contracturen per week", 0, 40, int(medewerker["Contracturen"]))
    harde_wens = st.text_area("Harde wens", medewerker["Harde wens"])
    zachte_wens = st.text_area("Zachte wens", medewerker["Zachte wens"])
    voorkeursdiensten = st.multiselect("Voorkeursdiensten", ["Ochtend", "Middag", "Avond", "Nacht"], medewerker["Voorkeursdiensten"].split(", "))
    gemaakte_afspraken = st.text_area("Gemaakte afspraken", medewerker["Gemaakte afspraken"])
    verantwoordelijk_dienst = st.checkbox("Bekwaam als verantwoordelijke dienst", medewerker["Verantwoordelijke dienst"])
    
    if st.button("Opslaan"):
        st.session_state.medewerkers.iloc[medewerker_index] = [
            naam, functie, contracturen, harde_wens, zachte_wens, ", ".join(voorkeursdiensten), gemaakte_afspraken, verantwoordelijk_dienst
        ]
        save_data(st.session_state.medewerkers)
        st.success("Medewerker bijgewerkt!")

# Mogelijkheid om medewerkers te importeren via CSV
st.header("Importeer medewerkers")
uploaded_file = st.file_uploader("Upload een CSV-bestand", type=["csv"])
if uploaded_file is not None:
    nieuwe_data = pd.read_csv(uploaded_file)
    st.session_state.medewerkers = pd.concat([st.session_state.medewerkers, nieuwe_data], ignore_index=True)
    save_data(st.session_state.medewerkers)
    st.success("Medewerkers geïmporteerd!")

# Mogelijkheid om medewerkers te exporteren naar CSV
st.header("Exporteer medewerkers")
st.download_button(
    label="Download CSV",
    data=st.session_state.medewerkers.to_csv(index=False).encode("utf-8"),
    file_name="medewerkers_export.csv",
    mime="text/csv"
)

# Toon de medewerkers en hun gegevens
st.header("Overzicht medewerkers")
st.dataframe(st.session_state.medewerkers)
