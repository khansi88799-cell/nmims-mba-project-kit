#!/usr/bin/env python3
"""Exact-phrase web check: pick phrases to search, then verify the checklist is complete.

1. Make (or refresh) the checklist:
       python3 sample_phrases.py <project>/report --out <project>/output/web_check.md [--per-chapter 4]
   For each chapter it picks the sentences most likely to reveal copying (long, specific, and
   especially those carrying a citation, because paraphrases of sources are where copying hides)
   and writes a 12-word exact-phrase query for each. Re-running after edits keeps every result
   already recorded for a query that is still in the report, so only new phrases need searching.

2. The agent searches EVERY query as an exact phrase with its web search tool and records it:
       - [x] "query"
         - result: no match (searched YYYY-MM-DD)
         - result: match: <url>; resolved: rewritten | quoted and cited | cut (searched YYYY-MM-DD)

3. Verify (required before the final build; the build reads the JSON):
       python3 sample_phrases.py --status <project>/output/web_check.md
   Writes web_check.json next to the checklist and exits 2 unless every query is searched
   and every match is resolved.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys

STOP = set("the a an and or of to in for on with by at from as is are was were be been that this these those it its their there which who whom into than then also not but can may will would should could has have had".split())
ITEM = re.compile(r'^- \[( |x|X)\] (".*")\s*$')
RESULT = re.compile(r"^\s+- result:\s*(.*)$")


def sentences(text):
    text = re.sub(r"(?s)<!--.*?-->|```.*?```", " ", text)
    text = "\n".join(l for l in text.splitlines() if l.strip() and not l.lstrip().startswith(("#", "|")) and not re.match(r"^(Table|Figure) \d", l.strip()))
    text = re.sub(r"\[(NEEDS|VERIFY):[^\]]*\]|https?://\S+|[*_`]", " ", text)
    for p in re.split(r"\n\s*\n", text):
        p = " ".join(p.split())
        for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", p):
            yield s


def score(s):
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", s)
    content = [w for w in words if w.lower() not in STOP]
    long_words = sum(1 for w in content if len(w) >= 7)
    cited = 3 if re.search(r"\([^()]*\d{4}[^()]*\)", s) else 0
    return long_words + cited + (1 if re.search(r"\d", s) else 0)


def query(s):
    clean = re.sub(r"\([^()]*\d{4}[^()]*\)", "", s)
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'%.,-]*", clean)
    if len(words) < 12:
        return None
    mid = max(0, (len(words) - 12) // 2)
    return '"' + " ".join(words[mid:mid + 12]).strip(",.") + '"'


def parse(path):
    """Return {query: (checked, result_text)} from an existing checklist."""
    found, cur = {}, None
    if not path or not os.path.exists(path):
        return found
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = ITEM.match(line)
        if m:
            cur = m.group(2)
            found[cur] = (m.group(1).lower() == "x", "")
            continue
        r = RESULT.match(line)
        if r and cur:
            found[cur] = (found[cur][0], r.group(1).strip())
            cur = None
    return found


def classify(checked, result):
    """'ok', 'pending' (not searched or no result) or 'unresolved' (a match not fixed)."""
    low = result.lower()
    if not checked or not result:
        return "pending"
    if low.startswith("no match"):
        return "ok"
    if low.startswith("match"):
        return "ok" if re.search(r"resolved:\s*(rewritten|quoted and cited|cut)", low) else "unresolved"
    return "pending"


def status(path):
    if not os.path.exists(path):
        print(f"No checklist at {path}; make it first with: sample_phrases.py <report_dir> --out {path}")
        return 2
    items = parse(path)
    states = {q: classify(c, r) for q, (c, r) in items.items()}
    pending = [q for q, s in states.items() if s == "pending"]
    unresolved = [q for q, s in states.items() if s == "unresolved"]
    res = {
        "generated": datetime.datetime.now().isoformat(timespec="seconds"),
        "checklist": os.path.abspath(path),
        "total": len(items),
        "searched": len(items) - len(pending),
        "matches": sum(1 for _, r in items.values() if r.lower().startswith("match")),
        "pending": pending,
        "unresolved": unresolved,
    }
    res["complete"] = bool(items) and not pending and not unresolved
    out = os.path.splitext(path)[0] + ".json"
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)
    print(f"Web check: {res['searched']} of {res['total']} phrases searched, {res['matches']} match(es), "
          f"{len(unresolved)} unresolved -> {'COMPLETE' if res['complete'] else 'NOT COMPLETE'} ({out})")
    for q in pending:
        print("  not searched:", q)
    for q in unresolved:
        print("  match not resolved:", q)
    return 0 if res["complete"] else 2


def build(report_dir, per_chapter, out):
    old = parse(out)
    lines = ["# Web originality checklist", "",
             "Search EVERY query as an exact phrase and record the result on its `result:` line, then tick the box:",
             "`no match (searched YYYY-MM-DD)` or `match: <url>; resolved: rewritten | quoted and cited | cut (searched YYYY-MM-DD)`.",
             "Then run `sample_phrases.py --status` on this file. The final build needs every query searched and every match resolved.", ""]
    kept = new = 0
    for f in sorted(glob.glob(os.path.join(report_dir, "[0-9][0-9]_*.md"))):
        name = os.path.basename(f)
        if name.startswith("00_"):
            continue
        first = open(f, encoding="utf-8").readline()
        if re.search(r"(References|Appendices)\s*$", first):
            continue
        cands = [s for s in sentences(open(f, encoding="utf-8").read()) if 15 <= len(s.split()) <= 60]
        picked = sorted(cands, key=score, reverse=True)[:per_chapter]
        if not picked:
            continue
        lines += [f"## {name}", ""]
        for s in picked:
            q = query(s)
            if not q:
                continue
            checked, result = old.get(q, (False, ""))
            if result:
                kept += 1
            else:
                new += 1
            lines += [f"- [{'x' if checked else ' '}] {q}", f"  - sentence: {s[:220]}", f"  - result: {result}"]
        lines.append("")
    text = "\n".join(lines) + "\n"
    if out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        open(out, "w", encoding="utf-8").write(text)
        print(f"Wrote {out}: {kept + new} phrases ({kept} already searched, {new} to search)")
    else:
        print(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report_dir", nargs="?")
    ap.add_argument("--per-chapter", type=int, default=4)
    ap.add_argument("--out")
    ap.add_argument("--status", metavar="CHECKLIST", help="verify a filled checklist and write its .json summary")
    a = ap.parse_args()
    if a.status:
        sys.exit(status(a.status))
    if not a.report_dir:
        ap.error("report_dir is required unless --status is given")
    build(a.report_dir, a.per_chapter, a.out)


if __name__ == "__main__":
    main()
