import streamlit as st
import pandas as pd

# Initialiseer de medewerkers-database
if "medewerkers" not in st.session_state:
    st.session_state.medewerkers = pd.DataFrame(columns=[
        "Naam", "Functie", "Contracturen", "Harde wens", "Zachte wens", 
        "Voorkeursdiensten", "Gemaakte afspraken", "Verantwoordelijke dienst"
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

# Zorg ervoor dat 'verantwoordelijk_dienst' altijd een waarde heeft
verantwoordelijk_dienst = st.sidebar.checkbox("Bekwaam als verantwoordelijke dienst", value=False)

if st.sidebar.button("Medewerker toevoegen"):
    nieuwe_medewerker = pd.DataFrame([[
        naam, functie, contracturen, harde_wens, zachte_wens, voorkeursdiensten, 
        gemaakte_afspraken, verantwoordelijk_dienst
    ]], columns=st.session_state.medewerkers.columns)
    
    st.session_state.medewerkers = pd.concat([st.session_state.medewerkers, nieuwe_medewerker], ignore_index=True)
    st.sidebar.success(f"{naam} toegevoegd!")

st.sidebar.write("Huidige medewerkers:")
st.sidebar.dataframe(st.session_state.medewerkers)

# Toon de medewerkers en hun gegevens
st.header("Overzicht medewerkers")
st.dataframe(st.session_state.medewerkers)
