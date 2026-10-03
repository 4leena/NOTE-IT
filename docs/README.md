# NOTE-IT

Turn messy psychology lecture notes into clean study notes, with a diagram and a study buddy chatbot. Runs fully local with **Gemma** via **Ollama**, so your notes never leave your laptop.

Built for the DEV Hacktoberfest Weekend Challenge ("Build for a Friend"): our friend studies psychology. Prize category: Best Use of Gemma.

## What it does

1. Paste rough psychology notes or a lecture transcript.
2. Gemma rewrites them into a psychology study template.
3. Gemma generates a Mermaid diagram of the main idea.
4. Ask the Study Buddy questions about your notes, or say "quiz me".

Template sections: Key Terms, Theories & Models, Key Studies, Evaluation, Real-Life Examples, Quiz Yourself.

## Setup

Requires Python 3.10+ and [Ollama](https://ollama.com/download).

```bash
git clone https://github.com/4leena/NOTE-IT.git
cd NOTE-IT
pip install -r requirements.txt
ollama pull gemma3:4b
streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501). Try a file from `samples/` to start.

## Project layout

```
app.py            Streamlit UI
gemma.py          Ollama calls: rewrite notes, diagram, chat
templates.py      Psychology template and prompts
samples/          Example psychology notes
docs/design.md    Design doc
```

## Tech

Python, Streamlit, Ollama (`gemma3:4b`), Mermaid.

## Team

- [@4leena](https://github.com/4leena)
- Teammate: TBD

## License

MIT
