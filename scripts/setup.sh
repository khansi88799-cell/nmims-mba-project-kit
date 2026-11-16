#!/usr/bin/env bash
# Check and install the tools the kit needs. Asks before every install.
#   bash scripts/setup.sh           check, then offer to install what is missing
#   bash scripts/setup.sh --check   check only
#   bash scripts/setup.sh --yes     install everything missing without asking (CI / unattended)
set -uo pipefail
MODE="${1:-}"
OS="$(uname -s)"
have() { command -v "$1" >/dev/null 2>&1; }
ok() { printf "  [ok]      %s\n" "$1"; }
miss() { printf "  [missing] %s - %s\n" "$1" "$2"; MISSING+=("$3"); }
MISSING=()

ask() {
  [[ "$MODE" == "--check" ]] && return 1
  [[ "$MODE" == "--yes" ]] && return 0
  read -r -p "  Install $1? [y/N] " a; [[ "$a" =~ ^[Yy]$ ]]
}

echo "Checking tools"
have node && [[ "$(node -v | sed 's/v//;s/\..*//')" -ge 18 ]] && ok "Node.js $(node -v)" || miss "Node.js 18+" "PDF and deck builds" node
PY=""; for p in python3.12 python3.11 python3.10 python3; do have "$p" && "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' && { PY="$p"; break; }; done
[[ -n "$PY" ]] && ok "Python 3.10+ ($PY)" || miss "Python 3.10+" "model, checks, originality" python
CHROME=""; for c in "${CHROME_PATH:-}" "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" /usr/bin/google-chrome /usr/bin/chromium; do [[ -n "$c" && -x "$c" ]] && CHROME="$c" && break; done
[[ -n "$CHROME" ]] && ok "Google Chrome" || miss "Google Chrome" "renders the PDF" chrome
{ have soffice || [[ -x /Applications/LibreOffice.app/Contents/MacOS/soffice ]]; } && ok "LibreOffice" || miss "LibreOffice (recommended)" "deck to PDF, chart previews" libreoffice
have pdftoppm && ok "Poppler (pdftoppm)" || miss "Poppler (recommended)" "page images on any OS" poppler
have gh && ok "GitHub CLI" || miss "GitHub CLI (optional)" "publish the repo" gh
[[ -f "/Applications/Microsoft Word.app/Contents/Resources/DFonts/Calibri.ttf" ]] && ok "Calibri (Microsoft Word)" || echo "  [note]    Calibri not found: install Microsoft Word for Calibri, or the build uses Arial (also allowed by NMIMS)"

[[ ${#MISSING[@]} -eq 0 ]] && { echo "All set."; exit 0; }
[[ "$MODE" == "--check" ]] && exit 0

if [[ "$OS" == "Darwin" ]]; then
  if ! have brew; then
    echo "Homebrew is needed to install tools on macOS: https://brew.sh (install it, then run this again)."; exit 1
  fi
  for t in "${MISSING[@]}"; do
    case "$t" in
      node)        ask "Node.js (brew install node)" && brew install node ;;
      python)      ask "Python 3.11 (brew install python@3.11)" && brew install python@3.11 ;;
      chrome)      ask "Google Chrome (brew install --cask google-chrome)" && brew install --cask google-chrome ;;
      libreoffice) ask "LibreOffice, about 700 MB (brew install --cask libreoffice)" && brew install --cask libreoffice ;;
      poppler)     ask "Poppler (brew install poppler)" && brew install poppler ;;
      gh)          ask "GitHub CLI (brew install gh)" && brew install gh ;;
    esac
  done
else
  echo "Install the missing tools with your package manager, for example on Ubuntu:"
  echo "  sudo apt install nodejs npm python3 python3-venv chromium libreoffice poppler-utils gh"
  echo "On Windows: use winget (OpenJS.NodeJS, Python.Python.3.11, Google.Chrome, TheDocumentFoundation.LibreOffice, GitHub.cli) and set CHROME_PATH."
fi
echo "Done. Re-run with --check to confirm."
