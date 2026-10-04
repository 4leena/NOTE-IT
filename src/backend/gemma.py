import json
import re

import ollama

import templates

MODEL = "gemma3:4b"
# Ollama settings to try in order. If the GPU runs out of memory, fall back to a
# smaller context window, then to the CPU (slower, but it never runs out of memory).
ATTEMPTS = [{"num_ctx": 8192}, {"num_ctx": 4096}, {"num_ctx": 4096, "num_gpu": 0}]
MAX_NOTES_CHARS = 12000  # longer notes would not fit in the context window
MAX_DIAGRAM_LINES = 15  # first line is "flowchart TD", then up to 14 connections


class GemmaError(Exception):
    pass


def _ask(messages, as_json=False, max_tokens=None):
    """Send messages to Gemma and return the reply text. Raises only GemmaError.

    max_tokens caps the reply length, so a rambling answer can't run on forever.
    """
    for settings in ATTEMPTS:
        options = dict(settings)
        if max_tokens:
            options["num_predict"] = max_tokens
        try:
            response = ollama.chat(
                model=MODEL,
                messages=messages,
                format="json" if as_json else "",
                options=options,
            )
            return response["message"]["content"]
        except ConnectionError:
            raise GemmaError("Ollama isn't running. Open the Ollama app and try again.")
        except ollama.ResponseError as e:
            if e.status_code == 404:
                raise GemmaError(f"Model missing. Run: ollama pull {MODEL}")
            if "out of memory" not in str(e.error).lower():
                raise GemmaError(f"Ollama returned an error: {e.error}")
            # out of memory: try the next, lighter setting

    raise GemmaError(
        "Your computer ran out of memory for Gemma. Close other apps "
        "(games, video), run `ollama stop gemma3:4b`, and try again."
    )


def _parse_notes(text):
    """Turn Gemma's reply into the notes dict, or return None if it is unusable."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("Topic"), str):
        return None

    notes = {"Topic": data["Topic"]}
    for section, fields in templates.SECTIONS.items():
        items = data.get(section, [])
        if not isinstance(items, list):
            return None
        for item in items:
            if fields is None and not isinstance(item, str):
                return None
            if fields is not None and not (
                isinstance(item, dict) and all(isinstance(item.get(f), str) for f in fields)
            ):
                return None
        notes[section] = items
    return notes


def rewrite_notes(notes):
    """Messy psychology notes -> dict with Topic plus the six sections."""
    if not notes.strip():
        raise GemmaError("Paste some notes first.")

    messages = [
        {"role": "system", "content": templates.REWRITE_PROMPT},
        {"role": "user", "content": notes[:MAX_NOTES_CHARS]},
    ]
    for attempt in range(2):  # one retry if the JSON is unusable or Ollama stumbles
        try:
            result = _parse_notes(_ask(messages, as_json=True, max_tokens=3000))
        except GemmaError:
            if attempt == 1:
                raise
            continue
        if result:
            return result
    raise GemmaError("Gemma's answer wasn't in the right format. Please try again.")


def _notes_outline(notes_dict):
    """A short text version of the notes, so the diagram prompt stays small."""
    lines = [f"Topic: {notes_dict.get('Topic', '')}"]
    for t in notes_dict.get("Key Terms", []):
        lines.append(f"Term: {t['term']}")
    for t in notes_dict.get("Theories & Researchers", []):
        lines.append(f"Theory: {t['name']} - {t['summary']}")
    for s in notes_dict.get("Key Studies", []):
        lines.append(f"Study: {s['study']} - {s['findings']}")
    return "\n".join(lines)


def _clean_label(label):
    """Keep letters, numbers and spaces only, since other characters break Mermaid."""
    label = re.sub(r"['’]", "", label)  # Bartlett's -> Bartletts, not "Bartlett s"
    return " ".join(re.sub(r"[^\w ]", " ", label).split())


def _clean_mermaid(text):
    """Cut code fences and chatter, fix labels, or return None if there is no diagram."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith(("flowchart", "mindmap")):
            lines = lines[i:]
            break
    else:
        return None
    for i, line in enumerate(lines):  # a closing fence ends the diagram
        if line.strip().startswith("```"):
            lines = lines[:i]
            break

    if lines[0].strip().startswith("flowchart"):
        skip = ("style", "classDef", "class ", "click", "subgraph", "end", "%%")
        lines = [l for l in lines if not l.strip().startswith(skip)]
        lines = lines[:MAX_DIAGRAM_LINES]
        text = "\n".join(lines)
        text = re.sub(r"\[([^\]\n]*)\]", lambda m: f"[{_clean_label(m.group(1))}]", text)
        text = re.sub(r"\{([^}\n]*)\}", lambda m: f"[{_clean_label(m.group(1))}]", text)
        return text.strip()
    return "\n".join(lines).strip()


def make_diagram(notes_dict):
    """Notes dict -> raw Mermaid code starting with flowchart or mindmap."""
    messages = [
        {"role": "system", "content": templates.DIAGRAM_PROMPT},
        {"role": "user", "content": _notes_outline(notes_dict)},
    ]
    for attempt in range(2):  # one retry if there is no usable diagram
        try:
            diagram = _clean_mermaid(_ask(messages, max_tokens=400))
        except GemmaError:
            if attempt == 1:
                raise
            continue
        if diagram:
            return diagram
    raise GemmaError("Gemma couldn't draw the diagram. Try Regenerate.")


def chat(history, notes, question, mode="tutor"):
    """One Study Buddy reply, answered from the notes in the style of `mode`."""
    system = templates.CHAT_MODES.get(mode, templates.CHAT_MODES["tutor"])
    messages = (
        [{"role": "system", "content": system + "\nNOTES:\n" + notes[:MAX_NOTES_CHARS]}]
        + history[-10:]  # keep the prompt short so replies stay fast
        + [{"role": "user", "content": question}]
    )
    return _ask(messages).strip()
