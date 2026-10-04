import html
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src" / "backend"))
import gemma  # real Gemma via Ollama. For the offline demo data: import fake_gemma as gemma

st.set_page_config(page_title="NOTE-IT", layout="wide")

MODES = {
    "Tutor": ("tutor", ":material/school:", "I'll explain your notes step by step."),
    "Peer": ("peer", ":material/group:", "Ask me anything. I'll keep it simple."),
    "Examiner": ("examiner", ":material/fact_check:", "I'll quiz you on your notes and mark your answers."),
}

BUDDY_CSS = """
<style>
.st-key-buddy_launcher {
  position: fixed;
  right: 12px;
  bottom: 52px;
  width: auto !important;
  z-index: 999996;
  flex-direction: row !important;
  align-items: flex-end !important;
  gap: 0 !important;
}
.st-key-buddy_launcher [data-testid="stElementContainer"] {
  width: auto !important;
}
.mascot {
  width: 96px;
  display: block;
  filter: drop-shadow(0 6px 10px rgba(59, 47, 37, 0.18));
}
.st-key-mascot_button {
  position: absolute !important;
  right: 0;
  bottom: 0;
  width: 96px !important;
  height: 112px;
}
.st-key-mascot_button button {
  width: 96px;
  height: 112px;
  opacity: 0;
  cursor: pointer;
}
.buddy-hello {
  position: relative;
  width: 220px;
  margin: 0 8px 70px 0;
  background: #FFFFFF;
  border: 1px solid #EAD8BF;
  border-radius: 18px;
  padding: 12px 16px;
  box-shadow: 0 10px 24px rgba(59, 47, 37, 0.16);
  color: #3B2F25;
  font-size: 0.92rem;
  animation: hello-pop 0.5s ease-out 0.4s both;
}
.buddy-hello::after {
  content: "";
  position: absolute;
  right: -8px;
  bottom: 18px;
  width: 14px;
  height: 14px;
  background: #FFFFFF;
  border-right: 1px solid #EAD8BF;
  border-bottom: 1px solid #EAD8BF;
  transform: rotate(-45deg);
}
.buddy-hello b {
  display: block;
  font-family: Caveat, cursive;
  font-size: 1.6rem;
  color: #8C5E2A;
}
@keyframes hello-pop {
  from { opacity: 0; transform: translateY(12px) scale(0.96); }
  to { opacity: 1; transform: none; }
}
.buddy-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #FFFCF7;
  font-weight: 600;
  font-size: 1.05rem;
}
.buddy-title img {
  width: 30px;
  height: 30px;
  background: #F3E2CB;
  border-radius: 50%;
  padding: 3px;
}
.st-key-buddy_close button {
  color: #FFFCF7 !important;
}
.st-key-buddy_close button p {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}
.bot-greet {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 4px;
}
.bot-avatar {
  flex: 0 0 auto;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #F3E2CB;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bot-avatar img {
  width: 52px;
}
.bot-bubble {
  position: relative;
  background: #FFFFFF;
  border: 1px solid #EAD8BF;
  border-radius: 16px;
  padding: 12px 14px;
  color: #3B2F25;
  font-size: 0.92rem;
}
.bot-bubble b {
  display: block;
  margin-bottom: 4px;
}
.st-key-buddy {
  position: fixed;
  right: 12px;
  bottom: 172px;
  width: 356px !important;
  z-index: 999996;
  box-shadow: 0 14px 36px rgba(59, 47, 37, 0.20);
  background: #FBF5EC;
  border: 1px solid #EAD8BF;
  border-radius: 14px;
  padding-bottom: 12px;
  overflow: hidden;
}
.st-key-buddy_header {
  background: #3B2F25;
  padding: 8px 12px 8px 16px;
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
.st-key-buddy [data-testid="stChatMessageAvatarUser"],
.st-key-buddy [data-testid="stChatMessageAvatarAssistant"] {
  background: #F3E2CB !important;
  color: #8C5E2A !important;
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
.st-key-buddy [data-testid="stChatMessage"]:not(:has([data-testid="stChatMessageAvatarUser"])) [data-testid="stChatMessageContent"] {
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

FRIEND_NAME = ""

START_SCREEN = """
<div style="text-align:center; padding:48px 16px 24px; color:#3B2F25;">
  <div class="hand" style="font-size:3rem; font-weight:700; color:#8C5E2A;">What are we studying today?</div>
  <div style="opacity:0.75; margin-top:6px;">Turn messy lecture notes into a page you actually want to study from.</div>
  <div style="display:flex; gap:16px; justify-content:center; margin-top:36px; flex-wrap:wrap;">
    <div class="step"><div class="hand num">1</div>Paste or upload your notes in the sidebar</div>
    <div class="step"><div class="hand num">2</div>Press Generate and give it a moment</div>
    <div class="step"><div class="hand num">3</div>Study, highlight, and chat with your buddy</div>
  </div>
</div>
"""

PAGE_CSS = """
<style>
.hand {
  font-family: Caveat, cursive;
}
.step {
  width: 170px;
  background: #FBF5EC;
  border: 1px solid #EAD8BF;
  border-radius: 12px;
  padding: 16px;
  font-size: 0.95rem;
}
.step .num {
  font-size: 2rem;
  font-weight: 700;
  color: #8C5E2A;
  line-height: 1;
  margin-bottom: 6px;
}
.brand {
  display: flex;
  align-items: baseline;
  gap: 16px;
}
.brand .wordmark {
  font-size: 1.4rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.brand .greet {
  font-size: 1.6rem;
  color: #8C5E2A;
}
.streak {
  text-align: right;
  font-size: 1.5rem;
  color: #3B2F25;
}
.cheer {
  font-size: 1.5rem;
  color: #3B2F25;
}
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


NOTEBOOK_HTML = """
<style>
@font-face { font-family: Caveat; src: url(/app/static/fonts/caveat-400.woff2); font-weight: 400; }
@font-face { font-family: Caveat; src: url(/app/static/fonts/caveat-700.woff2); font-weight: 700; }
html, body { margin: 0; height: 100%; }
body { font-family: -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; color: #3B2F25; line-height: 1.6;
  background: #FFFCF7; display: flex; gap: 14px; overflow: hidden; }
.rail { flex: 0 0 auto; display: flex; flex-direction: column; gap: 8px; padding: 4px 0; }
.rail button { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer;
  background: #FFFFFF; border: 1px solid #EAD8BF; border-radius: 12px; color: #8C5E2A; padding: 0; }
.rail button:hover { background: #FBF5EC; }
.rail button.on { background: #E7BE8A; border-color: #8C5E2A; color: #3B2F25; }
.rail svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.swatches { display: none; flex-direction: column; align-items: center; gap: 6px; padding: 2px 0 4px; }
body.sticky .swatches { display: flex; }
.swatch { width: 22px; height: 22px; border-radius: 50%; border: 2px solid #FFFFFF; box-shadow: 0 0 0 1px #EAD8BF; cursor: pointer; }
.swatch.on { box-shadow: 0 0 0 2px #8C5E2A; }
.scroller { flex: 1 1 auto; min-width: 0; overflow-y: auto; overflow-x: hidden; padding: 4px 8px 24px 2px; }
.page { position: relative; background: #FFFFFF; border: 1px solid #EAD8BF; border-radius: 6px 14px 14px 6px;
  padding: 12px 32px 40px 64px; margin-left: 22px; box-shadow: 0 2px 12px rgba(59, 47, 37, 0.06); }
.spiral { position: absolute; left: -24px; top: 18px; bottom: 18px; width: 56px; z-index: 2; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='34'%3E%3Ccircle cx='40' cy='17' r='5' fill='%23F1E8DA' stroke='%23DCCDB8'/%3E%3Cpath d='M40 17 C 30 3, 8 5, 6 15' fill='none' stroke='%237E746A' stroke-width='3.2' stroke-linecap='round'/%3E%3Cpath d='M38 13 C 30 6, 14 6, 10 12' fill='none' stroke='%23C8BFB4' stroke-width='1' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: repeat-y; }
.layout { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 28px; align-items: start; }
.quiz { position: sticky; top: 8px; background: #FFFCF7; border: 1px solid #EAD8BF; border-radius: 12px; padding: 4px 14px 14px; }
.quiz-head { display: flex; align-items: center; justify-content: space-between; }
.quiz h2 { margin: 8px 0 6px; font-size: 1.7rem; }
.icon-btn { width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; cursor: pointer; padding: 0;
  background: #FFFFFF; border: 1px solid #EAD8BF; border-radius: 10px; color: #8C5E2A; }
.icon-btn:hover, .show-gallery .gallery-toggle { background: #E7BE8A; color: #3B2F25; }
.icon-btn svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.deck { position: relative; margin: 10px 4px 6px; }
.deck::before, .deck::after { content: ""; position: absolute; inset: 0; background: #FFFFFF; border: 1px solid #EAD8BF;
  border-radius: 16px; box-shadow: 0 4px 10px rgba(59, 47, 37, 0.06); }
.deck::before { transform: rotate(-3deg); }
.deck::after { transform: rotate(2deg) translate(3px, 2px); }
.flashcard { position: relative; z-index: 1; height: 200px; perspective: 900px; cursor: pointer; }
.flashcard .inner { position: relative; width: 100%; height: 100%; transition: transform 0.5s; transform-style: preserve-3d; }
.flashcard.flipped .inner { transform: rotateY(180deg); }
.face { position: absolute; inset: 0; backface-visibility: hidden; -webkit-backface-visibility: hidden; border-radius: 14px;
  border: 1px solid #EAD8BF; padding: 18px 16px 56px; display: flex; align-items: center; justify-content: center; text-align: center;
  overflow: auto; box-shadow: 0 8px 18px rgba(59, 47, 37, 0.12); }
.front { background: #FFFFFF; font-weight: 700; font-size: 1rem; }
.back { background: #FFF6E3; transform: rotateY(180deg); font-family: Caveat, cursive; font-size: 1.5rem; line-height: 1.2; }
.turn { position: absolute; z-index: 2; left: 50%; bottom: 14px; transform: translateX(-50%); display: flex; align-items: center; gap: 6px;
  font: 600 0.9rem -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif; color: #FFFFFF; background: #8C5E2A;
  border: none; border-radius: 999px; padding: 7px 16px; cursor: pointer; box-shadow: 0 4px 10px rgba(140, 94, 42, 0.3); }
.turn:hover { background: #75491C; }
.turn svg { width: 15px; height: 15px; fill: none; stroke: currentColor; stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round; }
.quiz-nav { display: flex; align-items: center; justify-content: space-between; margin-top: 14px; font-size: 0.9rem; color: #6B5B4B; }
.round { width: 36px; height: 36px; border-radius: 50%; border: none; background: #8C5E2A; color: #FFFFFF; cursor: pointer;
  display: flex; align-items: center; justify-content: center; padding: 0; box-shadow: 0 3px 8px rgba(140, 94, 42, 0.3); }
.round:hover { background: #75491C; }
.round svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 2.6; stroke-linecap: round; stroke-linejoin: round; }
.gallery { display: none; grid-template-columns: 1fr 1fr; gap: 8px; }
.show-gallery .gallery { display: grid; }
.show-gallery .single { display: none; }
.mini { background: #FFFFFF; border: 1px solid #EAD8BF; border-radius: 10px; padding: 8px; font-size: 0.78rem; line-height: 1.3;
  cursor: pointer; }
.mini span { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.mini:hover { border-color: #8C5E2A; }
.mini b { display: block; font-family: Caveat, cursive; font-size: 1.1rem; color: #8C5E2A; }
h2 { font-family: Caveat, cursive; font-weight: 700; font-size: 2rem; color: #8C5E2A; margin: 22px 0 4px; }
p { margin: 6px 0; }
.term { font-weight: 600; padding: 0 4px; border-radius: 3px;
  background: linear-gradient(100deg, rgba(231,190,138,0) 0%, rgba(231,190,138,0.85) 3%, rgba(231,190,138,0.55) 50%, rgba(231,190,138,0.8) 96%, rgba(231,190,138,0) 100%); }
.card { background: #FFFCF7; border: 1px solid #EAD8BF; border-radius: 10px; padding: 12px 16px; margin: 10px 0; }
.example { border-left: 3px solid #E7BE8A; padding: 2px 0 2px 14px; margin: 10px 0; }
details { background: #FFFCF7; border: 1px solid #EAD8BF; border-radius: 10px; padding: 10px 14px; margin: 8px 0; }
summary { cursor: pointer; font-weight: 600; }
.answer { font-family: Caveat, cursive; font-size: 1.45rem; color: #8C5E2A; margin-top: 6px; }
canvas { position: absolute; inset: 0; pointer-events: none; z-index: 3; }
body.pen canvas, body.eraser canvas { pointer-events: auto; }
body.pen canvas { cursor: crosshair; }
body.eraser canvas { cursor: cell; }
body.highlight .content { cursor: text; }
body.sticky .page { cursor: copy; }
.notes-layer { position: absolute; inset: 0; z-index: 4; pointer-events: none; }
.note { position: absolute; width: 180px; pointer-events: auto; display: flex; flex-direction: column;
  box-shadow: 0 6px 14px rgba(59, 47, 37, 0.16); transform: rotate(-1.2deg); }
.note:nth-child(even) { transform: rotate(1deg); }
.note .grip { height: 16px; cursor: grab; touch-action: none; background-color: rgba(59, 47, 37, 0.07);
  background-image: radial-gradient(circle, rgba(59, 47, 37, 0.35) 1.2px, transparent 1.6px);
  background-size: 8px 8px; background-position: center; background-repeat: repeat-x; }
.note .grip:active { cursor: grabbing; }
.note .delete { position: absolute; top: 0; right: 2px; width: 18px; height: 16px; padding: 0; border: none; background: none;
  font: 600 14px/16px -apple-system, Helvetica, Arial, sans-serif; color: #3B2F25; opacity: 0.25; cursor: pointer; }
.note:hover .delete { opacity: 0.7; }
.note .delete:hover { opacity: 1; color: #8C5E2A; }
.note .text { min-height: 92px; padding: 8px 14px 12px; outline: none; cursor: text;
  font-family: Caveat, cursive; font-size: 1.35rem; line-height: 1.25; color: #3B2F25; }
.note .text:empty::before { content: "Write here..."; opacity: 0.45; }
body.pen .note { pointer-events: none; }
body.eraser .note { cursor: cell; }
</style>
<div class="rail">
  <button data-mode="pen" title="Pen" aria-label="Pen">
    <svg viewBox="0 0 24 24"><path d="M21.17 6.81a2.82 2.82 0 0 0-3.98-3.98L3.84 16.17a2 2 0 0 0-.5.83l-1.32 4.35a.5.5 0 0 0 .62.62l4.35-1.32a2 2 0 0 0 .83-.5z"/><path d="m15 5 4 4"/></svg>
  </button>
  <button data-mode="highlight" title="Highlighter" aria-label="Highlighter">
    <svg viewBox="0 0 24 24"><path d="m9 11-6 6v3h9l3-3"/><path d="m22 12-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4"/></svg>
  </button>
  <button data-mode="sticky" title="Sticky note" aria-label="Sticky note">
    <svg viewBox="0 0 24 24"><path d="M16 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V8z"/><path d="M15 3v4a2 2 0 0 0 2 2h4"/></svg>
  </button>
  <div class="swatches">
    <div class="swatch on" data-color="#F9E3B8" style="background:#F9E3B8" title="Butter"></div>
    <div class="swatch" data-color="#F3D7BF" style="background:#F3D7BF" title="Peach"></div>
    <div class="swatch" data-color="#DCE5C8" style="background:#DCE5C8" title="Sage"></div>
  </div>
  <button data-mode="eraser" title="Eraser" aria-label="Eraser">
    <svg viewBox="0 0 24 24"><path d="m7 21-4.3-4.3c-1-1-1-2.5 0-3.4l9.6-9.6c1-1 2.5-1 3.4 0l5.6 5.6c1 1 1 2.5 0 3.4L13 21"/><path d="M22 21H7"/><path d="m5 11 9 9"/></svg>
  </button>
</div>
<div class="scroller">
  <div class="page">
    <div class="spiral"></div>
    <div class="layout">
      <div class="content">NOTES_CONTENT</div>
      <aside class="quiz">
        <div class="quiz-head">
          <h2>Quiz Yourself</h2>
          <button class="icon-btn gallery-toggle" title="See all cards" aria-label="See all cards">
            <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
          </button>
        </div>
        <div class="single">
          <div class="deck">
            <div class="flashcard">
              <div class="inner"><div class="face front"></div><div class="face back"></div></div>
              <button class="turn" title="Turn the card" aria-label="Turn the card">
                <svg viewBox="0 0 24 24"><path d="M21 12a9 9 0 0 0-15-6.7L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 15 6.7l3-2.7"/><path d="M21 21v-5h-5"/></svg>
                Turn
              </button>
            </div>
          </div>
          <div class="quiz-nav">
            <button class="round prev" title="Previous card" aria-label="Previous card"><svg viewBox="0 0 24 24"><path d="m15 18-6-6 6-6"/></svg></button>
            <span class="count"></span>
            <button class="round next" title="Next card" aria-label="Next card"><svg viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></svg></button>
          </div>
        </div>
        <div class="gallery"></div>
      </aside>
    </div>
    <canvas></canvas>
    <div class="notes-layer"></div>
  </div>
</div>
<script>
const KEY = SESSION_KEY;
const QUIZ = QUIZ_DATA;
const quizBox = document.querySelector(".quiz");
const card = document.querySelector(".flashcard");
let cardIndex = 0;

function showCard() {
  card.classList.remove("flipped");
  card.querySelector(".front").textContent = QUIZ[cardIndex].q;
  card.querySelector(".back").textContent = QUIZ[cardIndex].a;
  quizBox.querySelector(".count").textContent = "Card " + (cardIndex + 1) + " of " + QUIZ.length;
}
if (QUIZ.length) {
  showCard();
  card.addEventListener("click", () => card.classList.toggle("flipped"));
  card.querySelector(".turn").addEventListener("click", event => { event.stopPropagation(); card.classList.toggle("flipped"); });
  quizBox.querySelector(".prev").addEventListener("click", () => { cardIndex = (cardIndex - 1 + QUIZ.length) % QUIZ.length; showCard(); });
  quizBox.querySelector(".next").addEventListener("click", () => { cardIndex = (cardIndex + 1) % QUIZ.length; showCard(); });
  quizBox.querySelector(".gallery-toggle").addEventListener("click", () => quizBox.classList.toggle("show-gallery"));
  const gallery = quizBox.querySelector(".gallery");
  QUIZ.forEach((item, i) => {
    const mini = document.createElement("div");
    mini.className = "mini";
    const label = document.createElement("b");
    label.textContent = "Card " + (i + 1);
    const question = document.createElement("span");
    question.textContent = item.q;
    mini.append(label, question);
    mini.addEventListener("click", () => { cardIndex = i; showCard(); quizBox.classList.remove("show-gallery"); });
    gallery.appendChild(mini);
  });
} else {
  quizBox.querySelector(".single").innerHTML = "<p>No quiz questions for these notes.</p>";
  quizBox.querySelector(".gallery-toggle").style.display = "none";
}
const page = document.querySelector(".page");
const content = document.querySelector(".content");
const canvas = document.querySelector("canvas");
const layer = document.querySelector(".notes-layer");
const ctx = canvas.getContext("2d");
let mode = "read";
let noteColor = "#F9E3B8";
let drawing = false;

function load(name) { try { return localStorage.getItem(KEY + ":" + name); } catch (e) { return null; } }
function store(name, value) { try { localStorage.setItem(KEY + ":" + name, value); } catch (e) {} }

const savedHighlights = load("highlights");
if (savedHighlights) content.innerHTML = savedHighlights;

function sizeCanvas() {
  const ratio = window.devicePixelRatio || 1;
  canvas.width = page.offsetWidth * ratio;
  canvas.height = page.offsetHeight * ratio;
  canvas.style.width = page.offsetWidth + "px";
  canvas.style.height = page.offsetHeight + "px";
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.lineCap = "round"; ctx.lineJoin = "round";
  const ink = load("ink");
  if (ink) { const img = new Image(); img.onload = () => ctx.drawImage(img, 0, 0, page.offsetWidth, page.offsetHeight); img.src = ink; }
}
sizeCanvas();
new ResizeObserver(sizeCanvas).observe(page);

function saveNotes() {
  const notes = [...layer.querySelectorAll(".note")].map(n => ({
    x: n.offsetLeft, y: n.offsetTop, color: n.dataset.color, text: n.querySelector(".text").innerText,
  }));
  store("stickies", JSON.stringify(notes));
}
function makeDraggable(note, grip) {
  grip.addEventListener("pointerdown", event => {
    if (mode === "eraser") return;
    event.preventDefault();
    grip.setPointerCapture(event.pointerId);
    const startX = event.clientX, startY = event.clientY;
    const left = note.offsetLeft, top = note.offsetTop;
    function move(e) {
      const x = Math.max(0, Math.min(left + e.clientX - startX, page.offsetWidth - note.offsetWidth));
      const y = Math.max(0, Math.min(top + e.clientY - startY, page.offsetHeight - note.offsetHeight));
      note.style.left = x + "px"; note.style.top = y + "px";
    }
    function stop() {
      grip.removeEventListener("pointermove", move);
      grip.removeEventListener("pointerup", stop);
      saveNotes();
    }
    grip.addEventListener("pointermove", move);
    grip.addEventListener("pointerup", stop);
  });
}
function addNote(x, y, color, text) {
  const note = document.createElement("div");
  note.className = "note";
  note.style.left = x + "px"; note.style.top = y + "px";
  note.style.background = color; note.dataset.color = color;
  const grip = document.createElement("div");
  grip.className = "grip"; grip.title = "Drag to move";
  const body = document.createElement("div");
  body.className = "text"; body.contentEditable = "true"; body.innerText = text;
  body.addEventListener("input", saveNotes);
  const remove = document.createElement("button");
  remove.className = "delete"; remove.title = "Delete note"; remove.setAttribute("aria-label", "Delete note");
  remove.textContent = "\u00D7";
  remove.addEventListener("pointerdown", event => event.stopPropagation());
  remove.addEventListener("click", event => { event.stopPropagation(); note.remove(); saveNotes(); });
  note.append(grip, body, remove);
  note.addEventListener("pointerdown", event => {
    if (mode !== "eraser") return;
    event.preventDefault(); note.remove(); saveNotes();
  });
  makeDraggable(note, grip);
  layer.appendChild(note);
  return note;
}
JSON.parse(load("stickies") || "[]").forEach(n => addNote(n.x, n.y, n.color, n.text));

document.querySelectorAll(".rail button").forEach(button => {
  button.addEventListener("click", () => {
    mode = mode === button.dataset.mode ? "read" : button.dataset.mode;
    document.body.className = mode;
    document.querySelectorAll(".rail button").forEach(b => b.classList.toggle("on", b.dataset.mode === mode));
  });
});
document.querySelectorAll(".swatch").forEach(swatch => {
  swatch.addEventListener("click", () => {
    noteColor = swatch.dataset.color;
    document.querySelectorAll(".swatch").forEach(s => s.classList.toggle("on", s === swatch));
  });
});

content.addEventListener("mouseup", () => {
  if (mode !== "highlight") return;
  const selection = window.getSelection();
  if (!selection || selection.isCollapsed) return;
  content.contentEditable = "true";
  document.execCommand("styleWithCSS", false, true);
  document.execCommand("hiliteColor", false, "#F6D58E");
  content.contentEditable = "false";
  selection.removeAllRanges();
  store("highlights", content.innerHTML);
});

page.addEventListener("click", event => {
  if (mode !== "sticky" || event.target.closest(".note")) return;
  const r = page.getBoundingClientRect();
  const x = Math.max(8, Math.min(event.clientX - r.left - 20, page.offsetWidth - 220));
  const note = addNote(x, event.clientY - r.top - 20, noteColor, "");
  note.querySelector(".text").focus({ preventScroll: true });
  saveNotes();
});

function point(event) { const r = canvas.getBoundingClientRect(); return [event.clientX - r.left, event.clientY - r.top]; }

function eraseUnder(event) {
  const hits = document.elementsFromPoint(event.clientX, event.clientY);
  const mark = hits.find(el => el.tagName === "SPAN" && el.style && el.style.backgroundColor && content.contains(el));
  if (mark) { mark.replaceWith(...mark.childNodes); store("highlights", content.innerHTML); }
}

canvas.addEventListener("pointerdown", event => {
  if (mode !== "pen" && mode !== "eraser") return;
  drawing = true;
  if (mode === "eraser") { eraseUnder(event); ctx.globalCompositeOperation = "destination-out"; ctx.lineWidth = 20; }
  else { ctx.globalCompositeOperation = "source-over"; ctx.lineWidth = 2.5; ctx.strokeStyle = "#8C5E2A"; }
  ctx.beginPath(); ctx.moveTo(...point(event));
});
canvas.addEventListener("pointermove", event => { if (!drawing) return; ctx.lineTo(...point(event)); ctx.stroke(); });
["pointerup", "pointerleave"].forEach(name => canvas.addEventListener(name, () => {
  if (!drawing) return;
  drawing = false; ctx.globalCompositeOperation = "source-over";
  store("ink", canvas.toDataURL());
}));
</script>
"""


def notes_html(result):
    e = html.escape
    parts = []

    terms = result.get("Key Terms", [])
    if terms:
        parts.append("<h2>Key Terms</h2>")
        for item in terms:
            parts.append(f"<p><span class='term'>{e(item['term'])}</span> {e(item['definition'])}</p>")

    theories = result.get("Theories & Researchers", [])
    if theories:
        parts.append("<h2>Theories &amp; Researchers</h2>")
        for item in theories:
            parts.append(f"<p><b>{e(item['name'])}</b><br>{e(item['summary'])}</p>")

    studies = result.get("Key Studies", [])
    if studies:
        parts.append("<h2>Key Studies</h2>")
        for item in studies:
            parts.append(
                f"<div class='card'><b>{e(item['study'])}</b>"
                f"<p><i>Method:</i> {e(item['method'])}</p>"
                f"<p><i>Findings:</i> {e(item['findings'])}</p></div>"
            )

    evaluation = result.get("Evaluation", [])
    if evaluation:
        parts.append("<h2>Evaluation</h2><ul>")
        parts.extend(f"<li>{e(point)}</li>" for point in evaluation)
        parts.append("</ul>")

    examples = result.get("Real-World Examples", [])
    if examples:
        parts.append("<h2>Real-World Examples</h2>")
        parts.extend(f"<div class='example'>{e(example)}</div>" for example in examples)

    return "\n".join(parts)


def quiz_data(result):
    cards = [{"q": item["q"], "a": item["a"]} for item in result.get("Quiz Yourself", [])]
    return json.dumps(cards).replace("</", "<\\/")


def show_notes(result):
    session_key = json.dumps("noteit:" + st.session_state.get("session_file", "unsaved"))
    page = (
        NOTEBOOK_HTML.replace("SESSION_KEY", session_key)
        .replace("NOTES_CONTENT", notes_html(result))
        .replace("QUIZ_DATA", quiz_data(result))
    )
    st.iframe(page, height=720)


def set_direction(code, direction):
    return re.sub(r"^(flowchart|graph)\s+\w+", rf"\1 {direction}", code, count=1)


def show_diagram(code):
    safe = json.dumps(code).replace("</", "<\\/")
    st.iframe(MERMAID_HTML.replace("DIAGRAM_CODE", safe), height=450)
    with st.expander("Edit as code (advanced)"):
        st.caption("Change the text and press Ctrl+Enter (Cmd+Enter on Mac) to redraw.")
        st.text_area("Mermaid code", key="diagram", height=200, label_visibility="collapsed")


def greeting():
    hour = datetime.now().hour
    part = "morning" if hour < 12 else "afternoon" if hour < 18 else "evening"
    return f"Good {part}, {FRIEND_NAME}" if FRIEND_NAME else f"Good {part}"


def study_streak(days):
    day = date.today()
    if day.isoformat() not in days:
        day -= timedelta(days=1)
    count = 0
    while day.isoformat() in days:
        count += 1
        day -= timedelta(days=1)
    return count


def show_header():
    streak = study_streak(sessions_by_day())
    streak_text = f"{streak}-day streak" if streak else "Start a streak today"
    with st.container(key="app_header"):
        left, middle, right = st.columns([4, 2, 1], vertical_alignment="center")
        left.html(f"<div class='brand'><span class='wordmark'>NOTE-IT</span><span class='hand greet'>{greeting()}</span></div>")
        middle.html(f"<div class='hand streak'>{streak_text}</div>")
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
        st.html(f"<div class='hand cheer'>{cheer}</div>")


BUDDY_AVATAR = "static/buddy-head.svg"


def bot_greeting(line):
    st.html(
        "<div class='bot-greet'><div class='bot-avatar'><img src='/app/static/buddy-head.svg' alt=''></div>"
        f"<div class='bot-bubble'><b>Hello! How can I help you today?</b>{line}</div></div>"
    )


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


def show_buddy_popup():
    st.html(BUDDY_CSS)
    is_open = st.session_state.get("buddy_open", False)
    with st.container(key="buddy_launcher"):
        if not is_open:
            line = "Ask me anything about your notes." if "result" in st.session_state else "Generate your notes and I'll help you study."
            st.html(f"<div class='buddy-hello'><b>Hello! I'm here to help.</b>{line}</div>")
        st.html("<img class='mascot' src='/app/static/buddy.svg' alt=''>")
        if st.button("Close Study Buddy" if is_open else "Open Study Buddy", key="mascot_button"):
            st.session_state["buddy_open"] = not is_open
            st.rerun()
    if is_open:
        show_buddy()


def show_buddy():
    with st.container(key="buddy"):
        with st.container(key="buddy_header"):
            title, close = st.columns([5, 1], vertical_alignment="center")
            title.html("<div class='buddy-title'><img src='/app/static/buddy-head.svg' alt=''>Study Buddy</div>")
            if close.button("Close", icon=":material/close:", key="buddy_close", type="tertiary"):
                st.session_state["buddy_open"] = False
                st.rerun()

        with st.container(key="buddy_body"):
            if "result" not in st.session_state:
                bot_greeting("Generate your notes first, then ask me anything about them.")
                return

            mode = st.session_state.setdefault("mode", "Tutor")
            history = st.session_state.setdefault("history", [])

            messages = st.container(height=330, border=False)
            with messages:
                if not history and not st.session_state.get("buddy_input"):
                    bot_greeting(MODES[mode][2])
                for msg in history:
                    with st.chat_message(msg["role"], avatar=BUDDY_AVATAR if msg["role"] == "assistant" else None):
                        st.markdown(msg["content"])

            show_mode_buttons(mode)
            question = st.chat_input("Type your message…", key="buddy_input")

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
                with st.chat_message("assistant", avatar=BUDDY_AVATAR):
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
    st.html(START_SCREEN)

show_buddy_popup()
show_footer()
