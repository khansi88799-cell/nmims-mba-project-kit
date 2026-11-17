---
description: Final checks and the submission outputs - the project PDF and the viva PPT
mode: agent
---
<!-- Generated from commands/finalise.md by scripts/sync_agent_files.py. Edit the source, not this file. -->

Finalise `projects/${input:args}`. Work through this list and stop at the first failure.

1. Cover: `tools/report.config.json` has the exact registered title (≤ 20 words), format, name, SAP ID, specialisation, exam cycle, guide. Ask the student to confirm.
2. Every `[NEEDS]` and `[VERIFY]` resolved (ask the student for the remaining NEEDS).
3. `/humanise` targets met for every chapter.
4. `/originality-check` passes after the last edit: local PASS, and the web check COMPLETE (`sample_phrases.py --status`: every phrase searched, every match resolved).
5. Citations: `check_citations.py --doi` clean.
6. Numbers consistent across summary, chapters, appendix and deck.
7. Set `"final": true` in `tools/report.config.json`; `npm run build`. It must succeed (it refuses if placeholders remain, the originality report is failing or stale, or the web check is incomplete or stale).
8. Copy the PDF to `output/<Name>_<SAPID>_MBA_Project.pdf`. Build the deck (`npm run deck`, `npm run deck:pdf`).
9. Look at every page and slide one last time.
10. Hand over both files, remind the student to read everything before uploading on the portal (Student Zone > Exam > Project Submission, PDF only), and log completion in `OPEN_ITEMS.md`.
