# Sprint 1 — Backend Skeleton

**Sprint goal:** a fresh clone can `docker compose up`, register a user,
connect a Plaid Sandbox account (or load demo data, or upload a CSV), and
get back synced, deduplicated transactions through the API. No
categorization, forecasting, or UI yet — this sprint only has to prove
data gets in correctly and sits behind real auth.

**Duration:** one sprint, sized as a single continuous build session rather
than calendar time — see the Phase 1 retro (written after) for how the
estimate actually held up, same practice as Momentum's `RETRO.md`.

## Scope (pulled from BACKLOG.md)

All P0 items in Epic 1 (Auth & Account Connection) and Epic 2 (Transaction
Sync Correctness), plus the Epic 1 P1 items that have no dependencies and
are cheap enough to fold in now, in dependency order:

1. **Data model** — Postgres schema for users, accounts, and transactions,
   plus whatever sync/dedup metadata WIZ-5/WIZ-6 need. Nothing else this
   sprint can be built without it.
2. **Auth** (WIZ-1) — required before any account/transaction endpoint can
   be scoped to a user.
3. **Plaid Sandbox connect + initial sync** (WIZ-2) — the primary ingestion
   path.
4. **Sync correctness** (WIZ-5, WIZ-6) — dedup and pending→posted handling,
   built alongside the first Plaid sync rather than retrofitted after —
   fixing dedup against data that's already wrong is worse than getting it
   right on the first sync.
5. **Demo-data seed** (WIZ-3) and **CSV upload** (WIZ-4) — independent of
   Plaid, buildable in either order. Pulled in now (even WIZ-4 at P1)
   because both are cheap and this project needs to be reviewable by
   someone with zero Plaid sandbox credentials configured.

**Explicitly left for a later sprint:** everything from Epic 3
(categorization) onward — Phase 2 per `ROADMAP.md`. Categorizing data whose
ingestion/dedup behavior isn't proven yet just means re-testing it once
ingestion inevitably changes shape.

## Definition of done

- `docker compose up` is the entire local setup — API, Postgres, and Redis
  all come up from one command; no undocumented manual steps.
- A fresh user can register and log in; every account/transaction endpoint
  returns 401 without a valid token.
- All three ingestion paths — Plaid Sandbox, demo-data seed, CSV upload —
  land transactions that are queryable through the API.
- Re-running a Plaid sync against unchanged data is provably a no-op (a
  test asserts row count doesn't move), and a transaction observed to go
  pending→posted is provably updated in place, not duplicated.
- Real tests exist specifically for the dedup key logic — the easiest place
  in this sprint for a silent, hard-to-notice bug (a transaction quietly
  duplicating) to hide.
- A phase retro is written afterward, honestly, before Phase 2 starts.

## Out of sprint

Everything in Epic 3 onward in `BACKLOG.md`, and all P2 items. See
`ROADMAP.md` Phase 2+.
