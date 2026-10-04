import streamlit as st

import fake_gemma as gemma

st.set_page_config(page_title="NOTE-IT", page_icon="🧠", layout="centered")

with st.sidebar:
    st.title("NOTE-IT")
    st.caption("Messy psychology notes in, study-ready notes out. Runs locally on Gemma.")

    notes = st.text_area("Paste your notes", height=250)
    uploaded = st.file_uploader("…or upload a file", type=["txt", "md"])
    if uploaded is not None:
        notes = uploaded.read().decode("utf-8")

    generate = st.button("Generate", type="primary", width="stretch")

    if generate and notes.strip() == "":
        st.warning("Paste or upload some notes first.")

st.caption("Paste or upload your notes in the sidebar, then click Generate.")
