---
description: Resolve [VERIFY] tags from primary sources and cross-check citations and DOIs
argument-hint: "<project folder>"
---
Verify sources for `projects/$ARGUMENTS`.

1. List every `[VERIFY: ...]` in the report (`grep -rn "\[VERIFY" projects/$ARGUMENTS/report`).
2. Resolve each from a primary source (filings, regulator or government documents, versioned legal PDFs, Crossref) per `skills/nmims-mba-project/references/research-and-citations.md`. Save the source in `research/sources/`. Rewrite the sentence to match what the source says; downgrade to "reported" or remove if only third-party sources exist.
3. Run `python3 skills/nmims-mba-project/scripts/check_citations.py projects/$ARGUMENTS/report --doi` and fix mismatches.
4. Report what was confirmed, changed or removed.
