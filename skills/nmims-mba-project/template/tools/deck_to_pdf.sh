#!/usr/bin/env bash
# Convert the viva deck to PDF with LibreOffice (headless). The PDF shows charts, so it is
# also the way to preview a deck without PowerPoint, and the file to annex in the report if needed.
#   bash deck_to_pdf.sh [deck.pptx]       (default: the newest .pptx in ../presentation)
set -euo pipefail
cd "$(dirname "$0")"
DECK="${1:-$(ls -t ../presentation/*.pptx 2>/dev/null | head -1)}"
[[ -f "$DECK" ]] || { echo "No deck found. Run: npm run deck"; exit 1; }
SOFFICE="$(command -v soffice || true)"
[[ -z "$SOFFICE" && -x "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]] && SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
if [[ -z "$SOFFICE" ]]; then
  echo "LibreOffice is not installed. Install it with:  brew install --cask libreoffice   (or run scripts/setup.sh from the kit)"
  echo "Without it: open the deck in PowerPoint or Keynote and use File > Export > PDF."
  exit 2
fi
"$SOFFICE" --headless --convert-to pdf --outdir "$(dirname "$DECK")" "$DECK" >/dev/null
echo "Wrote ${DECK%.pptx}.pdf"
