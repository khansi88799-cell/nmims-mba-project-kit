#!/usr/bin/env bash
# Run the humaniser's prose checks and the hidden-Unicode scan on every chapter.
#   scripts/lint_report.sh <report-dir>
# Targets (academic mode): AI vocabulary < 3 per 1,000 words, sentence-length CV 0.45-0.80,
# no em dashes, no curly quotes, no bold-label bullet lists in body text.
set -euo pipefail
DIR="${1:?usage: lint_report.sh <report-dir>}"
SKILLS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LINT="$SKILLS/humaniser/scripts/ai_lint.py"
UNI="$SKILLS/clean-user-facing-text/scripts/inspect_text.py"
for f in "$DIR"/[0-9][0-9]_*.md; do
  case "$(basename "$f")" in 00_*) continue ;; esac
  python3 "$LINT" --json "$f" | python3 -c "
import json,sys
d=json.load(sys.stdin); n=sys.argv[1]
print(f\"{n[:34]:34} words={d['words']:5} ai/1k={d['ai_words_per_1k']:4} CV={d['sent_cv']:<5} em={d['em_dashes']} flags={d['flags']}\")" "$(basename "$f")"
done
cat "$DIR"/[0-9][0-9]_*.md | python3 "$UNI" - 2>/dev/null | grep -E "^Suspicious" || true
echo "Detail for one chapter: python3 $LINT <file> --sections"
