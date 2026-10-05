import json
import time

FAKE_DIAGRAM = """flowchart TD
    A[Food] --> B[Salivation]
    C[Bell] --> D[No response]
    A --- C
    C --> E[Salivation after pairing]"""

class GemmaError(Exception):
    pass

def rewrite_notes(notes):
    time.sleep(2)
    if "ERROR" in notes:
        raise GemmaError("Ollama isn't running. Open the Ollama app and try again.")
    with open("samples/expected.json") as f:
        data = json.load(f)
    return data

def make_diagram(notes_dict):
    time.sleep(1)
    return FAKE_DIAGRAM

def chat(history, notes, question, mode="tutor"):
    time.sleep(1)
    if "ERROR" in question:
        raise GemmaError("Study Buddy couldn't reach Gemma. Check Ollama is running and try again.")
    return f"({mode}) You asked: " + question

def read_handwriting(image):
    time.sleep(1)
    return "Sensation -> the sensory system detects a stimulus.\nPerception -> organizing and interpreting the information."
