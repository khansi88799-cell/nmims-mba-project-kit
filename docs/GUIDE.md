# Guide: from idea to submission

For students and the people helping them. With an agent app, each step is one command; without one, run the commands shown.

## 0. One-time setup
```bash
bash scripts/setup.sh                 # asks before installing anything
python3 scripts/sync_agent_files.py   # makes skills and commands visible to every agent app
```

## 1. Start a project: `/new-project`
The agent asks, in rounds:
1. **Project**: name, type (Problem-Solving Proposal / Business Plan / Research Project), specialisation.
2. **Pre-work and existing work**: the Semester III pre-work submitted on the portal (exact title, description, faculty feedback), the registered title, and any drafts, notes, data or decks already made.
3. **Your idea in your own words**: the problem, who it affects, why it matters to you, the solution you have in mind.
4. **Questions for your project type** (organisation and data; or customers, pricing and capital; or research question and sample).
5. **Survey**: yes, already have one, or skip.
6. **Cover details**: name, SAP ID, exam cycle, faculty guide, deadline.

It creates `projects/<you>-<topic>/` (manual: `bash skills/nmims-mba-project/scripts/new_project.sh <you-topic> <type> --install`) and records everything in `OPEN_ITEMS.md`.

Answer honestly and briefly. "I don't know" is a fine answer; the agent marks it and comes back to it.

## 2. Survey (optional): `/survey <folder>`
You get a paste-ready form for Google Forms or Microsoft Forms. Share it, collect 30-50 responses, export the CSV into `research/survey/`. Skipping is allowed (a Research Project needs primary data, so the agent will remind you).

## 3. Write: `/write-chapter <folder> <chapter>`
Chapters are written in this order: analysis chapters, then reflection (from your answers), then the executive summary or abstract. Every source used is saved in `research/sources/`. Anything only you can answer appears as a yellow `[NEEDS: ...]` in the draft PDF.

## 4. Numbers (Business Plan and Problem-Solving)
Edit `tools/model.json` (start from `model.example.json`) with your assumptions and their basis, then `npm run model` in `tools/`. The tables go into the financial chapter and the appendix.

## 5. Voice and originality
- `/humanise <folder>`: academic, natural writing; measured before and after.
- `/originality-check <folder>`: compares your report with your sources, with every other project in the kit (copy-case check) and with the web (every sampled phrase is searched as an exact phrase, not just a few). Fix every finding (rewrite in your words, or quote and cite). The agent reports the local % and "N of M phrases searched"; the final build waits until both are complete.

## 6. Build and review: `/build <folder>`
Draft PDF in `output/`, deck in `presentation/` (fill `presentation/deck.json` from the report first). Read both fully.

## 7. Finalise: `/finalise <folder>`
Final checks, then the submission PDF `output/<Name>_<SAPID>_MBA_Project.pdf` and the deck. Upload the PDF on the student portal (Student Zone > Exam > Project Submission) after registering and paying the project fee. PDF only; annexures inside it.

## Other operating systems
- **Linux**: install `nodejs npm python3 python3-venv chromium libreoffice poppler-utils`; set fonts in `tools/report.config.json` to Arial or Carlito paths (e.g. `/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf`); use `pdftoppm` instead of `raster.swift`.
- **Windows**: use WSL, or install Node, Python, Chrome and LibreOffice with winget; set `CHROME_PATH`; run `python scripts/sync_agent_files.py --copy` (symlinks need admin rights); set font paths to `C:/Windows/Fonts/calibri.ttf` etc.

## Troubleshooting
| Symptom | Fix |
|---|---|
| "Final build blocked: originality..." | Run `/originality-check` after your last edit |
| "Final build blocked: web check not complete" | Search the phrases still unticked in `output/web_check.md`, then `sample_phrases.py --status` |
| "Final build blocked: fill cover fields" | Complete `tools/report.config.json` |
| Fonts look different / page count jumped | Calibri missing (Word not installed); Arial is used instead |
| A diagram says "Unsupported markdown: list" | A Mermaid label starts with "1. "; write "Step 1:" |
| Deck charts missing in preview | Quick Look cannot draw charts; use `npm run deck:pdf` (LibreOffice) |
| Agent app does not show the commands | Run `python3 scripts/sync_agent_files.py` and restart the app |
