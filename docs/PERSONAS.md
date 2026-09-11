# Steward — Personas

**Owner:** Yasir Hassan
**Status:** v1
**Last updated:** 2026-09-11

Three personas, each mapped to a specific research theme in
`USER_RESEARCH.md` and a specific feature area in `PRD.md`. Not designed to
be exhaustive — designed to be traceable, so every MVP feature has a named
reason to exist.

---

## 1. The Subscription Drifter

**Grounded in:** research theme 2 (subscription creep) and theme 3 (people
react to totals, not trends).

Steady paycheck, steady job. Doesn't think of themself as a big spender and
is mildly defensive when a budgeting app implies otherwise — and is usually
*right* about their big-ticket spending (rent, groceries, car payment are
all reasonable). What they're wrong about is the long tail: four
subscriptions signed up for during free trials 18 months ago, a gym
membership from a January they don't remember committing to, a streaming
bundle that duplicates one they already have. None of these individually
look alarming. The sum does.

**What breaks existing tools for them:** a category dashboard shows
"Subscriptions: $187/month" as one number among many, with the same visual
weight as "Groceries: $410/month" — nothing marks the $187 as unusually
*fixable* compared to the $410.

**What they need from Steward:** automatic recurring-charge detection that
surfaces the full list unprompted, sorted by "you could cancel this with one
click and probably wouldn't notice" rather than by dollar amount.

---

## 2. The Irregular Earner

**Grounded in:** research theme 6 (income irregularity breaks category
tools).

Freelance or contract income — deposits land on no fixed schedule and vary
2–3x between a good month and a slow one. Has tried category budgeting tools
and abandoned them within weeks, not from lack of discipline but because the
tools' core assumption (a predictable monthly paycheck to divide into
categories) doesn't hold. Doesn't ask "am I over budget in Dining this
month" — asks "if I take this trip, can I still make rent in five weeks."

**What breaks existing tools for them:** category budgets reset monthly on
a calendar the user's income doesn't follow, so "on track" and "over budget"
signals are frequently wrong in both directions.

**What they need from Steward:** cash-flow-forward forecasting keyed to
actual account balance trajectory, not a monthly category allowance — the
forecast is the primary view, categories are secondary.

---

## 3. The Goal-Driven Saver

**Grounded in:** research theme 4 (people want prescriptive moments, not
more charts) and theme 5 (trust requires visible reasoning) — this is also
the persona in the project's own motivating example ("save $10k this year").

Has a specific, dated financial target — a house down payment, an emergency
fund, a wedding, paying off a specific debt. Knows the number and the
deadline. Does not know the monthly behavior change required to hit it, and
finds generic advice ("spend less," "save more") useless because it doesn't
resolve to a plan they can start today.

**What breaks existing tools for them:** goal-tracking features in most
apps are a progress bar toward a savings *total* — they don't reverse-
engineer the goal into "cut X, keep Y, and you'll hit it by the deadline,"
and they don't show what happens if the user only does half of it.

**What they need from Steward:** the scenario simulator and recommendation
engine — enter a goal and deadline, get 2–3 ranked, explained plans, each
showing the specific spending changes required and the trade-off of doing
less than the full plan.

---

## Explicitly not a persona (yet)

**Couples/household shared finances.** Real and common, but it's a
different product surface (shared accounts, permissions, whose transaction
is whose) layered on top of everything above. Deferred — see Non-goals in
`PRD.md` and Phase 3+ in `ROADMAP.md`.
