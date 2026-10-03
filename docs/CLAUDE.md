# CLAUDE.md

## Project
NOTE-IT: Streamlit app that turns messy psychology lecture notes into structured study notes (one psychology template, no subject detection), a Mermaid diagram, and a Study Buddy chat. Built for a friend who studies psychology. Local-only, using Gemma (`gemma3:4b`) via Ollama. Hackathon project, deadline Sun Oct 4, 11:59 PM PDT. See `docs/design.md`.

## How to help (important)
We are building this ourselves. Default to:
- Explaining concepts and pointing to docs.
- Reviewing our code and helping debug errors we paste.
- Hints first, full answers only if we ask.
- **Do not write or edit files, or write full code, unless we explicitly ask.**

## Stack
Python 3.10+, Streamlit, `ollama` Python library, model `gemma3:4b` (keep it in one `MODEL` constant). Use `format="json"` for structured output. Mermaid is rendered in the browser through a small HTML component.

## Scope
In: psychology template, Mermaid diagram, Study Buddy.
Out: 3D models, live mic, handwriting/photo upload. Optional stretch only after the core works: ElevenLabs read-aloud.

## Conventions
- Keep it simple. Small functions, no extra abstractions.
- Gemma logic lives in `gemma.py` and `templates.py`; UI lives in `app.py`. Avoid editing the same file at once.
- Always handle Ollama errors (not running, model missing) with a friendly message.
- Commits are short and clear ("Add psychology template"). `git pull` before starting, push small changes often.

## Run
```bash
ollama pull gemma3:4b
streamlit run app.py
```
