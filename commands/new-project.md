---
description: Start a new NMIMS MBA project - ask the intake questions, create its own folder, and plan the report and deck
argument-hint: "[optional: student name or topic]"
---
Start a new NMIMS MBA project. Context from the user: $ARGUMENTS

1. Read `AGENTS.md` and `skills/nmims-mba-project/SKILL.md`, then `skills/nmims-mba-project/references/intake.md`.
2. Ask **Round 1** only: project name, project type (Problem-Solving Proposal, Business Plan or Research Project; recommend one if the student is unsure), specialisation. Wait for the answers.
3. Create the folder: `bash skills/nmims-mba-project/scripts/new_project.sh <student-topic> <problem-solving|business-plan|research> --install`. If tools are missing, suggest `/setup`.
4. Ask **Round 2**: the Semester III pre-work submitted on the portal (exact title, description, format, faculty feedback or approval) and any work already done. Ask for the files and save them in `research/student-input/`.
5. Ask **Round 3**: the idea in the student's own words. Then **Round 4** (questions for the chosen type), **Round 5** (offer the survey; skipping is allowed and recorded), **Round 6** (name, SAP ID, exam cycle, guide, deadline). One round at a time.
6. Record every answer in the project's `OPEN_ITEMS.md`, fill `tools/report.config.json`, and draft `report/00_OUTLINE.md` (chapter → rubric → evidence → pages).
7. Show the student the outline and the open questions. Do not write chapters until they confirm the format, title and scope.
