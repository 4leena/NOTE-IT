# NOTE-IT Build Guide (team of 2)

Goal: both of you work at the same time, with almost no waiting on each other.

The trick is a **contract**. You agree up front on what each function takes and returns. After that:
- **Person A (LLM)** builds the real functions and tests them from the terminal, with no UI.
- **Person B (UI)** builds the whole app against a **fake `gemma.py`** that returns hard-coded data, with no Ollama needed.
- When both are ready, delete the fake and plug in the real one. If both sides kept to the contract, it just works.

---

## Step 0: Setup (together, about 20 min, do this first)

Both people:
1. `git clone` the repo, create a venv, `pip install streamlit ollama`.
2. Install Ollama, then `ollama pull gemma3`.
3. Hello-world check (Person A leads, Person B copies): call `ollama.chat` with `format="json"` on one sentence and print the result. If this prints something, the setup works.
   - Docs: https://github.com/ollama/ollama-python
4. Add a `requirements.txt` and a `.gitignore` (`venv/`, `__pycache__/`), then push.

Optional: if you want Unsloth's quantized Gemma, use `ollama pull hf.co/unsloth/gemma-3-4b-it-GGUF:Q4_K_M`. Keep the model name in **one constant** so you can swap it later.

---

## Step 1: Write the contract (together, about 15 min)

Create two files and push them before splitting up.

**1. Function signatures** (from `design.md`). Do not change them after this without telling each other:

| Function | Input | Output |
|---|---|---|
| `detect_subject(notes)` | str | `"biology"` / `"math"` / `"cs"` |
| `rewrite_notes(notes, subject)` | str, str | `dict`, keys = section names for that subject |
| `make_diagram(notes_dict)` | dict | str (Mermaid code) |
| `chat(history, notes, question)` | list of `{role, content}`, str, str | str (the reply) |

**2. The exact section keys**, for example `"Key Terms"`, `"Quiz Yourself"`. Decide how the quiz is shaped (a list of strings, or a list of `{q, a}`?). **This is where teams get stuck, so decide it now.**

**3. Errors.** Decide that `gemma.py` raises one custom exception, for example `GemmaError(message)`, with a friendly message. The UI catches only that one.

**4. Sample inputs.** Together write three short note files in `samples/` (`bio.txt`, `math.txt`, `cs.txt`). Deliberately make them messy.

**5. A fake output.** Person A writes one example dict per subject in `samples/expected_*.json`. Person B will use these as fake data.

Commit and push. Now you can split.

---

## Person A: LLM / logic (`gemma.py`, `templates.py`)

Never touch `app.py`. Test everything from a throwaway script, `try_llm.py`, that loops over `samples/`.

| # | Task | How you know it works |
|---|---|---|
| A1 | `detect_subject`. Ask for one word, then clean it (lowercase, strip, check it's one of three, else fall back). | All 3 samples are classified correctly 5 times in a row. |
| A2 | `templates.py`: per-subject section lists and prompt text. | Prompt is built from the section list, not copy-pasted three times. |
| A3 | `rewrite_notes` with `format="json"`. Put the exact keys in the prompt. Validate keys after `json.loads`, and **retry once** on bad JSON or missing keys. | Every sample returns every key. Try empty input and gibberish. |
| A4 | `make_diagram`. Ask for Mermaid only (no code fences, no prose). Strip fences in code. Pick flowchart vs cycle vs structure by subject. | Paste output into https://mermaid.live. It renders for all 3 samples. |
| A5 | `chat`. System prompt: "Answer only from these notes, otherwise say so." Add a quiz mode. | Ask something not in the notes. It should refuse. "Quiz me" asks one question at a time. |
| A6 | Error handling. Catch connection and model-not-found errors, then raise `GemmaError`. | Stop Ollama and run it. You get a friendly message, not a traceback. |

**Test log:** keep a short `docs/llm-notes.md` with what worked, which prompts failed, and how fast each call was. This is also gold for the DEV post ("What was hard").

Tips:
- A 4B model follows short prompts better than long ones. Show **one small example** of the JSON you want.
- If Mermaid keeps breaking, ask for simpler diagrams (`flowchart TD`, short labels, no special characters).
- Do A1, A3 and A4 first. A5 is last because it is the easiest to cut down.

---

## Person B: UI / system (`app.py`, rendering, polish)

Never touch `gemma.py`. Instead create `fake_gemma.py` with the same function names that returns the data from `samples/expected_*.json` (add `time.sleep(2)` to feel the spinner). Use `import fake_gemma as gemma` in `app.py` for now.

| # | Task | How you know it works |
|---|---|---|
| B1 | Skeleton: title, text area, "Generate" button, empty-input message. | Empty input shows a friendly prompt. |
| B2 | Flow: spinner, then show the detected subject in a dropdown the user can **override**. | Changing the dropdown re-runs the rewrite. |
| B3 | Tabs: Notes, Diagram, Study Buddy. Render each dict key as a section. | All sections show from fake data. |
| B4 | Diagram tab: HTML component loading Mermaid from a CDN. If it fails, show the code as plain text. | Works with the fake diagram AND a deliberately broken one. |
| B5 | Study Buddy: chat UI with `st.session_state`, "Quiz me" button. Docs: https://docs.streamlit.io (chat elements). | History survives reruns. |
| B6 | Error handling: catch `GemmaError`, show `st.error`. Cache results so a rerun doesn't call the model again. | Fake a `GemmaError` and check the message. |
| B7 | Polish: layout, a "copy notes" or download button, a short "how to use" blurb. | Someone who never saw it can use it. |

Also own: README setup steps, screenshots, demo video script.

Tips:
- Streamlit reruns the script on every click, so keep results in `st.session_state`.
- B3 and B4 matter most. B5 and B7 can be trimmed.

---

## Step 2: Integrate (together, about 30 min)

1. Pull. In `app.py`, change `import fake_gemma as gemma` to `import gemma`.
2. Run the three samples end to end.
3. Fix mismatches **in the contract's favour**: if the UI expects a key and the LLM sends something different, decide together who changes. Don't both fix it.
4. Delete `fake_gemma.py` (or keep it as a dev/offline mode).

## Step 3: Test and freeze

- Run the test plan in `design.md` on all 3 samples. Then try bad input: empty, very long, non-English, wrong subject (history, say).
- **6:30 PM PDT Saturday: freeze.** After this, bug fixes only.

---

## Suggested timeline for today (PDT)

| Time | Both | Person A | Person B |
|---|---|---|---|
| Now to 1:30 | Steps 0 and 1 | | |
| 1:30 to 3:30 | | A1 to A3 | B1 to B4 |
| 3:30 to 5:00 | | A4, A5 | B5, B6 |
| 5:00 to 5:30 | Step 2: integrate | | |
| 5:30 to 6:30 | Step 3: test samples and fix | A6 | B7 |
| 6:30 | Freeze and push | | |

Sunday follows `Untitled` handoff plan: fix bugs, test the README setup literally, record the demo, show it to the real friend, write the DEV post.

Split the Sunday work too: one person records the demo and screenshots, the other drafts the post (writing quality counts most in judging).

---

## Git rules so you don't collide

- A owns `gemma.py`, `templates.py`, `try_llm.py`. B owns `app.py`, `fake_gemma.py`. `samples/` and the contract are shared: change them only after messaging each other.
- `git pull` before you start, commit small, push often. Short messages: "Add subject detection".
- If you must touch the other person's file, ask first or use a branch.

## If you fall behind (cut in this order)

1. "Quiz me" mode (keep plain Q&A).
2. Subject dropdown override.
3. Diagram variety (use one flowchart style for everything).
4. Polish (B7).

Never cut: detect, rewrite, error messages, and the three-sample test.

## Decide today

- Who is the friend you're building for? It affects the demo and the post.
- Who publishes the DEV post, and both DEV usernames.
