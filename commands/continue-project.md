---
description: Resume an existing project - read its log, report status and the next steps
argument-hint: "<project folder name under projects/>"
---
Resume the project `projects/$ARGUMENTS` (if empty, list the folders in `projects/` and ask which one).

1. Read `AGENTS.md`, the project's `AGENTS.md`, `OPEN_ITEMS.md` and `report/00_OUTLINE.md`.
2. Report status in a short table: intake rounds done, survey status, chapters drafted / to write, open `[NEEDS]` and `[VERIFY]` counts (`grep -c` in report/), last originality result, last build page count.
3. List the questions still waiting for the student and ask them.
4. Propose the next 1-3 steps from the workflow in `skills/nmims-mba-project/SKILL.md` and continue when the student agrees.
Never use material from any other project folder.
