---
description: Check a project for plagiarism and copy cases (sources, other projects, web) and fix every finding
---
<!-- Generated from commands/originality-check.md by scripts/sync_agent_files.py. Edit the source, not this file. -->

Arguments from the user, if any, follow the command name.

Run the originality check for `projects/the arguments the user gave`, following `skills/originality-check/SKILL.md`.

1. Make sure every source used is saved in the project's `research/` (ask the student for any they used that are missing).
2. Local check (plagiarism + copy case against every other project):
   `python3 skills/originality-check/scripts/similarity.py projects/the arguments the user gave/report --corpus projects/the arguments the user gave/research --peers projects --exclude-template skills/nmims-mba-project/formats --out projects/the arguments the user gave/output/originality`
3. Web check: `python3 skills/originality-check/scripts/sample_phrases.py projects/the arguments the user gave/report --out projects/the arguments the user gave/output/web_check.md`, then search **every** query as an exact phrase (in parallel where possible), tick it and record `no match (searched <date>)` or `match: <url>; resolved: ...`.
4. Fix findings with `skills/originality-check/references/fixing.md` (rewrite in the student's words, or quote and cite, or cut); then run `/humanise` on changed paragraphs.
5. Verify: `python3 skills/originality-check/scripts/sample_phrases.py --status projects/the arguments the user gave/output/web_check.md` must say COMPLETE.
6. Re-run steps 2-5 after any chapter edit until both pass. Report to the student: local PASS/FAIL and %, web check "N of M phrases searched, X matches, Y unresolved", and the date. Never say the check is done while any phrase is unsearched. Record the numbers in `OPEN_ITEMS.md`.
