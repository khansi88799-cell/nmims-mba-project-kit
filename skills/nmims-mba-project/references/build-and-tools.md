# Build tools: commands and gotchas

Each project has its own `tools/` folder (copied from `template/tools/` by `scripts/new_project.sh`). Requirements: Google Chrome (or `CHROME_PATH`), Node 18+, Python 3.10+, optionally Microsoft Word (Calibri) and LibreOffice (deck to PDF). Run `scripts/setup.sh` at the kit root to check and install them.

## Commands (inside `<project>/tools`)
| Command | Does |
|---|---|
| `npm install` and `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` | One-time setup (`new_project.sh --install` does both) |
| `npm run build` | Chapters → `output/MBA_Project_Report.pdf` (cover, contents, list of tables and figures, body, Page X of Y) |
| `npm run model` | `model.json` → `report/working/model_tables.md`, `model_assumptions.md`, `output/Financial_Model.xlsx` |
| `npm run deck` | `presentation/deck.json` → `presentation/<deck.fileName>.pptx` |
| `npm run deck:qa` | One-slide decks in `presentation/_qa` for previews (`qlmanage -t -s 1600 -o _qa _qa/*.pptx`; no charts) |
| `npm run deck:pdf` | Deck → PDF via LibreOffice (charts included) |
| `swift raster.swift ../output/X.pdf <dir> 0.8` or `pdftoppm -png -r 80 ../output/X.pdf <dir>/p` | Page images to inspect |
| `swift flatten.swift in.png out.png` | Flatten a logo with transparent corners onto white |

Checks run from the kit root: `bash skills/nmims-mba-project/scripts/lint_report.sh <project>/report`, `python3 skills/nmims-mba-project/scripts/check_citations.py <project>/report --doi`, and the originality check (`skills/originality-check/SKILL.md`).

## How the PDF build works
- `report.config.json`: chapter folder, output path, logo, cover fields, fonts, `final` switch, deck file name.
- Chapters `NN_name.md` build in filename order; `00_*` files are skipped. `<!-- include: working/file.md -->` pulls in generated tables.
- A paragraph starting `Table 3.2: ...` or `Figure 3.1: ...` becomes a caption and is listed in the front matter.
- Mermaid code blocks become figures (flowchart, quadrantChart, gantt). Display maths with `$$...$$` only.
- Two-pass render: pass 1 finds the page of every heading and caption (`find_pages.py`), pass 2 prints the numbers. The footer is stamped afterwards in the body font.
- `[NEEDS: ...]` and `[VERIFY: ...]` are highlighted in drafts. With `"final": true` the build stops if any remain (chapters or cover), or if `output/originality.json` is missing, failing, or older than the newest chapter.

## Gotchas already solved (do not reintroduce)
- Chrome's own footer cannot load embedded fonts; the footer is stamped with pdf-lib.
- Currency like "A$881 ... A$55" was read as inline maths; write AUD/USD/INR, single-$ maths stays off.
- Mermaid: a label starting "1. " renders as "Unsupported markdown: list" (write "Step 1:"); gantt needs `todayMarker off`; diagram fonts are forced to the body font; check that quadrant labels match the points.
- Justified paragraph style leaks into diagram labels; the build centres diagram text.
- Calibri lives inside Word's app bundle; without Word the build falls back to Arial.
- Logos with transparent rounded corners show a faint outline in PDF: flatten them.

## Deck
- `build_deck.cjs` renders `deck.json` (format in `deck-format.md`). Fonts are Georgia and Arial so previews match PowerPoint on any machine. A small helper (`deck_theme.cjs`) writes the colour theme into the file.
- PowerPoint and Keynote may refuse scripted access (macOS sandbox); use LibreOffice for automatic PDF export, or export by hand.
