"""Quick check of gemma.py against every sample. Run: uv run src/backend/try_llm.py"""
import sys
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

    # Step 0: does the model respond to this sample at all?
    reply = timed("one-line summary", lambda: gemma._ask(
        [{"role": "user", "content": f"Summarise these notes in one sentence:\n\n{notes}"}]
    ))
    if reply:
        print("  ->", reply.strip())

    # Add the real functions below as we write them:
    # notes_dict = timed("rewrite_notes", lambda: gemma.rewrite_notes(notes))
    # diagram = timed("make_diagram", lambda: gemma.make_diagram(notes_dict))
