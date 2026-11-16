#!/usr/bin/env python3
"""Find the page each heading/caption lands on in a rendered PDF.

Usage: find_pages.py BODY.pdf ENTRIES.json  -> prints a JSON list of 1-based page numbers (null if not found)
ENTRIES.json is a list of strings in document order. The search starts after the
page containing the BODYSTART sentinel and moves forward only, so mentions in the
contents pages or earlier text cannot match.
"""
import json
import re
import sys
import unicodedata

from pypdf import PdfReader


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[^a-z0-9]", "", s)


def main():
    reader = PdfReader(sys.argv[1])
    entries = json.load(open(sys.argv[2], encoding="utf-8"))
    pages = [norm(p.extract_text() or "") for p in reader.pages]
    start = next((i for i, t in enumerate(pages) if "bodystart" in t), 0)
    out, cur = [], start
    for e in entries:
        key = norm(e)[:45]
        found = None
        for i in range(cur, len(pages)):
            if key and key in pages[i]:
                found = i
                break
        if found is None:
            out.append(None)
        else:
            out.append(found + 1)
            cur = found
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
