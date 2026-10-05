# Sprint 2 — Categorization, Recurring Detection, Anomaly Detection

**Sprint goal:** every transaction that lands through any of the three
Phase 1 ingestion paths gets a category and a confidence score automatically
(WIZ-7), a user can see and correct that confidence (WIZ-8) with the
correction remembered for that merchant going forward (WIZ-9), recurring
charges are surfaced without being asked — including irregular intervals,
not just exact 30-day repeats (WIZ-10) — and anomalous transactions are
flagged with the specific reason, not just "anomaly" (WIZ-11). No
forecasting, recommendations, or UI yet — this sprint only has to prove the
three detectors are each individually correct against known-answer data.

**Duration:** one sprint, same sizing caveat as `SPRINT_1.md`: write and
test the application code as a continuous build; keep that separate from
verifying any infra (Celery/Redis wiring, `docker compose up`) the way
`PHASE_1_RETRO.md` flagged should have happened last time — infra
verification trouble must not block shipping and testing the detector
logic itself.

## Scope (pulled from `BACKLOG.md`)

All P0 items in Epic 3 (Categorization) and Epic 4 (Recurring & Anomaly
Detection), plus the Epic 3 P1 item, in dependency order:

1. **Data model additions** — a `categories` table (a fixed taxonomy, not
   free text), plus `category_id` / `category_confidence` / `category_source`
   on `transactions` (nullable until a detector runs); a `merchant_category_rules`
   table scoped per-user for WIZ-9; a `recurring_series` table and a
   nullable `recurring_series_id` on `transactions` for WIZ-10; an
   `anomaly_flags` table (one row per transaction per reason) for WIZ-11.
   Nothing else this sprint can be built without this.
2. **Rule-seeded categorization (WIZ-7)** — a merchant-keyword rule table
   seeded via migration, matched against `merchant_name`/`name` on every
   transaction. Every transaction gets a category; unmatched transactions
   get an explicit low-confidence "Uncategorized" bucket rather than a null
   — "I never start from an uncategorized list" means the *category field*
   is never empty, not that everything is matched with high confidence.
3. **Confidence surfacing + manual override (WIZ-8)** — `category_confidence`
   on the transaction response (already-matched rule = high confidence,
   fallback bucket = low confidence); `PATCH /transactions/{id}/category`
   applies immediately and is a single call.
4. **Correction propagation (WIZ-9, P1)** — a correction via WIZ-8 writes a
   `merchant_category_rules` row scoped to that user and merchant; future
   transactions from the same merchant for that user match it before
   falling through to the global rule table. Pulled in alongside WIZ-8
   since it's the same code path (an override *is* a rule, just
   user-scoped) rather than a separate feature.
5. **Recurring detection (WIZ-10)** — groups transactions by
   (account, merchant), flags a group as a `recurring_series` when it
   repeats at a roughly-consistent interval within a tolerance window
   (handles "paid on the 1st, then the 3rd, then the 2nd" — not just exact
   30-day gaps) and a roughly-consistent amount. `GET /recurring` lists
   active series.
6. **Anomaly detection (WIZ-11)** — flags, with the specific reason
   attached: unusual amount for this merchant (statistical outlier against
   that merchant's own transaction history), an entirely unusual merchant
   for the account (first time seen, no history), and a duplicate-looking
   charge (same merchant + amount within a short window). `GET /anomalies`
   lists active flags.
7. **Celery wiring** — a `celery_worker` service in `docker-compose.yml`
   against the Redis already provisioned in Phase 1; categorize/detect-
   recurring/detect-anomaly dispatch as tasks after any ingestion (Plaid
   sync, demo seed, CSV upload) instead of inline in the request path, per
   `ARCHITECTURE.md`. Tasks run in Celery's eager mode in tests (direct
   function call, no broker needed) so the detector logic is testable
   without infra — the Phase 1 lesson about not blocking code on
   environment trouble applies here by design, not as an excuse found
   later.

## Definition of done

- Every transaction ingested through any of the three Phase 1 paths has a
  non-null `category_id` and `category_confidence` after its detector run
  — "Uncategorized" counts, `NULL` does not.
- Categorization precision/recall is measured against a held-out labeled
  set, not eyeballed (`ROADMAP.md` Phase 2 exit criteria) — a fixture of
  hand-labeled synthetic transactions distinct from the rule-seed data,
  with a test or script that reports both numbers.
- Correcting a transaction's category is a single API call, takes effect
  on that transaction immediately, and the next synthetic transaction from
  the same merchant for the same user is categorized by the correction
  without needing a second manual fix.
- Recurring detection is validated against a synthetic dataset with
  known-recurring charges planted in it (`ROADMAP.md` Phase 2 exit
  criteria), including at least one irregular-interval case and at least
  one true negative (a merchant charged twice by coincidence, not on a
  pattern) that must NOT be flagged.
- Anomaly detection has a planted-case test for each of the three named
  reasons — unusual amount, unusual merchant, duplicate-looking charge —
  plus a true-negative case (ordinary repeat spending at a familiar
  merchant) that must NOT be flagged.
- All detector logic is unit-tested without a running Redis/Celery broker
  (eager-mode or direct function calls), the same no-external-dependency
  bar Phase 1's test suite set for itself.

## Out of sprint

Everything in Epic 5 (`ROADMAP.md` Phase 3) onward in `BACKLOG.md` —
forecasting, recommendations, the simulator — and all P2 items. A learned
(non-rule-based) categorization model is explicitly not in this sprint
either: `ARCHITECTURE.md` calls for evaluating the rule-seeded classifier's
precision/recall first and deciding only then whether a learned model is
worth it — that evaluation is this sprint's job, the decision is not.
Verifying `docker compose up` (including the new `celery_worker` service)
end-to-end stays a carried-over Phase 1 item per `PHASE_1_RETRO.md`, not
new Sprint 2 scope.
