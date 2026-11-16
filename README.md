# NMIMS MBA Project Kit

An AI-agent toolkit for the **NMIMS CDOE online MBA Semester IV project** (6 credits). It takes a student from the first idea to two submission-ready files:

- **Project report PDF**, built to the university's layout rules: official cover with the NMIMS CDOE logo, contents, list of tables and figures, Calibri 11 pt, 1-inch margins, 1.15 spacing, justified text, "Page X of Y", annexures inside the PDF.
- **Viva presentation (PPTX, plus a PDF copy)**: a 16-slide storyline with native charts and a business flow diagram.

It works with **Claude Code, OpenAI Codex, Google Antigravity, Gemini CLI, Cursor and GitHub Copilot**. Open the folder in any of them and ask it to start a project.

## What the kit makes sure of
- **Right format and title.** Covers all three NMIMS formats (Problem-Solving Proposal, Business Plan, Research Project), with chapter skeletons mapped to each marking rubric and a check that the title and format match the registration.
- **The agent asks before it writes.** Project name and type, the Semester III pre-work from the portal, work already done, the idea in the student's own words, type-specific questions, cover details.
- **A survey is always offered** (paste-ready for Google Forms or Microsoft Forms). The student can skip it.
- **No plagiarism, no copy case.** A local similarity engine compares the report against its sources and every other project in the kit, and the agent runs exact-phrase web checks. The final build is blocked until the check passes.
- **Human, original writing.** Academic-mode humaniser, prose lint, no invented facts, experiences or sources.
- **Verifiable numbers.** Primary-source evidence rules, APA 7 citations with a cross-checker and DOI resolver, and a reproducible financial model (P&L, cash flow, balance sheet, break-even, sensitivity).

## Quick start
```bash
git clone <this repo> nmims-mba-project-kit
cd nmims-mba-project-kit
bash scripts/setup.sh                 # checks Node, Python, Chrome, LibreOffice...; asks before installing
python3 scripts/sync_agent_files.py   # links skills and commands for every agent app
```
Then open the folder in your agent app and type `/new-project` (or say "start a new NMIMS project"). The agent asks the intake questions and creates `projects/<student>-<topic>/`.

Without an agent, the same steps are manual: see [docs/GUIDE.md](docs/GUIDE.md).

## Commands
| Command | What it does |
|---|---|
| `/new-project` | Intake questions, create the project folder, draft the outline |
| `/continue-project <folder>` | Status, open questions, next steps |
| `/survey <folder>` | Offer, draft, record or skip the survey |
| `/write-chapter <folder> <chapter>` | Write or revise one chapter against its rubric |
| `/humanise <folder> [chapter]` | Academic-voice pass with before/after measurements |
| `/originality-check <folder>` | Plagiarism and copy-case check, then fixes |
| `/verify-sources <folder>` | Resolve `[VERIFY]` tags, check citations and DOIs |
| `/build <folder>` | Draft PDF, financial tables and deck |
| `/finalise <folder>` | Final checks and the submission PDF + PPT |
| `/setup` | Check and install tools |

## Requirements
| Tool | Needed for | |
|---|---|---|
| Node.js 18+ | PDF and deck builds | required |
| Python 3.10+ | financial model, checks, originality engine | required |
| Google Chrome (or `CHROME_PATH`) | rendering the PDF | required |
| LibreOffice | deck to PDF, chart previews | recommended |
| Poppler (`pdftoppm`) | page images on any OS | recommended |
| Microsoft Word | Calibri font (Arial is used without it; NMIMS allows both) | optional |
| GitHub CLI | publishing your copy | optional |

Built and tested on macOS. Linux and Windows work with the notes in [docs/GUIDE.md](docs/GUIDE.md#other-operating-systems).

## Repository layout
```
skills/
  nmims-mba-project/   method, intake, references, chapter skeletons, build template, logos, guidelines PDF
  originality-check/   plagiarism + copy-case engine and web phrase sampler
  humaniser/           natural academic writing, AI-pattern lint
  clean-user-facing-text/  hidden-Unicode cleaner, rhythm scorer
commands/              canonical slash-command prompts
scripts/               setup.sh, sync_agent_files.py
docs/                  GUIDE.md, AGENT-APPS.md
projects/              student projects (git-ignored, never published)
AGENTS.md              rules for every AI agent (CLAUDE.md and GEMINI.md point here)
```

## Academic integrity
The kit is designed so the student remains the author: it asks for their idea, their organisation, their data and their experiences, never invents any of them, cites every source and checks originality. Read the university's rules on originality and on using AI tools, and follow your faculty guide's instructions. A passing local originality check lowers risk; it does not guarantee the university's scanner result.

## Credits and licences
- Kit code and documentation: MIT licence ([LICENSE](LICENSE)).
- `skills/humaniser` builds on [YKehinde/humaniser](https://github.com/YKehinde/humaniser) (MIT) and Wikipedia's "Signs of AI writing" (CC BY-SA).
- `skills/clean-user-facing-text` is from [guillaumemeyer/watermarks-remover](https://github.com/guillaumemeyer/watermarks-remover) (MIT).
- The NMIMS logos and the project guidelines PDF belong to SVKM's NMIMS. They are included so students can use them on their own project covers; they are not covered by the MIT licence. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
