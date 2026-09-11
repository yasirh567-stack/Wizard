# Steward — Roadmap

**Last updated:** 2026-09-11

This exists to make one thing explicit: the original brief for this project
(full ML pipeline + LLM layer + autonomous PM agent + production AWS +
multi-arm experimentation platform, all at once) is a lot more than a v1
should try to ship simultaneously. This roadmap sequences it instead, the
same way Momentum's roadmap sequenced its four procrastination mechanisms
rather than building all of them shallowly at once.

## Phase 0 — Planning

- **0a (this commit):** problem statement, research, personas, PRD, metrics,
  architecture.
- **0b (next):** backlog, risk register, and a sprint-1 scope cut — the
  detailed "what actually gets built first, in what order, inside Phase 1"
  breakdown, same role `SPRINT_1.md` played for Momentum.

**Exit criteria:** every doc above exists and cross-references correctly;
nothing in Phase 1 starts until 0b is done.

## Phase 1 — Backend skeleton

FastAPI project structure, PostgreSQL schema (users, accounts, transactions,
categories, budgets, recommendations, events), JWT auth, Docker Compose
(API + Postgres + Redis), Plaid Sandbox connection + sync, a CSV-upload
fallback path, and a synthetic seed-data generator for demoing without
setting up Plaid credentials.

**Exit criteria:** a connected (sandbox) account's transactions land in
Postgres, unauthenticated requests are rejected, `docker compose up` is the
entire local setup.

## Phase 2 — Categorization, recurring detection, anomaly detection

Rule-seeded categorization classifier with a confidence score and manual
override, recurring-subscription detector (handles irregular intervals, not
just exact-30-day repeats), spending anomaly detector. Run as Celery jobs
against Redis.

**Exit criteria:** categorization precision/recall measured against a
held-out labeled set (not eyeballed); recurring detection validated against
a synthetic dataset with known-recurring charges planted in it.

## Phase 3 — Forecasting, recommendations, simulator

Cash-flow time-series forecast, rule-based recommendation engine with
explanations tied to specific transaction/pattern evidence, budget scenario
simulator (compare 2–3 plans by outcome and survivability).

**Exit criteria:** the core loop in `PRD.md` works end to end against
synthetic data — goal in, ranked explained plans out.

## Phase 4 — LLM natural-language layer

Chat interface over the Phase 1–3 APIs via tool-calling (not a general
chatbot with app data stuffed into its prompt) — "I'm spending too much,
what should I change to save $10k this year" answered by actually calling
the recommendation engine and simulator, with the reasoning surfaced.

**Exit criteria:** the project's own motivating question, asked in chat,
produces a specific, correctly-computed, cited answer.

## Phase 5 — Frontend

Next.js dashboard (accounts, categorized transactions, recurring/anomaly
call-outs, forecast), scenario simulator UI, chat UI with streaming.

**Exit criteria:** every feature in `PRD.md` is reachable and usable from
the UI, not just the API.

## Phase 6 — PM Agent MVP

Now that the Copilot produces real telemetry: event logging (recommendation
shown/accepted/dismissed, feature usage), a synthetic support-ticket/feedback
generator modeling the personas in `PERSONAS.md`, and the agent pipeline
itself — research (pain-point extraction from tickets + telemetry) →
RICE/MoSCoW prioritization → PRD generation → architecture-change proposal.
Gets its own PRD at the start of this phase, once there's real data to
write it against.

**Exit criteria:** given the Copilot's actual (synthetic-user) telemetry,
the agent produces a PRD for a real next feature that a reviewer would
consider reasonable, with the reasoning traceable back to specific input
data — not a generic LLM-written PRD indistinguishable from one written with
no data at all.

## Phase 7 — Experimentation framework

A/B assignment, exposure logging, and metrics evaluation
(`METRICS.md` north star + guardrails) wired to real recommendation
strategies. The PM Agent's "experimentation" and "analytics" steps connect
to this real framework instead of describing one hypothetically.

**Exit criteria:** two recommendation strategies actually run against split
synthetic-user populations, and the agent produces a real analysis of which
one won and why, including a guardrail check.

## Phase 8 — Infra

CI (GitHub Actions: lint, type-check, test on every push), production Docker
images, AWS deploy (containerized — exact service TBD in Phase 0b), logging
and basic monitoring.

**Exit criteria:** a fresh clone can be deployed by following the README,
not by reconstructing undocumented steps.

## Phase 9 — Polish

Metrics writeup against real Phase 7 results, a retrospective (Momentum-
style `RETRO.md`), README rewritten for what the project actually became,
added to `yasir-portfolio`.

## Explicitly out of scope, indefinitely

- Real bank credentials / production Plaid access (compliance burden, not a
  fit for a portfolio project — see Non-goals in `PRD.md`).
- Households / shared accounts, investment/brokerage tracking, native
  mobile, multi-currency.
- A PM Agent that can modify `backend/`/`frontend/` itself rather than
  propose changes (see the read-only boundary in `ARCHITECTURE.md`).

These aren't "later" — they're either a different product or a boundary the
project is intentionally keeping.
