# NOTE-IT

Turn messy lecture notes into clean, subject-specific study notes, with a diagram and a study buddy chatbot. Runs fully local with **Gemma** via **Ollama**, so your notes never leave your laptop.

Built for the DEV Hacktoberfest Weekend Challenge ("Build for a Friend"). Prize category: Best Use of Gemma.

## What it does

1. Paste rough notes or a lecture transcript.
2. Gemma detects the subject (Biology, Math, or Computer Science).
3. Gemma rewrites the notes into that subject's template.
4. Gemma generates a Mermaid diagram of the main idea.
5. Ask the Study Buddy questions about your notes, or say "quiz me".

| Subject | Sections |
|---|---|
| Biology | Key Terms, Main Process, Structure & Function, Quiz Yourself |
| Math | Definitions, Theorems & Formulas, Worked Example, Common Mistakes, Quiz Yourself |
| Computer Science | Key Concepts, How It Works, Code/Pseudocode, Complexity & Trade-offs, Quiz Yourself |

## Setup

Requires Python 3.10+ and [Ollama](https://ollama.com/download).

```bash
git clone https://github.com/4leena/NOTE-IT.git
cd NOTE-IT
pip install -r requirements.txt
ollama pull gemma3
streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501). Try a file from `samples/` to start.

## Project layout

```
app.py            Streamlit UI
gemma.py          Ollama calls: detect subject, rewrite notes, diagram, chat
templates.py      Subject templates and prompts
samples/          Example notes (bio, math, cs)
docs/design.md    Design doc
```

## Tech

Python, Streamlit, Ollama (`gemma3` 4B), Mermaid.

## Team

- [@4leena](https://github.com/4leena)
- Teammate: TBD

## License

MIT
