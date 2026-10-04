import ollama

MODEL = "gemma3:4b"


class GemmaError(Exception):
    pass


def _ask(messages, as_json=False):
    """Send messages to Gemma and return the reply text. Raises only GemmaError."""
    try:
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            format="json" if as_json else "",
        )
    except ConnectionError:
        raise GemmaError("Ollama isn't running. Open the Ollama app and try again.")
    except ollama.ResponseError as e:
        if e.status_code == 404:
            raise GemmaError(f"Model missing. Run: ollama pull {MODEL}")
        raise GemmaError(f"Ollama returned an error: {e.error}")

    return response["message"]["content"]
