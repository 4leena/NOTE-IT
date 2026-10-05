# NOTE-IT: Project Handoff (Hacktoberfest Weekend Challenge)

## The challenge
- *Event:* DEV Hacktoberfest Weekend Challenge: "Build for a Friend"
  https://dev.to/challenges/hacktoberfest-weekend-2026-10-01
- *Prompt:* build something NEW with open-source AI at its core (open-weight model / local inference)
- *Theme:* solve a real problem for one real person, then hand it to them and share what they said
- *DEADLINE: Sunday Oct 4, 11:59 PM PDT.* Target: publish by 7:45 PM PDT.
- *Team:* up to 4 people. ONE person publishes the DEV post and lists teammates' DEV usernames (everyone needs a DEV account).
- *Judging:* Writing quality counts MOST, then relevance to theme, creativity, technical execution, partner tech (optional).
- *Prize category we're entering:* Best Use of Gemma
- *Rules:* project must be started this weekend; AI coding tools allowed; credit any significant code you didn't write; 18+.

## The app
*NOTE-IT* turns messy lecture notes into clean, subject-specific study notes.
1. User pastes rough notes or a lecture transcript
2. Gemma detects the subject (Biology / Math / Computer Science)
3. Gemma rewrites the notes into that subject's template
   - Bio: Key Terms, Main Process, Structure & Function, Quiz Yourself
   - Math: Definitions, Theorems & Formulas, Worked Example, Common Mistakes, Quiz Yourself
   - CS: Key Concepts, How It Works, Code/Pseudocode, Complexity & Trade-offs, Quiz Yourself
4. Gemma generates a *Mermaid diagram* (flowchart / cycle / labeled structure)
5. *Study Buddy chatbot* answers students' questions grounded in their own notes, and can quiz them ("quiz me")

*Out of scope (cut on purpose):* 3D models, live mic transcription, handwriting/photo upload. Stretch ONLY if core is done: optional ElevenLabs "read aloud" toggle (partner credits).

## Stack
- Python 3.10+, *Streamlit* (UI), *Ollama* Python library, model *gemma3* (4B)
- Ask Gemma for *JSON output* (format="json") to fill templates reliably
- Mermaid rendered in the browser via a small HTML component
- Docs: https://github.com/ollama/ollama-python · https://docs.streamlit.io

## Current status (Sat Oct 3, ~12:45 PM)
- ✅ Repo created: https://github.com/4leena/NOTE-IT (public, README, MIT license, description)
- ✅ Name decided: NOTE-IT
- ⏳ Collaborator invite being sent
- ⬜ ollama pull gemma3 + hello-world (Gemma classifies one sentence of notes)
- ⬜ Everything else below
- ⚠️ We're a bit behind the original plan, so keep scope tight.

## Plan for the rest of the weekend (PDT)
*Saturday*
- Now–2:30: setup on both laptops, hello-world working, write 3 sample notes (bio/math/cs) in samples/
- 2:30–5:30: core pipeline end to end (detect → template → display), diagram rendering, study buddy chat
- 5:30–6:30: test all 3 samples, fix bugs, friendly error messages
- *6:30 PM: FEATURE FREEZE.* Push. Write 3 bullets on "what was hard / what we learned."

*Sunday*
- 10–11 AM: bug fixes only, README setup steps (test them literally)
- 11–12:45: screenshots, 1–2 min demo video (upload to YouTube unlisted)
- 12:45–1:30: hand it to the real "friend," write down their exact reaction
- 3–6 PM: write DEV post using the official template
- 6–7:45 PM: final check and PUBLISH. Tags: #devchallenge #weekendchallenge #hf26challenge

## Suggested split (avoid editing the same file at once)
- *Person A:* Gemma logic (subject detection, templates, JSON prompts, Mermaid generation)
- *Person B:* Streamlit UI (input, tabs, diagram rendering, Study Buddy chat)
- Both: test with samples, demo video, DEV post

## Git workflow
- git pull before starting, commit + push small working changes often
- Use branches if touching the same file: git checkout -b study-buddy, then merge
- Commit message style: short and clear ("Add subject detection")

## DEV post outline (template sections)
What I Built · Demo (video + screenshots) · Code ({% github 4leena/NOTE-IT %}) · How I Built It · Why Open Innovation Matters (private notes, free, offline, swappable model) · Prize Categories: Best Use of Gemma

## Open decisions
- [ ] Who is the real "friend" we're building for? (needed for the post)
- [ ] Friend/teammate's GitHub + DEV usernames
- [ ] Who publishes the post

## How we want help from Claude
We're building this OURSELVES. Explain concepts, point to docs, review our code, and help debug errors we paste. Give hints before full answers. Don't write files or full code unless we explicitly ask.