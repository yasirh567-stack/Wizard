# Steward — User Research

**Owner:** Yasir Hassan
**Status:** v1
**Last updated:** 2026-09-11

## Methodology — read this section first

This is a portfolio project with no real user base, so there was no primary
research (no real interviews, no real surveys). Writing this document as if
there had been would be dishonest and would fall apart under any follow-up
question. What follows instead is **desk research + synthesis**: publicly
documented, widely-reported patterns in how people actually use budgeting
apps — recurring complaints in App Store / Play Store reviews of tools like
YNAB, Copilot Money, and Mint (before its 2024 shutdown), common threads in
r/personalfinance and r/ynab, and established behavioral-economics findings
on budgeting (e.g. why category budgets get abandoned, why people
underestimate recurring costs) — synthesized into the themes below and used
to ground the personas in `PERSONAS.md`.

If this were a funded product, the next step before writing a PRD would be
5–8 real interviews against the questions below. That's out of scope here,
and the PRD is written knowing the research underneath it is secondary, not
primary — see `PRD.md`'s risk section.

## Research questions

1. Why do people stop using budgeting apps after the first month or two?
2. When someone says "I spend too much," what are they actually reacting to —
   a specific transaction, a monthly total, or a vague feeling?
3. What do existing tools get right that shouldn't be thrown out?
4. What would make a recommendation feel trustworthy enough to act on, versus
   easy to dismiss?

## Synthesized themes

**1. Category budgets are set once and abandoned.** The near-universal
complaint about envelope/category-budgeting tools (YNAB being the most
cited) is the maintenance burden: categories need constant re-adjustment,
and a single overspent category makes the whole budget feel "broken" for the
rest of the month. This argues against Steward leading with manual category
limits as the primary interaction.

**2. Subscription creep is the single most-mentioned "gotcha."** Recurring
charges that started as a trial, a gift, or a one-time impulse and were never
canceled show up constantly in "how did I not notice this" anecdotes. This is
a high-confidence signal that automatic recurring-charge detection is
higher-value than most category-level insight.

**3. People react to totals, not trends.** The complaint "I opened the app,
saw a scary number, and closed it" recurs — dashboards that lead with a
big negative-feeling total without an accompanying "here's what to do about
it" tend to get abandoned specifically because they produce anxiety without
agency.

**4. Retrospective apps get used once, prescriptive moments get used
repeatedly.** Feature requests across these communities skew toward "tell me
what to change," not "show me another chart." This is the strongest single
argument for Steward's core bet: recommendations, not just dashboards.

**5. Trust in a recommendation depends on visible reasoning.** Generic
advice ("spend less on dining") gets dismissed; specific, sourced claims
("you've been charged $14.99 by [merchant] for 11 straight months") get
acted on. This directly shapes the "Explains why" requirement in `PRD.md`.

**6. Income irregularity breaks category-based tools entirely.** Budgeting
apps built around a stable monthly paycheck assumption are reported as
close to unusable by freelance/variable-income users, who instead want
cash-flow-forward visibility ("can I afford this in 3 weeks") over
category-accuracy. This is the basis for the Irregular Earner persona.

## What this research does not tell us

Desk research can surface *what people complain about*; it can't validate
*whether Steward's specific recommendations actually change behavior*. That
question is answered later, empirically, once the PM Agent's experimentation
framework exists (`docs/METRICS.md`, Phase 7 in `ROADMAP.md`) — synthetic
user-behavior simulation stands in for a real population, and is disclosed
as such wherever it's used.
