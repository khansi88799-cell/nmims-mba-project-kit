# Academic / MBA mode

Use this when the text goes to an examiner: MBA projects, assignments, dissertations, university reports. It replaces the "Personality and Soul" guidance in SKILL.md. Examiners want a credible student voice, not a blogger and not a consultancy brochure.

## What a human MBA report sounds like

- **Evidence first, claim second.** "The company's 2024 annual report shows logistics costs at 9% of revenue, up from 7% two years earlier (Company Ltd., 2024). On sales of INR 400 crore, that is INR 8 crore more per year." Not: "Logistics costs significantly erode profitability."
- **Measured verbs.** suggests, indicates, appears, is likely to, in this case. Avoid: proves, eliminates, guarantees, revolutionises, ensures (unless it is literally a guarantee).
- **Specific over grand.** Name the organisation, the year, the rupee/dollar figure, the department, the person's role. Drop "the global landscape", "the modern economy".
- **Honest limits.** Say what the data cannot show and where an assumption was made. One clear limitation beats three hedges per sentence.
- **Indian English is fine.** If the author writes "lakh", "crore", "the client went incommunicado", keep it. Stay consistent on British or American spelling across the whole document (NMIMS accepts either; British is common).
- **Reasonable sentence length.** Mostly 12-25 words, some short ones (6-10) for emphasis, the occasional long one for a chain of reasoning. Avoid stacking three 35-word sentences.

## Where first person belongs

| Section | First person? | Example |
|---|---|---|
| Executive summary, situational analysis, solution, impact | No (or "this project", "the proposal") | "The proposal targets retail customers in tier-2 cities ordering more than twice a month." |
| Methodology / data collection | Yes, sparingly | "I surveyed 42 store managers through two LinkedIn groups in October 2026." |
| Reflection and learning (rubric: leadership, teamwork, decisions) | Yes, required | "My first draft priced the premium at 1%. When I ran the loss numbers, the pool ran dry in month four, so I moved it to 3%." |

Reflection must come from the author's real experience. Ask the author for: a decision they changed, a disagreement and how it was resolved, feedback they received, something that failed. Do not invent these. Mark gaps as `[NEEDS: real example from author]`.

## Structure rules for report chapters

1. Paragraphs carry the argument. Bullets are for steps, criteria and short lists only, never `**Label:** sentence` walls.
2. Every table and figure gets a number, a caption ("Table 4.2: PESTEL summary") and one or two sentences in the text that say what the reader should notice. Do not just say "as shown below".
3. Every framework (SWOT, PESTEL, Porter, stakeholder grid, RACI) ends with a "so what": which finding drives which decision later in the report.
4. Headings: sentence case or consistent title case, numbered (4.2, 4.3). No colons-and-subtitles in every heading.
5. Bold: only for table headers and the rare key term on first use.
6. No signposting filler ("This chapter delves into..."). One orienting line per chapter is enough.

## Words to replace in academic drafts

| AI-flavoured | Plainer academic choice |
|---|---|
| leverage | use, draw on |
| robust | reliable, well-tested, strong |
| seamless(ly) | (delete) / without extra steps |
| comprehensive | full, detailed |
| holistic | overall, combined |
| paradigm shift | change, shift |
| ecosystem | market, network, set of firms |
| empower | allow, give X the means to |
| facilitate | help, make possible |
| unprecedented | (give the comparison instead) |
| furthermore / moreover / additionally | also, in addition, (or just start the sentence) |
| whilst | while |
| profound | large, major (or quantify) |
| plays a crucial role | matters because..., is needed for... |
| eliminates (risk) | reduces, removes most of |
| it is important to note that | (delete) |

## Citations (APA 7th, the usual NMIMS expectation)

- In-text: (Coase, 1937); (Rochet & Tirole, 2003); three or more authors: (Weyl et al., 2022).
- Every in-text citation appears in References and vice versa.
- Corporate reports: Company Ltd. (2024). *Annual report 2023-24*. URL
- Verify every statistic's source before keeping it. If a number cannot be traced, rephrase without it or label it as the author's estimate with the basis shown.

## Final checks before handing back

- Run `ai_lint.py --sections`. All body chapters: AI vocab < 3/1k, CV 0.45-0.80, 0 em dashes, no inline-header bullets.
- Read the opening sentence of every paragraph in a row. If they all start "The ..." or all start with a transition, vary them.
- Check that numbers match across chapters (summary vs financial chapter vs appendix).
- List every `[NEEDS: ...]` for the author.
