# Lessons learned

From building a complete Problem-Solving Proposal with this method (36 pages, Calibri, submission-ready). Apply them from the first day of every project.

## Mistakes found in a first draft, and the fix
| Problem found | Fix |
|---|---|
| Content read as a new-venture business plan, but the registered format was Problem-Solving with no organisation | Made a listed company the case organisation; the student's venture idea became the proposed solution to that organisation's problem |
| Registered title not on the cover; cover named the wrong school | Cover generated from `report.config.json` with the exact registered title and the CDOE logo |
| About 13 pages against a 30-page minimum, half of it bullet lists and diagrams | Rebuilt as prose chapters with captioned tables and figures |
| Six statistics with no traceable source | Replaced with primary sources (regulatory filings, government reports, the original survey) |
| Financials not credible (near-100% margins, nine-figure revenue in year 5) | Reproducible model with labelled assumptions and a sensitivity table; numbers became modest and defensible |
| Claims in the student's own requirements document that did not survive the model | Report states the corrected figure and says why it changed (examiners like this) |
| A SWOT quadrant chart with swapped labels; a wrong DOI | Render every page and look at it; check every DOI on Crossref |
| Wrong font, no page numbers, diagrams missing | Markdown → Chrome → PDF build meeting every layout rule |
| A research claim ("interviews showed ...") with no interviews behind it | Removed; the reflection was written only from the student's answers |
| Text sounded machine-written (bold-label bullets, "whilst", "profound") | Humaniser academic mode + prose-only lint |

## Habits that worked
- Ask everything in rounds (`intake.md`) and record answers verbatim. Do not guess the title, format, exam cycle or guide.
- Settle format, title and case organisation before writing.
- Write chapters 2 → 6, then the reflection, then the executive summary or abstract last.
- Derive design requirements from the analysis and reuse them as the scoring criteria for alternatives; run a sensitivity test on the weights.
- Benchmark several organisations to show the problem is structural.
- Generate report tables from the model; check that numbers match across summary, chapters, deck and appendix.
- `[NEEDS]` / `[VERIFY]` tags instead of guesses; a final build that refuses to run while any remain, or while the originality check is failing or out of date.
- When the student pushes back on a critique, look for the framing that satisfies both the rubric and their intent.
- Quarterly filings and versioned legal PDFs often answer questions that help pages block.
