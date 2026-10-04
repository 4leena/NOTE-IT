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
    with open("samples/expected.json") as f:
        data = json.load(f)
    return data

def make_diagram(notes_dict):
    time.sleep(1)
    return FAKE_DIAGRAM

def chat(history, notes, question):
    time.sleep(1)
    if question == "Quiz me":
        return "Quiz time! What is the unconditioned stimulus in Pavlov's study?"
    return "(fake) You asked: " + question
