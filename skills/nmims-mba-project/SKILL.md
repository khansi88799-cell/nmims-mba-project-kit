---
name: nmims-mba-project
description: End-to-end method for an NMIMS CDOE online MBA Semester IV project (6 credits) - Problem-Solving Proposal, Business Plan or Research Project - delivered as a submission-ready PDF and a viva PowerPoint deck. Runs a structured intake (project name and type, Semester III pre-work from the portal, work already done, the idea in the student's own words, format-specific questions, survey offer, cover details), creates a separate project folder per student, writes chapters mapped to each marking rubric with verified evidence and APA citations, builds a reproducible financial model, keeps the writing in the student's voice, checks originality (plagiarism and copy cases), and builds the PDF with the official NMIMS cover, contents and Page X of Y. Use for any NMIMS (or similar Indian university) MBA project, dissertation, business plan or capstone report.
metadata:
  version: 2.1.0
  updated: 2026-11-17
---

# NMIMS MBA project

Deliver two files the university will accept: the project **PDF** (main document, annexures inside) and the viva **PPT**. The student stays the author: their idea, their organisation, their data, their experiences, their decisions. This skill supplies structure, research discipline, writing quality and the build.

`<skill>` = the folder holding this file. `<kit>` = the repository root (`<skill>/../..`).

## Rule zero: one folder per project, never mixed
Each student's project lives in `<kit>/projects/<student>-<topic>/` (git-ignored, never published). Never copy text, data, figures, numbers or reflections between projects. The `originality-check` skill compares every project against every other one.

## Workflow

1. **Intake, round 1** (`references/intake.md`): project name, project type, specialisation. Then create the folder:
   `bash <skill>/scripts/new_project.sh <student-topic> <problem-solving|business-plan|research> --install`
2. **Intake, rounds 2-6**: Semester III pre-work from the portal (title, description, feedback), work already done (save files to `research/student-input/`), the idea in their own words, type-specific questions, **survey offer** (`references/survey.md`; skipping is allowed and recorded), cover details. Record all answers in `OPEN_ITEMS.md`. Fill `tools/report.config.json`.
3. **Fatal-risk check** (`references/guidelines-summary.md`): format matches registration; title ≤ 20 words and identical to the portal; specialisation fit; Problem-Solving has a real organisation.
4. **Plan**: fill `report/00_OUTLINE.md` (chapter → rubric → evidence → page budget). Ask the student to confirm scope and organisation naming.
5. **Evidence** (`references/research-and-citations.md`): primary sources first; save every source used into `research/` (the originality check compares against it); `[NEEDS]` / `[VERIFY]` instead of guesses.
6. **Numbers**: copy `tools/model.example.json` to `tools/model.json`, replace every value with the student's assumptions and their basis, `npm run model`, include the generated tables.
7. **Write** chapters in `report/` following each skeleton's rubric note: analysis chapters first, reflection from the student's answers (`references/reflection-questions.md`), summary or abstract last. Prose, not bullet walls; tables and figures numbered, captioned and discussed.
8. **Voice**: `humaniser` skill in academic mode, then `bash <skill>/scripts/lint_report.sh <project>/report` (AI vocabulary < 3/1k words, sentence-length CV 0.45-0.80, no em dashes, no hidden characters). Never invent experiences to add voice.
9. **Originality**: run the `originality-check` skill (local sources + all other projects + web phrase check) and fix every finding until it passes. Search every phrase in the web checklist, not a sample, and confirm with `sample_phrases.py --status`. Report "N of M phrases searched" to the student; never call the check done while it is partial.
10. **Build and inspect**: `npm run build`; look at the rendered pages (`references/build-and-tools.md`); 30-60 pages; `python3 <skill>/scripts/check_citations.py <project>/report --doi`.
11. **Deck**: copy `presentation/deck.example.json` to `presentation/deck.json`, fill it from the final report (`references/deck-format.md`), `npm run deck`, preview (`npm run deck:pdf` with LibreOffice, or `deck:qa`), look at every slide.
12. **Final**: resolve all `[VERIFY]` and `[NEEDS]`; set `"final": true`; `npm run build` (blocked unless placeholders are gone, the originality report passes, and the web check is complete, with both reports newer than the chapters). Deliver `output/<Name>_<SAPID>_MBA_Project.pdf` and the `.pptx` (plus its PDF). Ask the student to read everything before submitting.

Ask the student whenever a decision is theirs. Keep `OPEN_ITEMS.md` current: answers, decisions, progress, survey status, originality results.

## Reference files
| File | Use |
|---|---|
| `references/intake.md` | The question rounds, in order |
| `references/survey.md` | Designing, running, using (or skipping) the survey |
| `references/guidelines-summary.md` | University rules and layout |
| `references/formats-and-rubrics.md` | Templates and marking rubrics for the three types |
| `references/research-and-citations.md` | Evidence and APA rules, sources that work |
| `references/reflection-questions.md` | Questions for the reflection chapter |
| `references/deck-format.md` | Viva deck storyline and `deck.json` slide types |
| `references/build-and-tools.md` | Commands, build internals, solved gotchas |
| `references/lessons-learned.md` | Mistakes not to repeat |
| `references/improvement-areas.md` | Known limits of this method |
| `references/cover-options.html` | Cover designs (Option A is the built one) |
| `references/NMIMS_Project_Guidelines_Sem3_Sem4.pdf` | The university's document |
| `formats/<type>/` | Chapter skeletons copied into each project |
| `template/` | Build tools, logos, deck and model examples |
