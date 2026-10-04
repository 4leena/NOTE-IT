"""Quick check of gemma.py against every sample. Run: uv run src/backend/try_llm.py"""
import sys
import textwrap
import time
from pathlib import Path

import gemma

sys.stdout.reconfigure(encoding="utf-8")  # Windows console chokes on Gemma's curly quotes

SAMPLES = Path(__file__).resolve().parents[2] / "samples"


def timed(label, fn):
    start = time.perf_counter()
    try:
        result = fn()
    except gemma.GemmaError as e:
        print(f"  {label}: FAILED ({e})")
        return None
    print(f"  {label}: {time.perf_counter() - start:.1f}s")
    return result


for path in sorted(SAMPLES.glob("*.txt")):
    notes = path.read_text(encoding="utf-8")
    print(f"\n== {path.name} ({len(notes)} chars)")

    notes_dict = timed("rewrite_notes", lambda: gemma.rewrite_notes(notes))
    if notes_dict:
        print("  Topic:", notes_dict["Topic"])
        print("  Items:", {k: len(v) for k, v in notes_dict.items() if k != "Topic"})

    if notes_dict:
        diagram = timed("make_diagram", lambda: gemma.make_diagram(notes_dict))
        if diagram:
            print(textwrap.indent(diagram, "  "))


# Study Buddy: one question per mode, plus an examiner follow-up using history.
print("\n== chat (memory.txt)")
notes = (SAMPLES / "memory.txt").read_text(encoding="utf-8")
for mode, question in [
    ("tutor", "What is chunking?"),
    ("peer", "Explain Loftus and Palmer like I'm five."),
    ("tutor", "What did Milgram find?"),  # not in these notes: should say so
    ("examiner", "Ask me a question."),
]:
    reply = timed(f"chat {mode}", lambda: gemma.chat([], notes, question, mode))
    if reply:
        print(f"  Q: {question}\n  A: {textwrap.indent(reply, '     ').strip()}")

history = [
    {"role": "user", "content": "Ask me a question."},
    {"role": "assistant", "content": "What are the three stores in the multi-store model?"},
]
reply = timed("examiner marks", lambda: gemma.chat(history, notes, "sensory and long term", "examiner"))
if reply:
    print(f"  A: {textwrap.indent(reply, '     ').strip()}")
