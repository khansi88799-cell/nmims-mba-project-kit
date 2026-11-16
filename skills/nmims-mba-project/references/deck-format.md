# Viva deck format (presentation/deck.json)

The deck follows a 16-slide storyline that has worked for a Problem-Solving Proposal: opening, problem, solution, business, plan, reflection. Adapt it for the other formats (a Research deck replaces the business slides with method, findings and implications). `template/presentation/deck.example.json` shows every type with fictional sample content.

`deck.json` = `{ "footer": "...", "slides": [ ... ] }`. Optional `theme` (hex colours: ink, slate, accent, grey, good, warn, mist, line, mute, white). Every slide takes `type`, `title`, `section` (groups slides in PowerPoint) and `notes` (speaker notes, 2-4 sentences).

| # | Storyline slide | Type | Fields |
|---|---|---|---|
| 1 | Title | `title` | `subtitle`, `badges` (up to 3 words), optional `lines` (otherwise taken from the cover config) |
| 2 | The thought: where the idea came from | `story` | `heading`, `bullets`, `stats` [{value, label}] (up to 3), `source` |
| 3 | The problem at the organisation | `chart_text` | `chart` {kind: "col"\|"bar", title, labels, values, format, max, highlight}, `heading`, `bullets`, `callout`, `source` |
| 4 | Evidence / benchmark | `chart_cards` | `chart`, `cards` [{title, text}] (up to 3), `source` |
| 5 | Requirements | `cards` | `items` [{label, text}] (up to 8), `source` |
| 6 | Approach: alternatives scored | `scoring` | `chart` {title, labels, values} (highest is highlighted), `heading`, `rows` [[label, value]] (sensitivity), `note` |
| 7 | The solution | `steps` | `steps` [{title, text}] (up to 6), `notes_cards` [{title, text}] (up to 2) |
| 8 | Business flow diagram | `flow` | `nodes` [{id, title, sub, row, col, style: core\|plain\|muted}], `edges` [{from, to, label, kind: money\|info}], `note`. Grid of up to 3 rows × 4 columns; arrows route automatically; two edges between the same boxes are drawn side by side |
| 9 | How it makes money / pays back | `revenue` | `items` [{value, label, text}] (up to 4), `chart`, `note`, `source` |
| 10 | Financial outlook | `finance` | `chart` {title, labels, series [{name, values}]}, `kpis` [{value, label}] (up to 4), `source` |
| 11 | Investment plan | `invest` | `chart` {title, labels, values} (doughnut), `gates` [{name, date, text}] (up to 3), `note` |
| 12 | Roadmap | `roadmap` | `phases` [{code, date, name, items}] (up to 4), `highlight` (index), `source` |
| 13 | Changes along the way | `changes` | `rows` [{from, to}] (up to 6), optional `fromLabel`, `toLabel` |
| 14 | What I learned | `learnings` | `items` [{title, text}] (up to 4), `source` |
| 15 | Future enhancements | `horizons` | `columns` [{title, items}] (3), `approach` |
| 16 | Closing and the ask | `closing` | `subtitle`, `asks` [{title, text}] (up to 3), `thanks` |

## Rules
- Numbers, names and claims must match the report exactly. Build the deck after the report is final.
- Slide 2, 13 and 14 come from the student's own answers (intake rounds 3 and 7).
- Keep text short: titles under 60 characters, bullets under 12 words, body text 14 pt minimum (the layouts enforce sizes).
- Build: `npm run deck`; preview: `npm run deck:qa` + Quick Look (no charts) or `npm run deck:pdf` (LibreOffice, charts included). Look at every slide.
