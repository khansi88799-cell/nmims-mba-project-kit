---
name: originality-check
description: Check a report for plagiarism (text copied or closely paraphrased from web pages, papers, reports or other sources without quotation and citation) and for copy cases (two students' projects that are too similar, reuse of another project or of template text). Runs a local similarity engine against the project's sources and every other project in the workspace, samples distinctive sentences for exact-phrase web searches, checks that quotations are cited, and guides rewriting until the report is original. Use before any university submission, when a student asks for a plagiarism or similarity check, or when several projects are produced in the same workspace.
metadata:
  version: 1.1.0
  updated: 2026-11-17
---

# Originality check: plagiarism and copy cases

Universities scan submissions against the web, published sources, Gen-AI output and **other students' submissions**. Two different failures are checked here:

| Scenario | What it looks like | Caught by |
|---|---|---|
| **Plagiarism** | Sentences lifted or lightly reworded from a source; quotes without quotation marks or citation; ideas or numbers used without credit | Local check against `research/` + web phrase check |
| **Copy case** | Two projects share passages, structure-plus-wording, data, reflections or examples; a project reuses another project or the worked example; template guidance left in the text | Local check against every other project (`--peers`) |

`<skill>` below is the folder holding this file; `<kit>` is the repository root (`<skill>/../..`).

## Workflow (run per project, before every final build)

1. **Collect the sources.** Save every source used (downloaded PDFs, saved web pages as .html or .txt, notes, survey exports) under the project's `research/`. The local check can only compare against what it is given.
2. **Local check** (plagiarism + copy case in one run):
   ```bash
   python3 <skill>/scripts/similarity.py <project>/report \
     --corpus <project>/research \
     --peers <kit>/projects \
     --exclude-template <kit>/skills/nmims-mba-project/formats \
     --out <project>/output/originality
   ```
   It writes `output/originality.md` (readable) and `output/originality.json` (read by the final build gate). Exit code 2 means a threshold was crossed.
3. **Web check (all phrases, every time).**
   ```bash
   python3 <skill>/scripts/sample_phrases.py <project>/report --out <project>/output/web_check.md
   ```
   Search **every** query in the checklist as an exact phrase with the web search tool; do not stop after a sample of them. Send the searches in parallel where the tool allows it. Tick the box and record each result on its `result:` line:
   - `no match (searched YYYY-MM-DD)`: the phrase does not appear, or results are only the cited source or coverage of it in different wording (say so in brackets);
   - `match: <url>; resolved: rewritten | quoted and cited | cut (searched YYYY-MM-DD)`: after fixing it with step 4.
   Add more queries (`--per-chapter 6`) for chapters that lean on sources (literature review, situational analysis). Re-running the sampler after edits keeps results already recorded, so only new phrases need searching.
4. **Fix every finding** with `references/fixing.md`: rewrite in the student's own words and structure (then run the `humaniser` skill in academic mode), or quote and cite, or cut. Never "fix" similarity by inventing a citation or changing a few words.
5. **Verify the web check:** `python3 <skill>/scripts/sample_phrases.py --status <project>/output/web_check.md`. It writes `web_check.json`, which the final build reads, and exits 2 while any phrase is unsearched or any match is unresolved.
6. **Re-run** steps 2-5 after every edit to the chapters until both pass. Record the numbers in the project's `OPEN_ITEMS.md`.

## Reporting results (rule)
Never call the originality check "done" or "passed" while any part of it is unfinished. Always report all three numbers to the student:
- local result: PASS/FAIL and the overall % (plus the highest single source and peer %);
- web check: **N of M phrases searched**, number of matches, number unresolved;
- the date of the run, and whether any chapter changed after it (if so, it must be run again).
If the web check is partial, say so plainly and finish it before the final build. The final build refuses to run while `web_check.json` is missing, incomplete or older than the chapters.

## Pass thresholds (defaults; the final build requires a PASS)
- Prose matched to all sources ≤ 10%; to any single source ≤ 3%.
- Matched to any other project ≤ 5%, and **no** shared passage of 12+ words with another project.
- No passage of 12+ words matching a source unless it is in quotation marks with a citation.
- Every quotation of 5+ words has a citation (with page number where the source has pages).
- Web checklist complete: every phrase searched, no unresolved match (`--status` exits 0).

These are stricter than most university tolerances on purpose: the local check cannot see everything the university's scanner sees.

## Copy-case rules when one workspace serves several students
- Each student's ideas, data, survey, organisation details, examples, reflection and wording are their own. Never move text, tables, figures, numbers or reflections from one project to another, including the worked example.
- Two students on similar topics must differ in organisation, data, analysis and voice, not just in synonyms.
- Shared skeleton headings and instructions are excluded automatically (`--exclude-template`); everything else counts.

## Limits (say these to the student)
A local check is not Turnitin or the university's scanner, and an exact-phrase web search finds copying, not every paraphrase. A PASS lowers the risk; it is not a guarantee. The real protection is that the content (ideas, data, experiences, analysis) is the student's own and every source is credited.
