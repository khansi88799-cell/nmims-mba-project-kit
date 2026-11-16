---
description: Build the draft PDF, financial tables and viva deck for a project and inspect them
---
<!-- Generated from commands/build.md by scripts/sync_agent_files.py. Edit the source, not this file. -->

Arguments from the user, if any, follow the command name.

Build `projects/the arguments the user gave`.

1. `cd projects/the arguments the user gave/tools`. If `model.json` exists: `npm run model`.
2. `npm run build` (draft). Note the page count and open placeholders.
3. If `presentation/deck.json` exists: `npm run deck`, then `npm run deck:pdf` (LibreOffice) or `npm run deck:qa`.
4. Render pages and look at them: cover, contents, every figure, footer; every slide. Fix anything wrong.
5. Report: pages (30-60 required), open placeholders, issues found and fixed.
