# Phase 1 Retro — Backend Skeleton

**Written:** 2026-10-04, before Phase 2 starts, per the Definition of Done
in `SPRINT_1.md`.

## What shipped

All P0/P1 scope from `SPRINT_1.md`: Postgres data model (users, plaid_items,
accounts, transactions), JWT auth with argon2 hashing (WIZ-1), Plaid Sandbox
connect + `/transactions/sync`-based ingestion (WIZ-2), dedup and
pending→posted correctness (WIZ-5, WIZ-6), a demo-data seed (WIZ-3), and CSV
upload (WIZ-4). 15 tests, all passing. ~1,650 lines of backend code across
three commits.

## What went well

- **Building WIZ-5/WIZ-6 alongside the first sync, not after, was the right
  call.** The plan in `SPRINT_1.md` explicitly called this out in advance,
  and it paid off: the pending→posted test caught a real bug (a missing
  `db.flush()` between processing Plaid's `added` and `removed` entries let
  a posted transaction's relink get immediately clobbered by the stale
  `removed` lookup) before any real data ever hit the table. Writing the
  test first, against a fake Plaid client, is what surfaced it — it would
  have been a silent, hard-to-notice duplicate/data-loss bug against real
  sandbox data otherwise, exactly the failure mode the sprint doc flagged
  as the thing to guard against.
- **The cross-dialect `GUID` type (`app/db/types.py`) was worth the up-front
  cost.** Postgres is the right call for production (`ARCHITECTURE.md`
  already covers why), but tooling friction on this dev machine (see below)
  made a zero-dependency test path valuable enough to build deliberately
  rather than skip. It cost about 30 minutes to write and swap into the four
  models; it bought a 15-test suite that runs in under 3 seconds with no
  external service, on top of the Postgres path still being real for
  `docker compose up`.
- **WIZ-3 and WIZ-4 reusing the same `content_hash` dedup mechanism** that
  the schema had already reserved a column for (rather than inventing a
  second dedup strategy per ingestion path) kept the three ingestion paths
  consistent instead of three different correctness stories.

## What didn't go well

- **`docker compose up` — the sprint's own headline Definition-of-Done
  line — was never actually verified end-to-end in this environment.** This
  dev machine runs macOS 12 (Monterey), which Homebrew stopped shipping
  bottles for; Colima's only available VM backend here (QEMU) has to compile
  from source along with its full dependency chain (OpenSSL, ICU, Kerberos,
  Python itself as a build dependency). Multiple attempts across several
  days never finished — not because the compose file is wrong (`docker
  compose config` validates it cleanly, including env var resolution), but
  because the build environment itself couldn't produce a working Docker
  daemon in any attempt made. This is a real gap: the actual DoD line is
  unverified, not just inconvened around.
- **Time spent chasing the Docker/Colima/QEMU build was large relative to
  the value delivered.** Multiple sessions went into this before switching
  to the SQLite fallback for tests; the fallback should have been the first
  move once the first `qemu-img not found` error showed a from-source build
  was implied, not the last.
- **No real Plaid Sandbox credentials were ever exercised against this
  code.** `PLAID_CLIENT_ID`/`PLAID_SECRET` are blank in the local `.env`;
  the Plaid-path tests use a fake client that mimics the SDK's response
  shape from reading its source, not a verified-correct one. The request
  construction bug (passing `cursor=None` to `TransactionsSyncRequest`,
  which the SDK's generated model rejects) was caught this way — by
  actually trying to build the request object in a test, not by reasoning
  about the SDK's type stubs — which is a point in favor of the fake-client
  approach, but it only proves the code is *internally* consistent with the
  SDK, not that a real sandbox institution's response shape matches what
  the fake client was built to mimic.

## Estimate vs. actual

`SPRINT_1.md` sized this as "a single continuous build session." It instead
spanned five real-world dates (Sep 17 → Oct 4) — almost entirely due to the
Docker/Colima build time above, not the application code itself, which was
written, tested, and committed in two focused sessions (data model + auth +
Plaid sync; then demo seed + CSV upload). The lesson for `SPRINT_2.md`
sizing: separate "time to write and test the code" from "time to verify the
deployment story," and don't let the second block the first when they hit
unrelated environment trouble.

## Carried into Phase 2

- Verify `docker compose up` on an environment that isn't blocked on a
  from-source QEMU build (a newer macOS, Linux, or CI) before trusting it
  unconditionally.
- Exercise the Plaid routes against a real Sandbox institution at least
  once, rather than relying solely on the fake-client tests.
- The `content_hash`/dedup pattern and the `GUID` type are both reusable as
  Phase 2 adds categorization data — no rework anticipated there.
