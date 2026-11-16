---
description: Check a project for plagiarism and copy cases (sources, other projects, web) and fix every finding
argument-hint: "<project folder>"
---
Run the originality check for `projects/$ARGUMENTS`, following `skills/originality-check/SKILL.md`.

1. Make sure every source used is saved in the project's `research/` (ask the student for any they used that are missing).
2. Local check (plagiarism + copy case against every other project):
   `python3 skills/originality-check/scripts/similarity.py projects/$ARGUMENTS/report --corpus projects/$ARGUMENTS/research --peers projects --exclude-template skills/nmims-mba-project/formats --out projects/$ARGUMENTS/output/originality`
3. Web check: `python3 skills/originality-check/scripts/sample_phrases.py projects/$ARGUMENTS/report --out projects/$ARGUMENTS/output/web_check.md`, then search every query as an exact phrase and record the result.
4. Fix findings with `skills/originality-check/references/fixing.md` (rewrite in the student's words, or quote and cite, or cut); then run `/humanise` on changed paragraphs.
5. Re-run until PASS. Record the numbers in `OPEN_ITEMS.md`.
