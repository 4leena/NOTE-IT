# NOTE-IT Contract

The one place both halves must match. Person A builds `gemma.py` to this; Person B builds `app.py` (against `fake_gemma.py`) to this. **Don't change anything here without telling each other.**

## Model

```python
MODEL = "gemma3:4b"   # ollama list → ID a2af6cc3eb7f
```

## Functions in `gemma.py`

Three functions. No subject detection (psychology only).

### `rewrite_notes(notes: str) -> dict`
- `notes`: the raw text the user pasted.
- Returns the template dict below, with **all 6 keys always present**. A section with nothing in the notes is `[]`.

### `make_diagram(notes_dict: dict) -> str`
- `notes_dict`: the dict returned by `rewrite_notes`.
- Returns **raw Mermaid code only**: no ```` ``` ```` fences, no explanation text. Starts with `flowchart` or `mindmap`.

### `chat(history: list, notes: str, question: str) -> str`
- `history`: earlier messages, oldest first, **not** including `question`:
  `[{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]`
- `notes`: the raw pasted text (same string given to `rewrite_notes`).
- `question`: the new user message. The "Quiz me" button sends the literal text `"Quiz me"`.
- Returns the reply text. The UI appends both `question` and the reply to `history`.

### `GemmaError`
```python
class GemmaError(Exception):
    pass
```
- Defined in `gemma.py`. Every function raises **only** this, with a friendly message, e.g. `GemmaError("Ollama isn't running. Open the Ollama app and try again.")`.
- Covers: Ollama not running, model missing, bad JSON after one retry.
- The UI catches `gemma.GemmaError` and shows it with `st.error`. **`fake_gemma.py` must define `GemmaError` too**, so the same `except` works before and after the swap.

## Template (exact JSON keys)

Copy key names exactly, including capitals, spaces and `&`.

| Key | Shape |
|---|---|
| `"Key Terms"` | list of `{"term": str, "definition": str}` |
| `"Theories & Researchers"` | list of `{"name": str, "summary": str}` |
| `"Key Studies"` | list of `{"study": str, "method": str, "findings": str}` |
| `"Evaluation"` | list of str |
| `"Real-World Examples"` | list of str |
| `"Quiz Yourself"` | list of `{"q": str, "a": str}` |

### Example `rewrite_notes` output

```json
{
  "Key Terms": [
    {"term": "Classical conditioning", "definition": "Learning by associating a neutral stimulus with one that already causes a response."}
  ],
  "Theories & Researchers": [
    {"name": "Pavlov", "summary": "Showed dogs learn to salivate to a bell paired with food."}
  ],
  "Key Studies": [
    {"study": "Pavlov (1927)", "method": "Lab experiment with dogs, bell paired with food", "findings": "The bell alone came to trigger salivation."}
  ],
  "Evaluation": [
    "Animal studies may not generalise to humans."
  ],
  "Real-World Examples": [
    "Feeling hungry when you hear a snack wrapper."
  ],
  "Quiz Yourself": [
    {"q": "What is the unconditioned stimulus in Pavlov's study?", "a": "The food."}
  ]
}
```

### Example `make_diagram` output

```
flowchart TD
    A[Food] --> B[Salivation]
    C[Bell] --> D[No response]
    A --- C
    C --> E[Salivation after pairing]
```

## Shared files

| Path | Who | What |
|---|---|---|
| `samples/memory.txt`, `samples/conditioning.txt`, `samples/social.txt` | Both | Messy psychology notes for testing and the demo |
| `samples/expected.json` | A writes | One full `rewrite_notes` output, used by `fake_gemma.py` |
| `docs/contract.md` | Both | This file |

## File ownership

- **A:** `gemma.py`, `templates.py`, `try_llm.py`
- **B:** `app.py`, `fake_gemma.py`
- Swap at integration: in `app.py`, `import fake_gemma as gemma` → `import gemma`.
