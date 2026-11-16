#!/usr/bin/env python3
"""Generic multi-year financial model driven by model.json.

    .venv/bin/python financial_model.py [model.json] [--md]

Produces: profit and loss, cash flow and balance sheet (simplified, no debt), break-even
year, peak funding need, and a sensitivity table. With --md it writes report-ready tables:
  ../report/working/model_tables.md       (include in a chapter: <!-- include: working/model_tables.md -->)
  ../report/working/model_assumptions.md  (include in an appendix)
and always writes ../output/Financial_Model.xlsx (needs openpyxl).

model.json (all money in one currency unit, e.g. INR lakh or USD thousand; see model.example.json):
  currency_label, years (list of labels)
  streams: [{name, volume: [..per year..], price: [..] or number, variable_cost_pct: number}]
  fixed_costs: [{name, values: [..]}]
  capex: [..per year..], depreciation_years: number
  working_capital_pct: number (net working capital as % of revenue)
  tax_rate: number, equity_raised: [..per year..], opening_cash: number
  scenarios: {name: {"volume": x, "price": x, "fixed": x, "variable": x}}   (multipliers)
  assumption_notes: {key: "basis for the assumption"}

Every input is an assumption: label it in the report and keep the basis notes current.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def series(v, n):
    return list(v) if isinstance(v, list) else [v] * n


def run(m: dict, mult: dict | None = None) -> dict:
    mult = mult or {}
    n = len(m["years"])
    fv = lambda k: mult.get(k, 1.0)
    rev_by = {}
    var_cost = [0.0] * n
    for s in m["streams"]:
        vol = [x * fv("volume") for x in series(s["volume"], n)]
        price = [x * fv("price") for x in series(s["price"], n)]
        r = [a * b for a, b in zip(vol, price)]
        rev_by[s["name"]] = r
        pct = s.get("variable_cost_pct", 0) * fv("variable")
        var_cost = [vc + x * pct for vc, x in zip(var_cost, r)]
    revenue = [sum(v[i] for v in rev_by.values()) for i in range(n)]
    fixed_by = {f["name"]: [x * fv("fixed") for x in series(f["values"], n)] for f in m.get("fixed_costs", [])}
    fixed = [sum(v[i] for v in fixed_by.values()) for i in range(n)]
    gross = [r - v for r, v in zip(revenue, var_cost)]
    ebitda = [g - f for g, f in zip(gross, fixed)]
    capex = series(m.get("capex", 0), n)
    life = max(1, m.get("depreciation_years", 5))
    dep = [sum(capex[j] / life for j in range(i + 1) if i - j < life) for i in range(n)]
    ebit = [e - d for e, d in zip(ebitda, dep)]
    tax, carry = [], 0.0
    for e in ebit:
        taxable = e + carry
        if taxable > 0:
            tax.append(taxable * m.get("tax_rate", 0.25)); carry = 0.0
        else:
            tax.append(0.0); carry = taxable
    net = [e - t for e, t in zip(ebit, tax)]
    wc = [r * m.get("working_capital_pct", 0) for r in revenue]
    dwc = [wc[0]] + [wc[i] - wc[i - 1] for i in range(1, n)]
    cfo = [ni + d - w for ni, d, w in zip(net, dep, dwc)]
    cfi = [-c for c in capex]
    equity = series(m.get("equity_raised", 0), n)
    cash, c = [], m.get("opening_cash", 0)
    pre_funding, cf = [], m.get("opening_cash", 0)
    for i in range(n):
        c += cfo[i] + cfi[i] + equity[i]
        cash.append(c)
        cf += cfo[i] + cfi[i]
        pre_funding.append(cf)
    nfa, acc = [], 0.0
    for i in range(n):
        acc += capex[i] - dep[i]
        nfa.append(acc)
    paid_in = [m.get("opening_cash", 0) + sum(equity[: i + 1]) for i in range(n)]
    retained = [sum(net[: i + 1]) for i in range(n)]
    return {
        "years": m["years"], "rev_by": rev_by, "revenue": revenue, "var_cost": var_cost, "gross": gross, "fixed_by": fixed_by,
        "fixed": fixed, "ebitda": ebitda, "dep": dep, "ebit": ebit, "tax": tax, "net": net, "dwc": dwc, "cfo": cfo, "cfi": cfi,
        "equity": equity, "cash": cash, "wc": wc, "nfa": nfa, "paid_in": paid_in, "retained": retained,
        "assets": [a + b + c2 for a, b, c2 in zip(cash, wc, nfa)], "equity_total": [p + r for p, r in zip(paid_in, retained)],
        "breakeven": next((m["years"][i] for i, e in enumerate(ebitda) if e > 0), None),
        "funding_need": max(0.0, -min(pre_funding + [0.0])),
        "gross_margin": [g / r if r else 0 for g, r in zip(gross, revenue)],
    }


def f(x):
    if abs(x) < 0.05:
        return "0.0"
    return f"({abs(x):,.1f})" if x < 0 else f"{x:,.1f}"


def table(title, years, rows):
    out = [title, "", "| Line | " + " | ".join(years) + " |", "|---|" + "---|" * len(years)]
    for label, vals in rows:
        out.append(f"| {label} | " + " | ".join(v if isinstance(v, str) else f(v) for v in vals) + " |")
    return "\n".join(out) + "\n"


def tables_md(m, r):
    y, cur = r["years"], m.get("currency_label", "")
    pl = [(f"Revenue: {k}", v) for k, v in r["rev_by"].items()] + [("**Total revenue**", r["revenue"]), ("Variable costs", [-x for x in r["var_cost"]]),
          ("**Gross profit**", r["gross"]), ("Gross margin", [f"{g:.0%}" for g in r["gross_margin"]])]
    pl += [(f"Fixed: {k}", [-x for x in v]) for k, v in r["fixed_by"].items()]
    pl += [("**EBITDA**", r["ebitda"]), ("Depreciation", [-x for x in r["dep"]]), ("EBIT", r["ebit"]), ("Tax", [-x for x in r["tax"]]), ("**Net profit**", r["net"])]
    cfs = [("Net profit", r["net"]), ("Add back depreciation", r["dep"]), ("Change in working capital", [-x for x in r["dwc"]]), ("**Cash from operations**", r["cfo"]),
           ("Capital expenditure", r["cfi"]), ("Equity raised", r["equity"]), ("**Closing cash**", r["cash"])]
    bs = [("Cash", r["cash"]), ("Net working capital", r["wc"]), ("Net fixed assets", r["nfa"]), ("**Total assets**", r["assets"]),
          ("Paid-in capital", r["paid_in"]), ("Retained earnings", r["retained"]), ("**Total equity**", r["equity_total"])]
    md = table(f"Table X.1: Projected profit and loss ({cur})", y, pl) + "\n"
    md += table(f"Table X.2: Projected cash flow ({cur})", y, cfs) + "\n"
    md += table(f"Table X.3: Projected balance sheet ({cur})", y, bs) + "\n"
    md += f"Table X.4: Sensitivity ({cur})\n\n| Scenario | Final-year revenue | Final-year EBITDA | Break-even | Funding need |\n|---|---|---|---|---|\n"
    for name, mult in {"Base case": {}, **m.get("scenarios", {})}.items():
        s = run(m, mult)
        md += f"| {name} | {f(s['revenue'][-1])} | {f(s['ebitda'][-1])} | {s['breakeven'] or 'beyond plan'} | {f(s['funding_need'])} |\n"
    md += "\nRenumber the X in the captions to the chapter number before building.\n"
    return md


def assumptions_md(m):
    notes = m.get("assumption_notes", {})
    out = ["Table X.5: Financial model assumptions", "", "| Assumption | Value | Basis |", "|---|---|---|"]
    for s in m["streams"]:
        out.append(f"| {s['name']}: volume | {s['volume']} | {notes.get(s['name'] + ' volume', '[NEEDS: basis]')} |")
        out.append(f"| {s['name']}: price | {s['price']} | {notes.get(s['name'] + ' price', '[NEEDS: basis]')} |")
        out.append(f"| {s['name']}: variable cost | {s.get('variable_cost_pct', 0):.0%} of revenue | {notes.get(s['name'] + ' variable', '[NEEDS: basis]')} |")
    for fc in m.get("fixed_costs", []):
        out.append(f"| Fixed: {fc['name']} | {fc['values']} | {notes.get(fc['name'], '[NEEDS: basis]')} |")
    for k in ("capex", "depreciation_years", "working_capital_pct", "tax_rate", "equity_raised", "opening_cash"):
        if k in m:
            out.append(f"| {k.replace('_', ' ')} | {m[k]} | {notes.get(k, '[NEEDS: basis]')} |")
    return "\n".join(out) + "\n"


def write_xlsx(m, r, path):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        print("openpyxl not installed: skipped the Excel file")
        return
    wb = Workbook()
    ws = wb.active
    ws.title = "Assumptions"
    ws.append(["Input", "Value"])
    for k, v in m.items():
        if k != "assumption_notes":
            ws.append([k, json.dumps(v)])
    for name, keys in {"P&L": ["revenue", "var_cost", "gross", "fixed", "ebitda", "dep", "ebit", "tax", "net"],
                       "Cash flow": ["net", "dep", "dwc", "cfo", "cfi", "equity", "cash"],
                       "Balance sheet": ["cash", "wc", "nfa", "assets", "paid_in", "retained", "equity_total"]}.items():
        sh = wb.create_sheet(name)
        sh.append(["Line"] + r["years"])
        for k in keys:
            sh.append([k] + [round(x, 2) for x in r[k]])
    for sh in wb.worksheets:
        for c in sh[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="4D4D4F")
        sh.column_dimensions["A"].width = 28
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    print("Wrote", path)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mpath = Path(args[0]) if args else HERE / "model.json"
    if not mpath.exists():
        sys.exit(f"{mpath} not found. Copy model.example.json to model.json and edit it.")
    m = json.loads(mpath.read_text(encoding="utf-8"))
    r = run(m)
    bal = max(abs(a - e) for a, e in zip(r["assets"], r["equity_total"]))
    print(f"Break-even: {r['breakeven'] or 'beyond plan'}; peak funding need: {f(r['funding_need'])}; balance check diff: {bal:.6f}")
    if bal > 1e-6:
        print("WARNING: balance sheet does not balance; check the inputs")
    if "--md" in sys.argv:
        w = HERE.parent / "report" / "working"
        w.mkdir(parents=True, exist_ok=True)
        (w / "model_tables.md").write_text(tables_md(m, r), encoding="utf-8")
        (w / "model_assumptions.md").write_text(assumptions_md(m), encoding="utf-8")
        print("Wrote report/working/model_tables.md and model_assumptions.md")
    write_xlsx(m, r, HERE.parent / "output" / "Financial_Model.xlsx")
