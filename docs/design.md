# NOTE-IT Design Doc

## Problem
Psychology lecture notes are messy and hard to study from. Our friend, a psychology student, wants clean, structured notes, a quick visual, and a way to test themselves, without uploading private notes to a cloud service.

## Goal
Paste psychology notes, get structured study notes, a diagram, and a chatbot that answers from those notes. Everything runs locally.

## Non-goals
Other subjects, 3D models, live mic transcription, handwriting/photo upload. Optional stretch: ElevenLabs read-aloud.

## Flow

```
paste notes -> rewrite into psychology template -> generate diagram -> Study Buddy chat
```

## Components

| File | Job |
|---|---|
| `app.py` | Streamlit UI: input box, tabs (Notes, Diagram, Study Buddy), error messages |
| `gemma.py` | Ollama calls |
| `templates.py` | Psychology template and prompt text |

### `gemma.py` functions
- `rewrite_notes(notes) -> dict` (keys match the template sections)
- `make_diagram(notes_dict) -> str` (Mermaid code)
- `chat(history, notes, question) -> str`

All three raise `GemmaError(message)` with a friendly message on failure. The UI catches only that one.

Model: `gemma3:4b`, kept in one constant `MODEL`.

## Template (JSON keys)

Exact keys, shapes and examples live in **[contract.md](contract.md)**. Summary:

| Section | Shape |
|---|---|
| Key Terms | list of `{term, definition}` |
| Theories & Researchers | list of `{name, summary}` |
| Key Studies | list of `{study, method, findings}` |
| Evaluation | list of strings |
| Real-World Examples | list of strings |
| Quiz Yourself | list of `{q, a}` |

Gemma is called with `format="json"` and told the exact keys to return. If the notes have nothing for a section, it returns an empty list. The UI renders each key as a section and skips empty ones.

## Diagram
Gemma returns Mermaid text: a `flowchart` for models and processes (e.g. stages of memory), or a `mindmap` for a topic overview (theories, studies, terms). The UI embeds it with a small HTML component loading Mermaid from a CDN. If the code fails to render, show it as plain text instead of crashing.

## Study Buddy
- Chat history lives in `st.session_state`.
- Each request includes the student's notes in the system prompt: "Answer only from these notes. If it isn't in them, say so."
- "Quiz me" asks one question at a time from the Quiz Yourself section, then checks the answer against `a`.

## Error handling
- Ollama not running or `gemma3:4b` missing: show a message with the fix (`ollama pull gemma3:4b`).
- Bad or invalid JSON: retry once, then show a friendly error.
- Empty input: ask the user to paste notes.

## Why open-weight / local
Private notes stay on the device, it's free, works offline, and the model can be swapped (change one string).

## Risks
- 4B model may return bad JSON or invalid Mermaid: retry once, fall back to plain text.
- `mindmap` syntax is strict about indentation, so a 4B model may break it more often than `flowchart`. If so, use `flowchart` only.
- Slow on weak laptops: show a spinner, keep prompts short.
- Time: freeze features Sat 6:30 PM PDT.

## Test plan
Run the three files in `samples/` (`memory.txt`, `conditioning.txt`, `social.txt`) end to end: all sections render, diagram renders, Study Buddy answers and quizzes. Then try bad input: empty, very long, and a non-psychology topic.

## Open items
- Our friend's name/course and their reaction (for the DEV post).
- Teammate GitHub and DEV usernames.
- Who publishes the DEV post.
