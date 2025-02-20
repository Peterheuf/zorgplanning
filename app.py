import streamlit as st
import pandas as pd

st.title("Zorginstelling 24-uurs Planningstool")

if "medewerkers" not in st.session_state:
    st.session_state.medewerkers = pd.DataFrame(columns=["Naam", "Contracturen"])

st.sidebar.header("Admin: Beheer Medewerkers")
naam = st.sidebar.text_input("Naam")
contracturen = st.sidebar.number_input("Contracturen per week", 0, 40, 36)

if st.sidebar.button("Medewerker toevoegen"):
    st.session_state.medewerkers = pd.concat(
        [st.session_state.medewerkers, pd.DataFrame([[naam, contracturen]], columns=["Naam", "Contracturen"])], 
        ignore_index=True
    )
    st.sidebar.success(f"{naam} toegevoegd!")

st.sidebar.write("Huidige medewerkers:")
st.sidebar.dataframe(st.session_state.medewerkers)
