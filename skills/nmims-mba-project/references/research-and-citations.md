# Evidence, sources and citations

## Rules
1. **Every number has a source the examiner could open.** If a statistic cannot be traced to its original publisher, drop it or rephrase without it. Never keep a number because it sounds right.
2. **Never invent** sources, quotes, interviews, survey results, amounts or experiences. Missing information becomes `[NEEDS: ...]` (only the student can supply) or `[VERIFY: ...]` (check a live source). Final builds refuse to run while either remains.
3. **Grade each source** and phrase claims to match:
   - A: primary (regulatory filings, laws and regulator circulars, company legal terms and help pages, government reports, peer-reviewed papers). State plainly.
   - B: third-party guides, news, analyst blogs. Say "reported".
   - C: user reviews, forums, Trustpilot. Use only to show a pattern of complaints; never as proof.
4. **APA 7th edition**, alphabetical; "n.d." when no date; organisation abbreviations in the first citation, e.g. (Insurance Regulatory and Development Authority of India [IRDAI], 2015). Same author and year: 2025a, 2025b.
5. Run `scripts/check_citations.py <report-dir> --doi` before every final build.

## Primary sources that worked (and how to reach them)
| Need | Source | Tip |
|---|---|---|
| US-listed company numbers, risk factors, fee changes | SEC EDGAR: 10-K, 10-Q, 20-F, ARS | Quarterly 10-Qs often state policy changes more precisely than annual reports. Long filings: fetch in 100k-character chunks |
| Australian-listed company results | ASX announcements (mirrored on investor sites) | Check the currency (AUD) |
| Terms of service and legal terms | Company legal pages; versioned PDFs on PactSafe (`<company>.pactsafe.io/versions/...pdf`) | Record the version date from the PDF metadata |
| DOIs and article details | Crossref API: `https://api.crossref.org/works/<doi>` or `?query.bibliographic=` | A wrong DOI is a common error; always check |
| Indian policy and statistics | NITI Aayog, PIB, RBI master directions, IRDAI regulations, India Code | Help pages often block bots: find the text via search snippets, then cite the official URL |
| Industry surveys and indices | Industry bodies, associations, research institutes (e.g. NASSCOM, CII, FICCI, IBEF, RBI and NITI Aayog reports) | Older surveys are fine if dated honestly |

Many company help centres and some legal pages return HTTP 403 to automated tools. Use web search snippets to find wording, then confirm in a primary document such as a filing or a versioned PDF.

## Frameworks examiners expect (cite the originals)
Five whys / problem tree; PESTEL; SWOT; stakeholder power-interest grid; Porter's five forces; business model canvas (Osterwalder & Pigneur, 2010); weighted decision matrix with sensitivity; RACI; Gantt; break-even and sensitivity; theory as relevant, for example transaction costs (Coase, 1937; Williamson, 1985), information asymmetry (Akerlof, 1970), insurance markets (Rothschild & Stiglitz, 1976), two-sided platforms (Rochet & Tirole, 2003; Armstrong, 2006).
