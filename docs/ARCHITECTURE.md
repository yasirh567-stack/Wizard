# Wizard — Architecture

**Owner:** Yasir Hassan
**Status:** v1 draft — will be revised once Phase 1 locks the actual API
surface; treat this as intent, not as-built, until then.
**Last updated:** 2026-09-11

## System overview

One repo, three parts:

1. **`backend/`** — FastAPI. The Finance Copilot's API and business logic.
2. **`frontend/`** — Next.js. Dashboard, scenario simulator, chat.
3. **`agent/`** — the PM Agent (Phase 6+). Reads the Copilot's own telemetry
   and runs product management on it. Built after `backend/` exists and
   produces real telemetry — see `ROADMAP.md`.

Plus shared infra: PostgreSQL, Redis, Docker Compose for local dev, GitHub
Actions for CI, AWS for deploy.

## Diagram

```
 Next.js frontend (dashboard, simulator, chat)
        │  REST + SSE (chat streaming)
        ▼
 FastAPI backend
   /auth  /accounts  /transactions  /budgets
   /forecast  /recommendations  /chat
        │                                  │
        ▼                                  ▼
 PostgreSQL                             Redis
   users, accounts, txns,                 cache +
   categories, budgets,                   Celery broker/
   recommendations, events                result backend
        ▲
        │ read / write
 Celery workers
   categorize · detect-recurring · detect-anomaly
   recompute-forecast · generate-recommendations
        │
        ▼
 Plaid Sandbox  (transaction feed)


 PM Agent  (Phase 6+, reads — never writes app code)
   reads:    event log, recommendation outcomes,
             synthetic support tickets / feedback
   produces: research → RICE/MoSCoW → PRD → architecture
             proposal → A/B test design → analysis →
             next-build recommendation
```

## Key design decisions

- **Plaid Sandbox for ingestion, not a hand-rolled CSV parser.** A CSV
  upload path still exists (fastest way to demo without setup), but the
  primary path is a real fintech API integration — sandbox mode is free,
  requires no compliance review, and produces realistically-shaped data
  (multiple institutions, pending vs. posted transactions, varied merchant
  name formatting) that a synthetic generator alone tends not to replicate.

- **Async by default for anything derived.** Categorization,
  recurring-detection, anomaly-detection, and forecast recompute all run as
  Celery jobs against Redis, not inline in the request path. A transaction
  sync shouldn't block on a forecast recompute, and re-running a detector
  against updated data shouldn't require re-ingesting anything.

- **The recommendation engine never auto-executes.** It proposes; the user
  decides. No bill negotiation, no autonomous transfers or cancellations.
  This is a trust boundary (see Non-goals in `PRD.md`), not a v1 gap to
  close later.

- **The PM Agent is read-only against the Copilot.** It reads the event log
  and outcome data through the same API surface anything else would use; it
  proposes PRDs and architecture changes, it does not open pull requests or
  modify `backend/`/`frontend/` itself. Keeping that boundary explicit
  matters for the project's own credibility — an agent that quietly patches
  the app it's supposed to be *evaluating* would make its own analysis
  unfalsifiable.

- **One repo, three subsystems, not three repos.** The PM Agent's entire
  reason to exist is the Copilot's real data shape; splitting them into
  separate repos would turn a coupled system into two projects that happen
  to reference each other, which is a worse portfolio story, not a better
  one.

## Why not X

- **Why not extend Momentum's stack (Next.js API routes + Prisma) instead
  of a separate FastAPI backend?** Categorization, forecasting, and the
  recommendation engine are genuinely Python's ecosystem (scikit-learn /
  statsmodels, not a JS equivalent); Celery needs a real backend process
  model Next.js API routes don't provide. It's also a deliberate stack
  choice — the portfolio has a Next.js-monolith example already.

- **Why Postgres over SQLite (Marginalia's choice)?** Marginalia is
  single-process, local-first, and its persistence need (an incremental-
  indexing manifest) fits SQLite well. Wizard has concurrent Celery
  workers writing derived data and relational integrity requirements across
  accounts/transactions/budgets/recommendations that call for a real RDBMS —
  and it's a stack gap none of the other three repos currently cover.

- **Why Redis for both cache and broker, instead of a dedicated queue
  (SQS, RabbitMQ)?** One moving part in local dev and in the initial deploy;
  Celery's Redis support is first-class. Revisit if a real throughput
  reason shows up — none is expected at this project's scale.

## Deferred to Phase 1

Exact Postgres schema, the categorization model's specific approach
(starting point: a rule-seeded classifier with a small labeled set,
evaluated before deciding whether it needs to be a learned model at all),
and the precise FastAPI route list. Locking these before any code exists
would be guessing; `PRD.md`'s feature list is the real constraint, the
schema follows from it.
