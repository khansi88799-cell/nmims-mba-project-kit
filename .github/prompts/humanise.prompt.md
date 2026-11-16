---
description: Make a chapter or the whole report read as the student's own natural writing (academic mode) and measure it
mode: agent
---
<!-- Generated from commands/humanise.md by scripts/sync_agent_files.py. Edit the source, not this file. -->

Humanise: ${input:args}

1. Follow `skills/humaniser/SKILL.md` in **academic mode** (`skills/humaniser/references/academic-mba.md`). Keep every fact, number and citation exactly; never invent experiences, examples or sources.
2. Measure before and after: `python3 skills/humaniser/scripts/ai_lint.py <chapter> --sections` (or `bash skills/nmims-mba-project/scripts/lint_report.sh <project>/report` for all chapters).
3. Targets: AI vocabulary < 3 per 1,000 words, sentence-length CV 0.45-0.80, no em dashes, no curly quotes, no bold-label bullet lists in body text.
4. Strip hidden Unicode: `python3 skills/clean-user-facing-text/scripts/clean_text.py <file> -o <file> --stats --no-normalize-spaces`.
5. Report the before/after numbers per chapter.
