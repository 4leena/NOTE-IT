from datetime import date

import streamlit as st

import fake_gemma as gemma

st.set_page_config(page_title="NOTE-IT", layout="centered")


def show_notes(result):
    terms = result.get("Key Terms", [])
    if terms:
        st.subheader("Key Terms")
        for item in terms:
            st.markdown(f"**{item['term']}** — {item['definition']}")

    theories = result.get("Theories & Researchers", [])
    if theories:
        st.subheader("Theories & Researchers")
        for item in theories:
            st.markdown(f"**{item['name']}**  \n{item['summary']}")

    studies = result.get("Key Studies", [])
    if studies:
        st.subheader("Key Studies")
        for item in studies:
            with st.container(border=True):
                st.markdown(f"**{item['study']}**")
                st.markdown(f"*Method:* {item['method']}")
                st.markdown(f"*Findings:* {item['findings']}")

    evaluation = result.get("Evaluation", [])
    if evaluation:
        st.subheader("Evaluation")
        st.markdown("\n".join(f"- {point}" for point in evaluation))

    examples = result.get("Real-World Examples", [])
    if examples:
        st.subheader("Real-World Examples")
        for example in examples:
            st.markdown("> " + example)

    quiz = result.get("Quiz Yourself", [])
    if quiz:
        st.subheader("Quiz Yourself")
        for item in quiz:
            with st.expander(item["q"]):
                st.write(item["a"])


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
    elif generate:
        with st.spinner("Organizing your notes…"):
            st.session_state["notes"] = notes
            st.session_state["result"] = gemma.rewrite_notes(notes)
            st.session_state["diagram"] = gemma.make_diagram(st.session_state["result"])

if "result" in st.session_state:
    result = st.session_state["result"]
    today = date.today()
    st.title(result.get("Topic", "Study Notes"))
    st.caption(f"Psychology · {today:%b} {today.day}")

    notes_tab, diagram_tab, buddy_tab = st.tabs(["Notes", "Diagram", "Study Buddy"])
    with notes_tab:
        show_notes(result)
    with diagram_tab:
        st.code(st.session_state["diagram"])
    with buddy_tab:
        st.caption("Study Buddy is coming soon.")
else:
    st.caption("Paste or upload your notes in the sidebar, then click Generate.")
