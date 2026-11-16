# Changelog

All notable changes to the Humaniser skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-04-22

### Added

- Initial public release
- Full catalogue of twenty-five AI writing patterns across five groups (content, language, style, communication artefacts, filler)
- Self-audit pass: after the first rewrite, the skill prompts itself with "What makes the below so obviously AI generated?" and does a second pass on the tells it caught
- "Personality and Soul" section pushing for voice, rhythm variation, stated opinions, and admitted uncertainty in rewritten output
- Worked full example in `EXAMPLE.md`
- MIT licence

## [2.4.0-local] - 2026-11-05

### Added
- Mode selection (casual / academic / business) and non-negotiables (no invented facts, keep citations and numbers)
- `references/academic-mba.md`: examiner-facing voice, first-person rules by section, structure, APA 7, word swaps
- `scripts/ai_lint.py`: Markdown-aware, prose-only gauge (AI vocabulary per 1k, sentence CV, em dashes, bold, inline-header bullets, per-section ranking)
- Patterns 26-33 from the 2026 Wikipedia revision: vague association, contrast templates, 2025-26 vocabulary, bold-label bullet walls, section signposting, citation red flags, uniform paragraph shape, style drift
### Changed
- Pattern 25 relaxed in academic mode (standard compound-modifier hyphens stay)
