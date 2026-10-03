# CLAUDE.md

## Project
NOTE-IT: Streamlit app that turns messy lecture notes into subject-specific study notes (Bio / Math / CS), a Mermaid diagram, and a Study Buddy chat. Local-only, using Gemma (`gemma3` 4B) via Ollama. Hackathon project, deadline Sun Oct 4, 11:59 PM PDT. See `docs/design.md`.

## How to help (important)
We are building this ourselves. Default to:
- Explaining concepts and pointing to docs.
- Reviewing our code and helping debug errors we paste.
- Hints first, full answers only if we ask.
- **Do not write or edit files, or write full code, unless we explicitly ask.**

## Stack
Python 3.10+, Streamlit, `ollama` Python library, model `gemma3`. Use `format="json"` for structured output. Mermaid is rendered in the browser through a small HTML component.

## Scope
In: subject detection, templates, Mermaid diagram, Study Buddy.
Out: 3D models, live mic, handwriting/photo upload. Optional stretch only after the core works: ElevenLabs read-aloud.

## Conventions
- Keep it simple. Small functions, no extra abstractions.
- Gemma logic lives in `gemma.py` and `templates.py`; UI lives in `app.py`. Avoid editing the same file at once.
- Always handle Ollama errors (not running, model missing) with a friendly message.
- Commits are short and clear ("Add subject detection"). `git pull` before starting, push small changes often.

## Run
```bash
ollama pull gemma3
streamlit run app.py
```
