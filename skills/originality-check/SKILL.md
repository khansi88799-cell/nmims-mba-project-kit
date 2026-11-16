---
name: originality-check
description: Check a report for plagiarism (text copied or closely paraphrased from web pages, papers, reports or other sources without quotation and citation) and for copy cases (two students' projects that are too similar, reuse of another project or of template text). Runs a local similarity engine against the project's sources and every other project in the workspace, samples distinctive sentences for exact-phrase web searches, checks that quotations are cited, and guides rewriting until the report is original. Use before any university submission, when a student asks for a plagiarism or similarity check, or when several projects are produced in the same workspace.
metadata:
  version: 1.0.0
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
3. **Web check.** `python3 <skill>/scripts/sample_phrases.py <project>/report --out <project>/output/web_check.md`. Search every query as an exact phrase with the web search tool. Record "no match" or the URL in the checklist. Check more sentences in chapters that lean on sources (literature review, situational analysis).
4. **Fix every finding** with `references/fixing.md`: rewrite in the student's own words and structure (then run the `humaniser` skill in academic mode), or quote and cite, or cut. Never "fix" similarity by inventing a citation or changing a few words.
5. **Re-run** steps 2-3 until the report passes. Record the final numbers in the project's `OPEN_ITEMS.md`.

## Pass thresholds (defaults; the final build requires a PASS)
- Prose matched to all sources ≤ 10%; to any single source ≤ 3%.
- Matched to any other project ≤ 5%, and **no** shared passage of 12+ words with another project.
- No passage of 12+ words matching a source unless it is in quotation marks with a citation.
- Every quotation of 5+ words has a citation (with page number where the source has pages).
- Web checklist complete with no unresolved match.

These are stricter than most university tolerances on purpose: the local check cannot see everything the university's scanner sees.

## Copy-case rules when one workspace serves several students
- Each student's ideas, data, survey, organisation details, examples, reflection and wording are their own. Never move text, tables, figures, numbers or reflections from one project to another, including the worked example.
- Two students on similar topics must differ in organisation, data, analysis and voice, not just in synonyms.
- Shared skeleton headings and instructions are excluded automatically (`--exclude-template`); everything else counts.

## Limits (say these to the student)
A local check is not Turnitin or the university's scanner, and an exact-phrase web search finds copying, not every paraphrase. A PASS lowers the risk; it is not a guarantee. The real protection is that the content (ideas, data, experiences, analysis) is the student's own and every source is credited.
