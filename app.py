import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import fake_gemma as gemma

st.set_page_config(page_title="NOTE-IT", layout="wide")

MODES = {
    "Tutor": ("tutor", ":material/school:", "I'll explain your notes step by step."),
    "Peer": ("peer", ":material/group:", "Ask me anything. I'll keep it simple."),
    "Examiner": ("examiner", ":material/fact_check:", "I'll quiz you on your notes and mark your answers."),
}

BUDDY_CSS = """
<style>
.st-key-buddy {
  background: #FBF5EC;
  border: 1px solid #EAD8BF;
  border-radius: 14px;
  padding-bottom: 12px;
  overflow: hidden;
}
.st-key-buddy_header {
  background: #F3E2CB;
  border-bottom: 1px solid #EAD8BF;
  padding: 12px 16px;
}
.st-key-buddy_body {
  padding: 0 14px;
}
.st-key-buddy [class*="st-key-mode_"] button {
  border-radius: 999px;
  background: #FFFFFF;
  border: 1px solid #EAD8BF;
  padding: 4px 6px;
  gap: 4px;
  white-space: nowrap;
}
.st-key-buddy [data-testid="stChatMessage"] {
  background: transparent;
}
.st-key-buddy [data-testid="stChatMessageContent"] {
  flex: 0 1 auto;
  max-width: 85%;
  padding: 8px 14px;
}
.st-key-buddy [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  flex-direction: row-reverse;
}
.st-key-buddy [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  background: #E7BE8A;
  border-radius: 16px 16px 4px 16px;
}
.st-key-buddy [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
  background: #FFFFFF;
  border: 1px solid #EAD8BF;
  border-radius: 16px 16px 16px 4px;
}
.st-key-buddy [data-testid="stChatInput"],
.st-key-buddy [data-testid="stChatInput"] > div {
  border-radius: 999px;
}
</style>
"""

EMPTY_STATE = """
<div style="text-align:center; padding:56px 12px; color:#3B2F25;">
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#8C5E2A" stroke-width="1.5" stroke-linejoin="round">
    <path d="M12 3l2.2 6.8L21 12l-6.8 2.2L12 21l-2.2-6.8L3 12l6.8-2.2z"/>
  </svg>
  <div style="font-size:1.2rem; font-weight:600; margin-top:12px;">TITLE</div>
  <div style="opacity:0.7; margin-top:4px;">SUBTITLE</div>
</div>
"""

CHEERS = [
    "You've got this, girl.",
    "One page at a time. You're doing great.",
    "Look at you, showing up again.",
    "Small steps still count.",
    "Future you is already proud of you.",
    "You understand more than you think.",
    "Consistency beats cramming. Keep going.",
    "Take a breath. You're learning, not racing.",
]

PAGE_CSS = """
<style>
.st-key-app_header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  z-index: 999995;
  background: #F3E2CB;
  border-bottom: 1px solid #EAD8BF;
  padding: 0 32px;
  justify-content: center;
}
.st-key-app_header [data-testid="stHorizontalBlock"] {
  align-items: center;
}
.st-key-app_header [data-testid="stColumn"]:last-child [data-testid="stVerticalBlock"] {
  align-items: flex-end;
}
.st-key-app_header [data-testid="stMarkdownContainer"],
.st-key-app_footer [data-testid="stCaptionContainer"] {
  margin-bottom: 0 !important;
}
.st-key-app_header h3 {
  padding: 0 !important;
  margin: 0 !important;
  letter-spacing: 0.04em;
}
.st-key-app_footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 48px;
  z-index: 999995;
  background: #F3E2CB;
  border-top: 1px solid #EAD8BF;
  justify-content: center;
  align-items: center;
  text-align: center;
}
.st-key-app_footer p {
  font-size: 0.95rem;
  color: #3B2F25;
  margin: 0 !important;
  text-align: center;
}
[data-testid="stHeader"] {
  top: 64px;
  background: transparent;
}
[data-testid="stSidebar"] {
  top: 64px;
  height: calc(100vh - 112px);
}
[data-testid="stMainBlockContainer"] {
  padding-top: calc(64px + 2rem);
  padding-bottom: calc(48px + 2rem);
}
</style>
"""

SAVE_DIR = Path("saved_notes")
SAVED_KEYS = ["notes", "result", "diagram", "history"]
DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
HEAT_COLORS = ["#EFE8DE", "#F3E2CB", "#E7BE8A", "#C9955A", "#8C5E2A"]
WEEKS_SHOWN = 26
CELL = 24

LEGEND = (
    "<div style='display:flex; gap:6px; align-items:center; justify-content:center; font-size:0.85rem;'>Less "
    + "".join(
        f"<span style='width:14px; height:14px; border-radius:3px; background:{color}; display:inline-block;'></span>"
        for color in HEAT_COLORS
    )
    + " More</div>"
)

LAYOUTS = {"Top to bottom": "TD", "Left to right": "LR"}

MERMAID_HTML = """
<div id="diagram"></div>
<pre id="fallback" style="display:none; white-space:pre-wrap"></pre>
<script src="/app/static/mermaid.min.js"></script>
<script>
const code = DIAGRAM_CODE;
function showFallback() {
  const box = document.getElementById("fallback");
  box.textContent = "Couldn't draw this diagram. Here is the code instead:\\n\\n" + code;
  box.style.display = "block";
}
if (typeof mermaid === "undefined") {
  showFallback();
} else {
  mermaid.initialize({
    startOnLoad: false,
    theme: "base",
    themeVariables: {
      primaryColor: "#F8EFE3",
      primaryBorderColor: "#8C5E2A",
      primaryTextColor: "#3B2F25",
      lineColor: "#8C5E2A",
      fontFamily: "-apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"
    }
  });
  mermaid.render("graph", code)
    .then(({ svg }) => { document.getElementById("diagram").innerHTML = svg; })
    .catch(showFallback);
}
</script>
"""


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


def set_direction(code, direction):
    return re.sub(r"^(flowchart|graph)\s+\w+", rf"\1 {direction}", code, count=1)


def show_diagram(code):
    safe = json.dumps(code).replace("</", "<\\/")
    st.iframe(MERMAID_HTML.replace("DIAGRAM_CODE", safe), height=450)
    with st.expander("Edit as code (advanced)"):
        st.caption("Change the text and press Ctrl+Enter (Cmd+Enter on Mac) to redraw.")
        st.text_area("Mermaid code", key="diagram", height=200, label_visibility="collapsed")


def show_header():
    with st.container(key="app_header"):
        left, right = st.columns([5, 1], vertical_alignment="center")
        left.markdown("### NOTE-IT")
        if right.button("Calendar", icon=":material/calendar_month:"):
            show_calendar()


def save_session():
    SAVE_DIR.mkdir(exist_ok=True)
    name = st.session_state.setdefault("session_file", datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".json")
    data = {key: st.session_state[key] for key in SAVED_KEYS}
    (SAVE_DIR / name).write_text(json.dumps(data, indent=2))


def open_requested_session():
    name = st.session_state.pop("open_file", None)
    if name is None:
        return
    data = json.loads((SAVE_DIR / name).read_text())
    for key in SAVED_KEYS:
        st.session_state[key] = data[key]
    st.session_state["session_file"] = name


def sessions_by_day():
    days = {}
    for path in sorted(SAVE_DIR.glob("*.json")):
        days.setdefault(path.stem[:10], []).append(path)
    return days


def heatmap(days):
    today = date.today()
    start = today - timedelta(days=(today.weekday() + 1) % 7 + 7 * (WEEKS_SHOWN - 1))
    rows = []
    for i in range((today - start).days + 1):
        day = start + timedelta(days=i)
        count = len(days.get(day.isoformat(), []))
        rows.append({
            "date": day.isoformat(),
            "week": (start + timedelta(weeks=i // 7)).isoformat(),
            "weekday": DAY_NAMES[i % 7],
            "level": min(count, 4),
            "sessions": count,
        })
    month_label = "utcdate(toDate(datum.value)) <= 7 ? utcFormat(toDate(datum.value), '%b') : ''"
    return (
        alt.Chart(pd.DataFrame(rows))
        .mark_rect(cornerRadius=3, stroke="#FFFCF7", strokeWidth=3)
        .encode(
            x=alt.X("week:O", title=None, axis=alt.Axis(orient="top", labelExpr=month_label, labelAngle=0, ticks=False, domain=False)),
            y=alt.Y("weekday:O", sort=DAY_NAMES, title=None, axis=alt.Axis(ticks=False, domain=False)),
            color=alt.Color("level:O", scale=alt.Scale(domain=[0, 1, 2, 3, 4], range=HEAT_COLORS), legend=None),
            tooltip=[alt.Tooltip("date:N", title="Date"), alt.Tooltip("sessions:Q", title="Sessions")],
        )
        .add_params(alt.selection_point(name="day", fields=["date"]))
        .properties(width=WEEKS_SHOWN * CELL, height=7 * CELL)
    )


@st.dialog("Your study calendar", width="large")
def show_calendar():
    days = sessions_by_day()
    plural = "day" if len(days) == 1 else "days"
    st.caption(f"{len(days)} study {plural} so far. Click a coloured square to open those notes.")
    event = st.altair_chart(heatmap(days), on_select="rerun", key="heatmap", width="content")
    st.html(LEGEND)
    picked = event.selection.get("day", [])
    if not picked:
        return
    sessions = days.get(picked[0]["date"], [])
    if not sessions:
        st.caption("No notes on this day.")
    for path in sessions:
        data = json.loads(path.read_text())
        started = datetime.strptime(path.stem, "%Y-%m-%d_%H%M%S")
        label = f"{started:%I:%M %p}".lstrip("0") + " · " + data["result"].get("Topic", "Study Notes")
        if st.button(label, key=f"open_{path.stem}", width="stretch"):
            st.session_state["open_file"] = path.name
            st.rerun()


def show_footer():
    cheer = CHEERS[date.today().toordinal() % len(CHEERS)]
    with st.container(key="app_footer"):
        st.caption(cheer)


def empty_state(title, subtitle):
    st.html(EMPTY_STATE.replace("SUBTITLE", subtitle).replace("TITLE", title))


def show_mode_buttons(current):
    columns = st.columns(len(MODES), gap="small")
    for column, (label, (value, icon, _)) in zip(columns, MODES.items()):
        if column.button(label, icon=icon, key=f"mode_{value}", width="stretch"):
            st.session_state["mode"] = label
            st.rerun()
    selected = MODES[current][0]
    st.html(
        f"<style>.st-key-mode_{selected} button {{"
        "background: #E7BE8A !important; border-color: #8C5E2A !important; }</style>"
    )


def show_buddy():
    st.html(BUDDY_CSS)
    with st.container(key="buddy"):
        with st.container(key="buddy_header"):
            st.markdown("**:material/auto_awesome: Study Buddy**")

        with st.container(key="buddy_body"):
            if "result" not in st.session_state:
                empty_state("Your Study Buddy", "Generate your notes first, then ask questions here.")
                return

            mode = st.session_state.setdefault("mode", "Tutor")
            history = st.session_state.setdefault("history", [])

            messages = st.container(height=420, border=False)
            with messages:
                if not history:
                    empty_state("How can I help you today?", MODES[mode][2])
                for msg in history:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

            show_mode_buttons(mode)
            question = st.chat_input("Type your message…")

        if question:
            with messages:
                with st.chat_message("user"):
                    st.markdown(question)
                with st.spinner("Thinking…"):
                    try:
                        reply = gemma.chat(history, st.session_state["notes"], question, MODES[mode][0])
                    except gemma.GemmaError as error:
                        st.error(str(error))
                        return
                with st.chat_message("assistant"):
                    st.markdown(reply)
            history.append({"role": "user", "content": question})
            history.append({"role": "assistant", "content": reply})
            save_session()


open_requested_session()

with st.sidebar:
    st.caption("Paste your messy notes and get study-ready notes back.")

    notes = st.text_area("Paste your notes", height=250)
    uploaded = st.file_uploader("…or upload a file", type=["txt", "md"])
    if uploaded is not None:
        notes = uploaded.read().decode("utf-8")

    generate = st.button("Generate", type="primary", width="stretch")

    if generate and notes.strip() == "":
        st.warning("Paste or upload some notes first.")
    elif generate:
        try:
            with st.spinner("Organizing your notes…"):
                result = gemma.rewrite_notes(notes)
                diagram = gemma.make_diagram(result)
        except gemma.GemmaError as error:
            st.error(str(error))
        else:
            st.session_state["notes"] = notes
            st.session_state["result"] = result
            st.session_state["diagram"] = diagram
            st.session_state["history"] = []
            st.session_state.pop("session_file", None)
            save_session()

st.html(PAGE_CSS)
show_header()

notes_col, buddy_col = st.columns([3, 2], gap="large")

with notes_col:
    if "result" in st.session_state:
        result = st.session_state["result"]
        today = date.today()
        st.title(result.get("Topic", "Study Notes"))
        st.caption(f"Psychology · {today:%b} {today.day}")

        notes_tab, diagram_tab = st.tabs(["Notes", "Diagram"])
        with notes_tab:
            show_notes(result)
        with diagram_tab:
            if st.button("Regenerate diagram"):
                try:
                    with st.spinner("Redrawing…"):
                        st.session_state["diagram"] = gemma.make_diagram(result)
                except gemma.GemmaError as error:
                    st.error(str(error))
                else:
                    save_session()
            if st.session_state["diagram"].startswith(("flowchart", "graph")):
                layout = st.radio("Layout", list(LAYOUTS), horizontal=True)
                st.session_state["diagram"] = set_direction(st.session_state["diagram"], LAYOUTS[layout])
            show_diagram(st.session_state["diagram"])
    else:
        st.caption("Paste or upload your notes in the sidebar, then click Generate.")

with buddy_col:
    show_buddy()

show_footer()
