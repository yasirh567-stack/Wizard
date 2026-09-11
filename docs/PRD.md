# Steward (Finance Copilot) — Product Requirements Document

**Owner:** Yasir Hassan
**Status:** v1 (MVP) approved for build
**Last updated:** 2026-09-11

This PRD covers the **Finance Copilot** only — the user-facing product. The
**PM Agent** (the system that runs product management on the Copilot's own
telemetry) gets its own PRD once the Copilot exists and produces telemetry
to analyze; see Phase 6 in `ROADMAP.md`. Building the PM Agent's PRD before
the Copilot has any real data to point at would make it exactly the kind of
disconnected-from-reality case study this project is trying not to be —
see `PROBLEM.md`.

## Problem

See `PROBLEM.md` in full. Short version: budgeting apps report what already
happened; almost none convert "I spend too much" into a specific, explained,
achievable plan.

## Target users

Three personas, detailed in `PERSONAS.md`: the Subscription Drifter
(recurring-charge blindness), the Irregular Earner (income variability
breaks category budgets), the Goal-Driven Saver (has a number and a
deadline, no plan). All three are individuals managing personal finances —
not a household/shared-account product; see Non-goals.

## Goals (v1)

1. Turn "I spend too much" into a specific, dollar-denominated recommendation
   in one sitting — connect data in, get a plan out.
2. Surface money a user is already losing without deciding to (recurring
   charges, anomalies) before asking them to change any behavior at all.
3. Make every recommendation defensible — a user (or an interviewer) can ask
   "why" and get a specific, sourced answer, not a generic tip.
4. Let a user see the cost of a plan before committing to it (the simulator),
   so "hit the goal" and "survive the month" are evaluated together.

## Non-goals (v1)

- **Real bank credentials / production data access.** Plaid **Sandbox**
  only. This is a portfolio project, not a licensed financial service —
  handling real account credentials brings compliance obligations
  (data security, regulatory) that are out of scope for what this is.
  See `ARCHITECTURE.md`.
- **Autonomous execution.** Steward recommends; it never cancels a
  subscription, moves money, or contacts a merchant on its own. A
  recommendation engine that can act without the user is a trust and safety
  problem this project isn't taking on. This is a permanent constraint, not
  a v1-only limitation.
- **Households / shared accounts / multi-user.** Single user. See
  `PERSONAS.md`.
- **Investment or brokerage accounts.** Checking, savings, and credit
  accounts only — investment tracking is a different data model and a
  different set of recommendations (asset allocation, not spending).
- **Native mobile.** Web only.
- **Multi-currency.** USD only.

## The core loop

1. **Connect** — link accounts via Plaid Sandbox (or load the bundled
   synthetic dataset to explore without setup).
2. **Understand** — transactions are categorized, recurring charges and
   anomalies are surfaced automatically, with no action required from the
   user to get this far.
3. **Ask** — the user states a goal in plain language ("save $10k this
   year") via the chat interface, or sets one via the dashboard.
4. **Simulate** — the system proposes 2–3 ranked plans, each a concrete set
   of changes with a projected outcome and an explanation.
5. **Decide** — the user picks a plan, a subset of it, or none; the
   forecast updates either way, and next month's recommendations account for
   what was actually accepted vs. ignored.

## Features (v1 / MVP scope)

| # | Feature | Why it's in v1 |
|---|---|---|
| 1 | Transaction ingestion (Plaid Sandbox + synthetic seed dataset) | Nothing else works without transaction data; sandbox avoids real-credential compliance burden while still exercising a real fintech API integration. |
| 2 | Categorization (rule-based + ML classifier, confidence score, manual override) | Every downstream feature (recurring detection, forecasting, recommendations) depends on category-level structure the raw transaction doesn't have. |
| 3 | Recurring-subscription detection | The single highest-confidence research finding (`USER_RESEARCH.md` theme 2) — money lost without an active decision. |
| 4 | Spending anomaly detection | Same category of "surface it before being asked" value as recurring detection; catches one-off issues (a duplicate charge, an unusual merchant) recurring-detection can't. |
| 5 | Cash-flow forecast | Required for the Irregular Earner persona and for any goal ("save $10k by December") to resolve to a monthly number at all. |
| 6 | Recommendation engine with explanations | The actual answer to "what should I change" — the project's core bet. Every recommendation must cite the specific data behind it (research theme 5). |
| 7 | Budget scenario simulator | Lets a user compare plans by survivability, not just by dollar amount (Goal-Driven Saver persona) — this is what makes a recommendation a plan instead of a tip. |
| 8 | LLM natural-language layer (chat) | The interface for goals 1 and 3 — "I'm spending too much, what should I change to save $10k this year" needs to be answerable as asked, not only through form fields. |
| 9 | Auth (email/password, JWT) | Multi-session, deployable product needs real auth even as a single-user tool — also fills a stack gap the author's other projects (HTTP Basic Auth, no-auth) don't cover. |
| 10 | Dashboard (Next.js) | Where 3–9 actually get looked at. |

**Deliberately excluded** from v1 despite being part of the original brief:
a learned (vs. rule-seeded) recommendation-ranking model — v1 ships
rule-based recommendations with logged outcomes, and a learned ranker is a
Phase-2 candidate once there's outcome data to train on (see `ROADMAP.md`);
production AWS hardening beyond a working deploy; a fully general LLM chat
that can answer anything vs. one scoped to this app's data and tools.

## Success metrics

See `METRICS.md` for the full definition. North star: % of (synthetic) users
who reduce discretionary spending after receiving and viewing a
recommendation. Since this ships without a real user base, "users" in v1
means synthetic behavioral profiles run through the same recommendation and
forecasting code paths a real account would hit — disclosed as such, not
presented as real usage data.

## Key risks

Full register in `RISK_REGISTER.md` (next doc pass, Phase 0b). The two
biggest, flagged now because they shape v1 scope directly: (1) categorization
accuracy determines whether anything downstream is trustworthy — a
confidently-wrong category poisons the recommendation built on top of it,
which is why manual override is in v1 scope and not deferred; (2) the
research underneath this PRD is secondary/desk research, not primary — see
`USER_RESEARCH.md` — so personas are directional, not validated, until the
experimentation framework (Phase 7) produces real outcome data.
