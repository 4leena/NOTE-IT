# NOTE-IT Design Doc

## Problem
Lecture notes are messy and hard to study from. Students want clean, structured notes, a quick visual, and a way to test themselves, without uploading private notes to a cloud service.

## Goal
Paste notes, get structured study notes, a diagram, and a chatbot that answers from those notes. Everything runs locally.

## Non-goals
3D models, live mic transcription, handwriting/photo upload. Optional stretch: ElevenLabs read-aloud.

## Flow

```
paste notes -> detect subject -> rewrite into template -> generate diagram -> Study Buddy chat
```

## Components

| File | Job |
|---|---|
| `app.py` | Streamlit UI: input box, tabs (Notes, Diagram, Study Buddy), error messages |
| `gemma.py` | Ollama calls |
| `templates.py` | Subject templates and prompt text |

### `gemma.py` functions
- `detect_subject(notes) -> "biology" | "math" | "cs"`
- `rewrite_notes(notes, subject) -> dict` (keys match the template sections)
- `make_diagram(notes_or_dict) -> str` (Mermaid code)
- `chat(history, notes, question) -> str`

## Templates (JSON keys)

| Subject | Sections |
|---|---|
| Biology | Key Terms, Main Process, Structure & Function, Quiz Yourself |
| Math | Definitions, Theorems & Formulas, Worked Example, Common Mistakes, Quiz Yourself |
| CS | Key Concepts, How It Works, Code/Pseudocode, Complexity & Trade-offs, Quiz Yourself |

Gemma is called with `format="json"` and told the exact keys to return. The UI renders each key as a section.

## Diagram
Gemma returns Mermaid text (flowchart for processes, cycle for loops, labeled structure for biology parts). The UI embeds it with a small HTML component loading Mermaid from a CDN. If the code fails to render, show it as plain text instead of crashing.

## Study Buddy
- Chat history lives in `st.session_state`.
- Each request includes the student's notes in the system prompt: "Answer only from these notes. If it isn't in them, say so."
- "Quiz me" asks one question at a time from the Quiz Yourself section, then checks the answer.

## Error handling
- Ollama not running or `gemma3` missing: show a message with the fix (`ollama pull gemma3`).
- Bad or invalid JSON: retry once, then show a friendly error.
- Empty input: ask the user to paste notes.
- Subject unclear: default to the closest of the three and let the user override with a dropdown.

## Why open-weight / local
Private notes stay on the device, it's free, works offline, and the model can be swapped (change one string).

## Risks
- 4B model may return bad JSON or invalid Mermaid: retry once, fall back to plain text.
- Slow on weak laptops: show a spinner, keep prompts short.
- Time: freeze features Sat 6:30 PM PDT.

## Test plan
Run the three files in `samples/` (bio, math, cs) end to end: detection is correct, all sections render, diagram renders, Study Buddy answers and quizzes.

## Open items
- Who is the real "friend" we're building for?
- Teammate GitHub and DEV usernames.
- Who publishes the DEV post.
