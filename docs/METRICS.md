# Steward — Metrics

**Owner:** Yasir Hassan
**Status:** v1
**Last updated:** 2026-09-11

## North star

**% of users who reduce discretionary spending by ≥10% within 30 days of
viewing a recommendation, measured against their trailing 90-day category
baseline.**

Why this framing specifically:

- **"Viewing," not "receiving."** A recommendation generated but never seen
  can't have caused anything — gating on view time gives a clean pre/post
  window instead of an ambiguous one.
- **Trailing 90-day baseline, not calendar-month-over-month.** A single
  unusually expensive or cheap prior month would distort a month-over-month
  comparison; 90 days smooths seasonal one-offs (a birthday month, a holiday
  month) without needing a full year of history a new account won't have.
- **Discretionary, not total, spending.** Total spending falling because
  rent went up elsewhere isn't a Steward outcome. The metric has to isolate
  the category the product actually has a causal path to affecting.
- **10% threshold, not "any reduction."** A 1% reduction is within normal
  week-to-week noise for most spending categories; 10% is large enough to
  plausibly attribute to an actual behavior change rather than variance.
  This threshold is a v1 assumption, not a validated one — revisit once
  Phase 7's experimentation framework has real variance data to check it
  against.

## Guardrail metrics

Metrics the north star is not allowed to improve at the expense of:

- **No increase in projected-overdraft rate** among users who acted on a
  recommendation (projected end-of-month balance below $0, from the
  forecast). A recommendation that hits the savings number by starving
  essential spending is a failure mode, not a win.
- **No increase in missed-recurring-payment flags.** Same failure mode,
  narrower signal — a plan shouldn't recommend cutting something that turns
  out to be a bill.
- **Recommendation dismissal rate stays flat or improves.** A rising
  dismissal rate is an early signal that recommendations are becoming less
  relevant (e.g., overfit to one persona) before it shows up in the north
  star itself.

## Input / diagnostic metrics

Metrics that don't define success on their own but explain movement in the
north star:

| Metric | What it's a leading indicator of |
|---|---|
| Recommendation acceptance rate (viewed → at least one action taken) | Whether recommendations are persuasive at all, upstream of whether they work |
| Categorization precision/recall vs. a held-out labeled set | Trust in everything built on top of categorization (PRD risk #1) |
| Forecast error (MAPE, 30-day-out cash flow) | Whether "can I afford this" answers are credible |
| Time from account-connect to first recommendation shown | Activation — the core loop is worthless if it doesn't complete |
| Recurring-charge detection precision (flagged vs. confirmed-actually-recurring) | False positives here directly damage trust in every other recommendation |

## How this connects to experimentation

Different recommendation *strategies* (e.g., rule-ranked vs. a learned
ranker once one exists; leading with recurring-charge cuts vs. leading with
category cuts) are compared against the north star and guardrails via the
A/B framework built in Phase 7 (`ROADMAP.md`). The north star is deliberately
defined now, before that framework exists, so strategy comparisons have a
fixed target to optimize instead of a metric invented after the fact to
justify whichever result came back.

## Honesty note

v1 has no real user base. Every number this project reports is either (a) a
code-quality/model metric measured against real held-out data (categorization
precision, forecast MAPE — these are real, not synthetic) or (b) a behavioral
metric (north star, guardrails, acceptance rate) measured against synthetic
user-behavior simulations, disclosed as such everywhere it's reported. The
two categories are never presented the same way.
