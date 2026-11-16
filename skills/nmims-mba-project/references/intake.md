# Intake: questions to ask, in this order

Ask in rounds. Wait for answers before the next round. Tell the student that short, rough answers in their own words are best, any language mix is fine, and "no" or "not sure" are valid answers. Record every answer in the project's `OPEN_ITEMS.md` under the round's heading, word for word where it is their own idea or experience.

Never fill a gap with an invented fact. Unknowns become `[NEEDS: ...]` in the report.

## Round 1: the project (ask first, before creating the folder)
1. **Project name**: a short working name (used for the folder: `<student>-<topic>`).
2. **Project type**: Problem-Solving Proposal, Business Plan, or Research Project? (If unsure, see `formats-and-rubrics.md` "Choosing a format" and recommend one.)
3. **Specialisation**: Business Management, Finance, HR, Marketing, or Operations & Data Science?

Then create the folder: `bash <skill>/scripts/new_project.sh <slug> <type> --install`.

## Round 2: pre-submission work from the portal and anything already done
4. **Semester III pre-work**: what was submitted on the portal (Exams > Project Pre-work)? Ask for the exact **title**, the **description**, the format chosen, and the **faculty feedback or approval status**. A screenshot or copy-paste is ideal.
5. Is the **title registered** for Semester IV? Exact wording (the cover must match it, at most 20 words).
6. **Work already done**: drafts, notes, a business requirements document, data, interviews, a survey, a deck, earlier assignments on the same topic. Ask for the files and save them in the project's `research/student-input/`. Read them before planning; reuse the student's own ideas and words, and run the originality check on anything that came from elsewhere.

## Round 3: the idea, in their own words
7. "Describe your project idea as you would explain it to a friend." (free text, no format)
8. What problem does it solve, and who feels it most?
9. Why does this matter to you? Any real incident or personal experience? (roughly what happened, amounts if known, how it ended)
10. What solution or outcome do you have in mind, even roughly?

## Round 4: questions for the chosen type
**Problem-Solving Proposal**
- Which organisation and department? Is it the student's employer? Can it be named? If no access, which public company could serve as the case (annual reports, filings, published policies)?
- What are the visible symptoms, since when, and how are they measured (any numbers)?
- Who is affected inside and outside the organisation (stakeholders)?
- What has been tried already, and what constraints exist (budget, people, rules, technology)?
- Which data or documents can be used?

**Business Plan**
- Business name (or working name), what is sold, to whom, where.
- Target customer: who exactly, how many, how they buy today.
- Competitors the student knows; what makes this different.
- Pricing idea, cost drivers, team, starting capital and its source.
- Stage: idea, prototype, first customers?

**Research Project**
- Research question (one sentence) and why it matters.
- Variables or themes; any hypothesis.
- Population and how the student can reach them (sampling access).
- Preferred method: survey, interviews, secondary data; tools known (Excel, SPSS, Python).

## Round 5: survey (always ask)
11. "Would you like a short survey to strengthen the project?" Explain: it adds primary evidence (Research projects need it; it lifts marks for the other two formats).
    - **Yes**: draft the form with `survey.md`, share it as text the student can paste into Google Forms or Microsoft Forms, agree a target (30-50 responses) and a deadline, and ask them to send the response export (CSV) back into `research/survey/`.
    - **Already have one**: ask for the form and the responses export.
    - **Skip**: record "survey skipped by student on <date>" in `OPEN_ITEMS.md`; design the report so it does not depend on survey results; keep Appendix A as the instrument for future use. For a Research Project, warn that it cannot pass without primary data and ask again.

## Round 6: cover and admin
12. Full name, SAP ID, exam cycle (e.g. December 2026), faculty guide (or none).
13. Deadline for submission, and when they can review drafts.

## Round 7: reflection (Problem-Solving only, before writing that chapter)
Use `reflection-questions.md` (decisions changed, hardest trade-off, who helped, feedback and response, what they led, surprises, career use).

## During the project
Ask whenever a choice belongs to the student: scope, organisation naming, any number they must supply, approval of the cover, which findings to emphasise. Do not guess.
