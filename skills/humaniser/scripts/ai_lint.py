#!/usr/bin/env python3
"""ai_lint.py - Markdown-aware AI-pattern checker for reports and academic prose.

Why this exists: generic stylometry scorers count table rows, bullets and
headings as sentences, which inflates cadence variance and hides AI tells.
This script extracts running prose only, then reports:
  * AI vocabulary density (academic/business list, per 1,000 words)
  * stock phrases and transitions
  * em/en dashes, curly quotes, bold density, inline-header bullets
  * sentence-length mean / CV (burstiness) on prose only
  * per-section breakdown so you know where to rewrite first

Stdlib only. Usage:
  python3 ai_lint.py FILE.md [--json] [--sections] [--dump-prose OUT.txt]
Exit code 0 always (it is a gauge, not a gate).
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# --- word lists ---------------------------------------------------------
# Single words (matched case-insensitively on word boundaries, simple stems).
AI_WORDS = """
additionally align aligns aligned crucial delve delves enduring enhance enhances
enhancing fostering foster fosters garner highlight highlights highlighting
interplay intricate intricacies pivotal showcase showcases showcasing tapestry
testament underscore underscores underscoring valuable vibrant landscape
leverage leverages leveraging multifaceted prioritize prioritise robust seamless
seamlessly comprehensive holistic paradigm ecosystem synergy synergies empower
empowers empowering unlock unlocks unprecedented transformative profound
meticulous meticulously nuanced streamline streamlines streamlining facilitate
facilitates furthermore moreover notably consequently thereby whilst amidst
realm navigate navigating bolster bolsters commendable noteworthy invaluable
elevate elevates cutting-edge game-changer groundbreaking revolutionize
revolutionise dynamic myriad plethora pertinent paramount utilize utilise
utilizes utilises utilization endeavor endeavour embark embarks
""".split()

AI_PHRASES = [
    "plays a crucial role", "plays a vital role", "plays a pivotal role",
    "it is important to note", "it is worth noting", "it's worth noting",
    "in today's fast-paced", "in today's digital", "in the realm of",
    "a testament to", "serves as a", "stands as a", "not only", "but also",
    "in conclusion", "in summary", "overall,", "to sum up", "at its core",
    "harness the power", "paves the way", "pave the way", "the evolving landscape",
    "a wide range of", "a myriad of", "a plethora of", "in order to",
    "due to the fact that", "with regard to", "in terms of", "when it comes to",
    "valuable insights", "key takeaways", "deep dive", "rapidly evolving",
    "ever-evolving", "ever-changing", "game changer", "it is essential",
    "it is crucial", "this ensures", "ensuring that", "setting the stage",
    "marking a", "underscores the importance", "highlights the importance",
    "in connection with", "in association with", "rather than",
    "despite these challenges", "future outlook", "looking ahead",
    "the future looks bright", "strategic imperative", "value proposition",
    "best-in-class", "world-class", "state-of-the-art", "end-to-end",
]

CURLY = "“”‘’"

# --- markdown -> prose ----------------------------------------------------

def extract_sections(md: str):
    """Yield (heading, prose_text, stats) with tables/code/mermaid/math removed."""
    lines = md.splitlines()
    sections, cur_head, buf = [], "(preamble)", []
    in_fence = False
    in_math = False
    bullets = inline_hdr_bullets = 0
    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if s.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if s.startswith("$$"):
            if not (s.endswith("$$") and len(s) > 2):
                in_math = not in_math
            continue
        if in_math:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", s)
        if m:
            sections.append((cur_head, "\n".join(buf), bullets, inline_hdr_bullets))
            cur_head, buf, bullets, inline_hdr_bullets = m.group(2), [], 0, 0
            continue
        if s.startswith("|") or re.match(r"^[-*_]{3,}$", s) or not s:
            buf.append("")  # paragraph break
            continue
        b = re.match(r"^([*+-]|\d+\.)\s+(.*)", s)
        if b:
            bullets += 1
            if re.match(r"^\*\*[^*]{1,80}\*\*\s*:?", b.group(2)) or re.match(r"^\*\*[^*]{1,80}:\*\*", b.group(2)):
                inline_hdr_bullets += 1
            s = b.group(2)
            buf.append("")
        if s.startswith(">"):
            s = s.lstrip("> ")
        buf.append(s)
    sections.append((cur_head, "\n".join(buf), bullets, inline_hdr_bullets))
    return sections


def clean_inline(text: str) -> str:
    text = re.sub(r"`[^`]*`", " ", text)
    text = text.replace("\\$", "USD")            # escaped currency first
    text = re.sub(r"\$[^$\n]{1,80}\$", " X ", text)  # short inline math only
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", " ", text)
    return text


def sentences(text: str):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out = []
    for p in paras:
        p = " ".join(p.split())
        # protect common abbreviations
        p2 = re.sub(r"\b(e\.g|i\.e|etc|vs|Dr|Mr|Ms|al|approx|Inc|Ltd|No)\.", lambda m: m.group(0).replace(".", "<DOT>"), p)
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"(])", p2)
        for s in parts:
            s = s.replace("<DOT>", ".").strip()
            if len(re.findall(r"[A-Za-z]+", s)) >= 4:  # ignore fragments/labels
                out.append(s)
    return out


def analyse(text_raw: str, bullets: int, ihb: int):
    bold = len(re.findall(r"\*\*[^*]+\*\*", text_raw))
    text = clean_inline(text_raw)
    plain = re.sub(r"\*+", "", text)
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", plain)
    wc = len(words)
    low = plain.lower()
    hits = {}
    for w in AI_WORDS:
        n = len(re.findall(r"\b" + re.escape(w) + r"\b", low))
        if n:
            hits[w] = n
    phr = {}
    for p in AI_PHRASES:
        n = low.count(p)
        if n:
            phr[p] = n
    sents = sentences(plain)
    lens = [len(re.findall(r"[A-Za-z0-9]+", s)) for s in sents]
    mean = statistics.mean(lens) if lens else 0
    cv = (statistics.pstdev(lens) / mean) if len(lens) > 1 and mean else 0
    return {
        "words": wc,
        "sentences": len(sents),
        "sent_mean": round(mean, 1),
        "sent_cv": round(cv, 3),
        "ai_words": sum(hits.values()),
        "ai_words_per_1k": round(1000 * sum(hits.values()) / wc, 1) if wc else 0,
        "ai_word_hits": dict(sorted(hits.items(), key=lambda x: -x[1])),
        "phrase_hits": dict(sorted(phr.items(), key=lambda x: -x[1])),
        "em_dashes": text_raw.count("—"),
        "en_dashes": text_raw.count("–"),
        "curly_quotes": sum(text_raw.count(c) for c in CURLY),
        "bold_spans": bold,
        "bold_per_1k": round(1000 * bold / wc, 1) if wc else 0,
        "bullets": bullets,
        "inline_header_bullets": ihb,
        "_sentences": sents,
    }


def verdict(r):
    flags = []
    if r["ai_words_per_1k"] > 8: flags.append("HIGH AI vocabulary (>8/1k)")
    elif r["ai_words_per_1k"] > 4: flags.append("moderate AI vocabulary (4-8/1k)")
    if r["sentences"] >= 8 and r["sent_cv"] < 0.40: flags.append("uniform sentence length (CV<0.40)")
    if r["sent_mean"] > 26: flags.append("long average sentence (>26 words)")
    if r["em_dashes"]: flags.append(f"{r['em_dashes']} em dash(es)")
    if r["curly_quotes"]: flags.append("curly quotes")
    if r["bold_per_1k"] > 6: flags.append("bold overuse")
    if r["inline_header_bullets"] >= 3: flags.append("inline-header bullet lists")
    if sum(r["phrase_hits"].values()) >= 5: flags.append("stock phrases")
    return flags


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sections", action="store_true", help="per-section table")
    ap.add_argument("--dump-prose", help="write extracted prose (for other scorers)")
    a = ap.parse_args()
    md = Path(a.file).read_text(encoding="utf-8")
    secs = extract_sections(md)
    whole_txt = "\n\n".join(t for _, t, _, _ in secs)
    total = analyse(whole_txt, sum(s[2] for s in secs), sum(s[3] for s in secs))
    if a.dump_prose:
        Path(a.dump_prose).write_text("\n\n".join(total["_sentences"]), encoding="utf-8")
    per = []
    for h, t, b, i in secs:
        r = analyse(t, b, i)
        if r["words"] >= 60:
            per.append((h, r))
    if a.json:
        out = {k: v for k, v in total.items() if not k.startswith("_")}
        out["flags"] = verdict(total)
        out["sections"] = [{"heading": h, **{k: v for k, v in r.items() if not k.startswith("_") and k not in ("ai_word_hits", "phrase_hits")}, "flags": verdict(r)} for h, r in per]
        print(json.dumps(out, indent=2))
        return
    t = total
    print(f"== ai_lint: {a.file}")
    print(f"Prose words: {t['words']}  sentences: {t['sentences']}  mean len: {t['sent_mean']}  CV: {t['sent_cv']}")
    print(f"AI vocab: {t['ai_words']} ({t['ai_words_per_1k']}/1k)  stock phrases: {sum(t['phrase_hits'].values())}")
    print(f"Em dashes: {t['em_dashes']}  curly quotes: {t['curly_quotes']}  bold: {t['bold_spans']} ({t['bold_per_1k']}/1k)  bullets: {t['bullets']} (inline-header: {t['inline_header_bullets']})")
    print("Top AI words:", ", ".join(f"{k}x{v}" for k, v in list(t["ai_word_hits"].items())[:20]) or "-")
    print("Stock phrases:", ", ".join(f"'{k}'x{v}" for k, v in list(t["phrase_hits"].items())[:15]) or "-")
    print("FLAGS:", "; ".join(verdict(t)) or "none")
    if a.sections:
        print("\nPer section (>=60 prose words), worst first:")
        per.sort(key=lambda x: (-x[1]["ai_words_per_1k"]))
        for h, r in per:
            print(f"  {r['ai_words_per_1k']:>5}/1k  CV {r['sent_cv']:<5} mean {r['sent_mean']:<5} {h[:60]}  {'| ' + '; '.join(verdict(r)) if verdict(r) else ''}")


if __name__ == "__main__":
    main()
