#!/usr/bin/env python3
"""Cross-check APA in-text citations against the reference list.

Usage: python3 check_citations.py <report-dir>
  <report-dir> holds the chapter files; the references chapter is the file whose
  first heading ends with "References". Reports in-text citations with no reference,
  references never cited, and DOIs that do not resolve on Crossref (with --doi).
Stdlib only. Heuristic: check anything it flags by eye.
"""
import glob
import json
import os
import re
import sys
import urllib.request


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    d = sys.argv[1]
    files = sorted(f for f in glob.glob(os.path.join(d, "[0-9][0-9]_*.md")) if not os.path.basename(f).startswith("00_"))
    ref_file = next((f for f in files if re.search(r"^#\s.*References\s*$", open(f, encoding="utf-8").read(), re.M)), None)
    if not ref_file:
        sys.exit("No references chapter found (a file whose heading ends with 'References').")
    text = " ".join(open(f, encoding="utf-8").read() for f in files if f != ref_file)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    refs_raw = open(ref_file, encoding="utf-8").read()
    entries = [e.strip() for e in refs_raw.split("\n\n")[1:] if e.strip() and not e.strip().startswith("<!--")]

    # In-text: (Author, 2020), (Author & Other, 2020), (Org [ABBR], 2020), (Author et al., 2020), (Author, n.d.), Author (2020)
    cites = set(re.findall(r"\(([A-Z][\w.&' -]+?)(?: \[[A-Z]+\])?(?:,| et al\.,)\s*(\d{4}|n\.d\.)", text))
    cites |= set(re.findall(r"\b([A-Z][a-z]+(?: (?:and|&) [A-Z][a-z]+)?) \((\d{4})\)", text))
    missing = sorted(c for c in cites if c[0].split(" &")[0].split(" and ")[0].strip() not in refs_raw)
    unused = []
    for e in entries:
        author = re.split(r"[.,(]", e, 1)[0].strip()
        if author and author not in text:
            unused.append(author)
    print(f"In-text citations found: {len(cites)}")
    print("Cited but not in References:", missing or "none")
    print("In References but never cited:", unused or "none")

    if "--doi" in sys.argv:
        for doi in sorted(set(re.findall(r"doi\.org/(10\.\d{4,9}/[^\s)]+)", refs_raw))):
            try:
                with urllib.request.urlopen(f"https://api.crossref.org/works/{doi}", timeout=20) as r:
                    m = json.load(r)["message"]
                print(f"OK   {doi}  {m.get('title', [''])[0][:70]}")
            except Exception as ex:  # noqa: BLE001
                print(f"FAIL {doi}  ({ex})")


if __name__ == "__main__":
    main()
