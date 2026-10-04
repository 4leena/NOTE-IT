import streamlit as st

import fake_gemma as gemma

st.set_page_config(page_title="NOTE-IT", layout="wide")

st.title("NOTE-IT")
st.caption("Messy psychology notes in, study-ready notes out. Runs locally on Gemma.")

left, right = st.columns([1, 2])

with left:
    notes = st.text_area("Paste your notes:", height=300)
    generate = st.button("Generate", type="primary")

    if generate and notes.strip() == "":
        st.warning("Paste some notes first.")

with right:
    st.info("← Paste notes and click Generate to get started.")
