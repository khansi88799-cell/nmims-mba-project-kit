#!/usr/bin/env python3
"""Local originality check: plagiarism against sources and copy cases between projects.

    python3 similarity.py <project>/report \
        --corpus <project>/research            # downloaded sources, notes, PDFs (plagiarism)
        --peers <kit>/projects                 # every other student project (copy case)
        --exclude-template <kit>/skills/nmims-mba-project/formats   # skeleton text is not "copying"
        --out <project>/output/originality

Method: each chapter is cut into overlapping k-word sequences ("shingles", default 8 words).
A word counts as matched when it sits inside a shingle that also occurs in a source or a
peer project. Runs of matched words of at least --min-run words are reported as passages.
Quoted text ("...") of 5+ words is left out of the score but must carry a citation; quotes
without one are listed. Headings, tables markup, code, URLs, citations and [NEEDS]/[VERIFY]
markers are ignored.

Writes <out>.md (readable report) and <out>.json (summary used by the final build gate).
Exit code: 0 = within thresholds, 2 = over a threshold, 1 = usage error.
Stdlib only; reads .md .txt .html .pdf (if pypdf is installed) .docx .pptx.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import html
import json
import os
import re
import sys
import zipfile
from collections import defaultdict

WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'%.-]*")


# ---------------------------------------------------------------- reading
def read_any(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in (".md", ".txt", ".csv"):
            return open(path, encoding="utf-8", errors="ignore").read()
        if ext in (".html", ".htm"):
            t = open(path, encoding="utf-8", errors="ignore").read()
            t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
            return html.unescape(re.sub(r"<[^>]+>", " ", t))
        if ext == ".pdf":
            try:
                from pypdf import PdfReader  # optional
            except ImportError:
                print(f"  (skipped {path}: install pypdf to read PDFs)", file=sys.stderr)
                return ""
            return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
        if ext in (".docx", ".pptx"):
            z = zipfile.ZipFile(path)
            parts = [n for n in z.namelist() if (n == "word/document.xml" or re.match(r"ppt/slides/slide\d+\.xml", n))]
            return " ".join(re.sub(r"<[^>]+>", " ", z.read(n).decode("utf-8", "ignore")) for n in parts)
    except Exception as ex:  # noqa: BLE001
        print(f"  (could not read {path}: {ex})", file=sys.stderr)
    return ""


def walk(path: str):
    if os.path.isfile(path):
        yield path
        return
    for root, _, files in os.walk(path):
        if any(part in ("node_modules", ".venv", ".git", ".build") for part in root.split(os.sep)):
            continue
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in (".md", ".txt", ".html", ".htm", ".pdf", ".docx", ".pptx", ".csv"):
                yield os.path.join(root, f)


def chapter_files(report_dir: str):
    files = sorted(glob.glob(os.path.join(report_dir, "[0-9][0-9]_*.md")))
    out = []
    for f in files:
        name = os.path.basename(f)
        if name.startswith("00_"):
            continue
        first = open(f, encoding="utf-8").readline()
        if re.search(r"References\s*$", first) or re.search(r"Appendices\s*$", first):
            continue  # reference lists and annex material are checked by reading, not scored
        out.append(f)
    return out


# ---------------------------------------------------------------- cleaning
QUOTE = re.compile(r"(?:(?<=^)|(?<=[\s(]))[\"“](?=\S)([^\"”\n]{20,400}?)(?<=\S)[\"”](?![A-Za-z])")


def clean_markdown(t: str):
    """Return (prose_text, quotes) with markup, citations and quotes removed."""
    t = re.sub(r"(?s)<!--.*?-->", " ", t)
    t = re.sub(r"(?s)```.*?```", " ", t)
    t = re.sub(r"\[(NEEDS|VERIFY):[^\]]*\]", " ", t)
    lines = []
    for line in t.splitlines():
        s = line.strip()
        if s.startswith("#") or re.match(r"^\|?\s*:?-{3,}", s):
            continue
        if re.match(r"^(Table|Figure) \d+\.\d+:", s):
            continue
        lines.append(s.replace("|", " "))
    t = "\n".join(lines)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    quotes = []
    for m in QUOTE.finditer(t):
        q = m.group(1)
        if len(q.split()) >= 5:
            rest = t[m.end(): m.end() + 300]
            end = re.search(r"[.!?](\s|$)", rest)
            sentence_after = rest[: end.end()] if end else rest
            before = t[max(0, m.start() - 160): m.start()]
            cite = re.compile(r"\([^()]*(\d{4}[a-z]?|n\.d\.)[^()]*\)")
            cited = bool(cite.search(sentence_after)) or bool(cite.search(before))
            quotes.append((q, cited))
    t = QUOTE.sub(lambda m: " " if len(m.group(1).split()) >= 5 else m.group(0), t)
    t = re.sub(r"\([^()]*?(\d{4}[a-z]?|n\.d\.)[^()]*?\)", " ", t)  # (Author, 2020)
    t = re.sub(r"[*_`>]", " ", t)
    return t, quotes


def tokens(t: str):
    out = []
    for m in WORD.finditer(t):
        w = m.group(0).lower().strip(".'-")
        if w:
            out.append((w, m.group(0)))
    return out


def shingles(words, k):
    return [hash(tuple(words[i:i + k])) for i in range(len(words) - k + 1)]


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report_dir")
    ap.add_argument("--corpus", action="append", default=[], help="file or folder of sources (repeatable)")
    ap.add_argument("--peers", action="append", default=[], help="folder holding other projects (each with report/)")
    ap.add_argument("--exclude-template", action="append", default=[], help="skeleton text to ignore")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--min-run", type=int, default=12, help="report matched passages of at least this many words")
    ap.add_argument("--max-overall", type=float, default=10.0, help="max %% of prose matched to sources")
    ap.add_argument("--max-source", type=float, default=3.0, help="max %% matched to any single source")
    ap.add_argument("--max-peer", type=float, default=5.0, help="max %% matched to any other project")
    ap.add_argument("--out", default=None, help="output path without extension")
    a = ap.parse_args()

    target = os.path.realpath(a.report_dir)
    chapters = chapter_files(target)
    if not chapters:
        print("No chapters found in", target)
        sys.exit(1)
    k = a.k

    # template shingles (ignored)
    ignore = set()
    for d in a.exclude_template:
        for f in walk(d):
            ignore.update(shingles([w for w, _ in tokens(clean_markdown(read_any(f))[0])], k))

    # source corpus
    index = defaultdict(set)  # shingle -> {source label}
    labels = {}
    def add_doc(label, text, kind):
        labels[label] = kind
        for s in shingles([w for w, _ in tokens(text)], k):
            if s not in ignore:
                index[s].add(label)

    for c in a.corpus:
        for f in walk(c):
            add_doc(os.path.relpath(f, os.path.dirname(os.path.realpath(c))), read_any(f), "source")
    project_root = os.path.dirname(target)
    for pdir in a.peers:
        for proj in sorted(glob.glob(os.path.join(pdir, "*"))):
            rep = os.path.join(proj, "report")
            if not os.path.isdir(rep) or os.path.realpath(proj) == os.path.realpath(project_root):
                continue
            text = "\n".join(clean_markdown(open(f, encoding="utf-8").read())[0] for f in chapter_files(rep))
            add_doc(f"PROJECT:{os.path.basename(proj)}", text, "peer")

    src_labels = {l for l, kd in labels.items() if kd == "source"}
    total_words = 0
    matched_total = 0
    matched_src = 0
    per_source = defaultdict(int)
    per_chapter = []
    passages = []
    quotes_uncited = []
    for f in chapters:
        prose, quotes = clean_markdown(open(f, encoding="utf-8").read())
        quotes_uncited += [(os.path.basename(f), q) for q, cited in quotes if not cited]
        toks = tokens(prose)
        words = [w for w, _ in toks]
        n = len(words)
        covered = [set() for _ in range(n)]
        for i, s in enumerate(shingles(words, k)):
            if s in ignore:
                continue
            srcs = index.get(s)
            if srcs:
                for j in range(i, i + k):
                    covered[j] |= srcs
        m = sum(1 for c in covered if c)
        matched_src += sum(1 for c in covered if c & src_labels)
        total_words += n
        matched_total += m
        for lab in labels:
            per_source[lab] += sum(1 for c in covered if lab in c)
        per_chapter.append((os.path.basename(f), n, m))
        i = 0
        while i < n:
            if covered[i]:
                j = i
                srcs = defaultdict(int)
                while j < n and covered[j]:
                    for s in covered[j]:
                        srcs[s] += 1
                    j += 1
                if j - i >= a.min_run:
                    best = max(srcs, key=srcs.get)
                    passages.append({"chapter": os.path.basename(f), "words": j - i, "source": best, "kind": labels[best],
                                     "text": " ".join(orig for _, orig in toks[i:j])})
                i = j
            else:
                i += 1

    pct = lambda x: round(100.0 * x / total_words, 1) if total_words else 0.0
    src_rows = sorted(((lab, pct(c)) for lab, c in per_source.items() if c), key=lambda r: -r[1])
    peer_rows = [r for r in src_rows if labels[r[0]] == "peer"]
    source_rows = [r for r in src_rows if labels[r[0]] == "source"]
    overall_sources = pct(matched_src)  # peers are judged separately
    ext_passages = [p for p in passages if p["kind"] == "source"]
    peer_passages = [p for p in passages if p["kind"] == "peer"]

    problems = []
    if source_rows and overall_sources > a.max_overall:
        problems.append(f"overall match to sources {overall_sources}% > {a.max_overall}%")
    problems += [f"source {l}: {p}% > {a.max_source}%" for l, p in source_rows if p > a.max_source]
    problems += [f"copy case with {l}: {p}% > {a.max_peer}%" for l, p in peer_rows if p > a.max_peer]
    if ext_passages:
        problems.append(f"{len(ext_passages)} passage(s) of {a.min_run}+ words match a source without quotation marks")
    if peer_passages:
        problems.append(f"{len(peer_passages)} passage(s) of {a.min_run}+ words match another project")
    if quotes_uncited:
        problems.append(f"{len(quotes_uncited)} quotation(s) without a citation")
    ok = not problems

    stamp = dt.datetime.now().isoformat(timespec="seconds")
    md = [f"# Originality report", "", f"Generated {stamp} for `{target}`", "",
          f"**Result: {'PASS' if ok else 'FAIL'}**  (k={k}-word sequences; passages of {a.min_run}+ words reported)", "",
          f"- Prose words checked: {total_words} (references, appendices, headings, tables markup, citations and quotations excluded)",
          f"- Sources indexed: {len(src_labels)}; other projects compared: {len(labels) - len(src_labels)}",
          f"- Words matching any source or project: {matched_total} ({pct(matched_total)}%)", ""]
    if problems:
        md += ["## Problems", ""] + [f"- {p}" for p in problems] + [""]
    md += ["## By chapter", "", "| Chapter | Words | Matched | % |", "|---|---|---|---|"]
    md += [f"| {c} | {n} | {m} | {round(100*m/n,1) if n else 0} |" for c, n, m in per_chapter]
    if src_rows:
        md += ["", "## By source or project", "", "| Source | Kind | % of prose |", "|---|---|---|"]
        md += [f"| {l} | {labels[l]} | {p} |" for l, p in src_rows[:25]]
    if passages:
        md += ["", "## Matched passages (rewrite in your own words, or quote and cite)", ""]
        for p in sorted(passages, key=lambda x: -x["words"])[:40]:
            md += [f"- **{p['chapter']}**, {p['words']} words, {p['kind']} `{p['source']}`: \"{p['text'][:400]}\""]
    if quotes_uncited:
        md += ["", "## Quotations without a citation", ""] + [f"- {c}: \"{q[:200]}\"" for c, q in quotes_uncited]
    md += ["", "_A local check is not the university's scanner. It only sees the sources given to it; the web check in the originality-check skill covers the rest._"]

    summary = {"generated_at": stamp, "target": target, "pass": ok, "problems": problems,
               "prose_words": total_words, "matched_pct": pct(matched_total),
               "sources": len(src_labels), "peers": len(labels) - len(src_labels),
               "top_sources": src_rows[:10], "passages": len(passages), "uncited_quotes": len(quotes_uncited)}
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
        json.dump(summary, open(a.out + ".json", "w", encoding="utf-8"), indent=2)
        print(f"Wrote {a.out}.md and {a.out}.json")
    print("\n".join(md[:12]))
    if problems:
        print("\n".join("  - " + p for p in problems))
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
