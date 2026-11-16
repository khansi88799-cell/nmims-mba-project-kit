#!/usr/bin/env bash
# Create a new, self-contained NMIMS project folder from the skill template.
#
#   scripts/new_project.sh <name-topic-slug> <format> [--install]
#     format: problem-solving | business-plan | research
#     --install  also installs the build tools (npm packages + Python venv)
#
# Creates <kit>/projects/<slug>/ (or $PROJECTS_DIR/<slug>) and never touches any other project.
# <kit>/projects/ is git-ignored: student work is never published.
set -euo pipefail

SLUG="${1:-}"; FORMAT="${2:-}"; INSTALL="${3:-}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KIT_ROOT="$(cd "$SKILL_DIR/../.." && pwd)"
DEST="${PROJECTS_DIR:-$KIT_ROOT/projects}/$SLUG"

case "$FORMAT" in
  problem-solving) LABEL="Problem-Solving Proposal" ;;
  business-plan)   LABEL="Business Plan" ;;
  research)        LABEL="Research Project" ;;
  *) echo "usage: $0 <name-topic-slug> <problem-solving|business-plan|research> [--install]"; exit 1 ;;
esac
[[ "$SLUG" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "slug must be lowercase letters, digits and hyphens, e.g. rahul-supply-chain"; exit 1; }
[[ -e "$DEST" ]] && { echo "Refusing to overwrite existing folder: $DEST"; exit 1; }

mkdir -p "$DEST"/{report/working,output,presentation,research/student-input,research/survey,research/sources}
cp -R "$SKILL_DIR/template/tools" "$SKILL_DIR/template/assets" "$DEST/"
cp "$SKILL_DIR/template/presentation/deck.example.json" "$DEST/presentation/"
rm -rf "$DEST/tools/node_modules" "$DEST/tools/.venv" "$DEST/tools/.build"
cp "$SKILL_DIR/formats/$FORMAT/"*.md "$DEST/report/"
python3 - "$DEST/tools/report.config.json" "$LABEL" <<'PY'
import json, sys
p, label = sys.argv[1], sys.argv[2]
c = json.load(open(p)); c["cover"]["format"] = label
json.dump(c, open(p, "w"), indent=2, ensure_ascii=False)
PY

cat > "$DEST/AGENTS.md" <<EOF
# NMIMS MBA project: $SLUG

Format: **$LABEL**. Created $(date +%Y-%m-%d) from the nmims-mba-project skill.

1. Read the kit rules: \`../../AGENTS.md\`.
2. Follow the skill: \`../../skills/nmims-mba-project/SKILL.md\` (intake questions in its \`references/intake.md\`).
3. Work only inside this folder. Never copy text, data or files from another student's project.
4. Before the final build, run the originality check: \`../../skills/originality-check/SKILL.md\`.

| Path | Purpose |
|---|---|
| \`report/\` | Chapters (Markdown, built in filename order). \`00_OUTLINE.md\` is the plan |
| \`report/working/\` | Generated tables and notes (not built unless included) |
| \`tools/\` | Build: \`npm run build\` (PDF), \`npm run deck\` (slides), \`.venv/bin/python financial_model.py --md\` |
| \`tools/report.config.json\` | Cover details, fonts, output name, \`final\` switch |
| \`research/sources/\` | Every source used (PDF, saved pages); compared by the originality check |
| \`research/student-input/\` | Files the student shared (pre-work, drafts, notes) |
| \`research/survey/\` | Survey form and responses export |
| \`output/\` | Built PDF and spreadsheets |
| \`presentation/\` | \`deck.json\` (copy from deck.example.json) and the built deck |
| \`OPEN_ITEMS.md\` | Questions for the student, decisions, progress log |
EOF
printf '@AGENTS.md\n\nRead AGENTS.md first.\n' > "$DEST/CLAUDE.md"
printf '@AGENTS.md\n\nRead AGENTS.md first.\n' > "$DEST/GEMINI.md"
cat > "$DEST/OPEN_ITEMS.md" <<EOF
# $SLUG: open items

## Intake (see skills/nmims-mba-project/references/intake.md)
### Round 1: project
- Project name: $SLUG
- Type: $LABEL
- Specialisation:
### Round 2: Semester III pre-work and work already done
- Pre-work title / description / feedback:
- Registered title (exact):
- Files shared (saved in research/student-input/):
### Round 3: the idea in the student's own words
### Round 4: type-specific answers
### Round 5: survey (offered on: ; decision: yes / already have / skipped)
### Round 6: cover and admin
- Name, SAP ID, exam cycle, faculty guide, deadline:
### Round 7: reflection answers

## Decisions

## Progress log
- $(date +%Y-%m-%d): project created.
EOF

if [[ "$INSTALL" == "--install" ]]; then
  (cd "$DEST/tools" && npm install --silent && python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt)
fi
echo "Created $DEST ($LABEL)"
echo "Next: fill tools/report.config.json and OPEN_ITEMS.md, then: cd $DEST/tools && npm install && npm run build"
