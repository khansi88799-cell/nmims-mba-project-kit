#!/usr/bin/env python3
"""Pick distinctive sentences for an exact-phrase web check.

    python3 sample_phrases.py <project>/report [--per-chapter 4] [--out <project>/output/web_check.md]

For each chapter it chooses the sentences most likely to reveal copying: long, specific,
and especially those that carry a citation (paraphrases of sources are where copying
hides). For each it prints a search query (12 consecutive words in quotes). The agent
runs each query with its web search tool and records the result in the checklist:
"no match", "match: <url>" (then rewrite or quote and cite).
"""
import argparse
import glob
import os
import re

STOP = set("the a an and or of to in for on with by at from as is are was were be been that this these those it its their there which who whom into than then also not but can may will would should could has have had".split())


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report_dir")
    ap.add_argument("--per-chapter", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args()
    lines = ["# Web originality checklist", "", "Search each query as an exact phrase. Record: no match / match: URL. Any match must be rewritten in the student's own words or quoted with a citation.", ""]
    for f in sorted(glob.glob(os.path.join(a.report_dir, "[0-9][0-9]_*.md"))):
        name = os.path.basename(f)
        if name.startswith("00_"):
            continue
        first = open(f, encoding="utf-8").readline()
        if re.search(r"(References|Appendices)\s*$", first):
            continue
        cands = [s for s in sentences(open(f, encoding="utf-8").read()) if 15 <= len(s.split()) <= 60]
        picked = sorted(cands, key=score, reverse=True)[: a.per_chapter]
        if not picked:
            continue
        lines += [f"## {name}", ""]
        for s in picked:
            q = query(s)
            if q:
                lines += [f"- [ ] {q}", f"  - sentence: {s[:220]}", "  - result: "]
        lines.append("")
    out = "\n".join(lines) + "\n"
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, "w", encoding="utf-8").write(out)
        print("Wrote", a.out)
    else:
        print(out)


if __name__ == "__main__":
    main()
