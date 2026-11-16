# Known gaps and improvement areas

Ordered by impact. Update this file when a gap is closed or a new one appears.

1. **Business Plan and Research skeletons are not yet proven on a real submission.** They follow the university templates; refine them on first use.
2. **No institutional similarity checker.** `originality-check` compares against local sources, other projects and exact-phrase web searches. It cannot see paywalled databases, other universities' submissions or the scanner's Gen-AI model. If the student has access to Turnitin or a similar tool, run it before submitting.
3. **The web originality check is agent-driven.** It depends on the agent having a web search tool; agents without one can only run the local check.
4. **Deck to PDF needs LibreOffice.** Without it, export by hand from PowerPoint or Keynote (File > Export > PDF). Quick Look previews do not show charts.
5. **Calibri depends on Microsoft Word.** Without Word the build uses Arial (also allowed), which changes the page count by about 20%.
6. **macOS first.** Page rendering uses Swift (`raster.swift`) and fonts use macOS paths. On Linux or Windows, use `pdftoppm` for page images and set Arial or Carlito paths in `report.config.json`; set `CHROME_PATH`.
7. **The citation checker and the AI-writing lint are heuristics.** Confirm anything they flag by reading; the lint ignores text inside tables.
8. **Financial model is simplified** (no debt, single tax rate, net working capital as a % of revenue). Extend it if the business needs loans, inventory or GST detail.
