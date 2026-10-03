import json

import ollama

MODEL = "gemma3:4b"

notes = "Classical conditioning: Pavlov's dogs learned to salivate at a bell paired with food."

prompt = (
    "You turn psychology notes into study notes. "
    'Reply in JSON with one key: "Key Terms", '
    'a list of {"term": ..., "definition": ...}.\n\n'
    f"Notes: {notes}"
)

response = ollama.chat(
    model=MODEL,
    messages=[{"role": "user", "content": prompt}],
    format="json",
)

text = response["message"]["content"]
print("Raw reply:", text)

data = json.loads(text)
for item in data["Key Terms"]:
    print("-", item["term"], ":", item["definition"])
