# Wizard — Problem

**Owner:** Yasir Hassan
**Status:** v1
**Last updated:** 2026-09-11

## The problem

Every mainstream personal-finance app is good at one thing: telling you what
already happened. You spent $340 on restaurants last month, up 12% from the
month before. That's a chart, not a decision.

Take the question this project is named after: *"I'm spending too much. What
should I change if I want to save $10k this year?"* The user already knows
**that** they're overspending — a pie chart confirms it without answering the
actual question. Answering it for real requires:

1. **Knowing what's discretionary vs. fixed.** A $60/month gym membership and
   a $60/month loan payment look identical in a category chart. They are not
   the same decision.
2. **Knowing what's recurring but invisible** — subscriptions and small
   creeping charges nobody re-evaluates after the first month.
3. **Forecasting forward, not just reporting backward.** "$10k by December"
   is a specific dollars-per-month number that depends on income timing and
   existing obligations, not a vague direction to "spend less."
4. **Simulating trade-offs.** Cancel two unused subscriptions and cut dining
   out 20% → hits the goal and is survivable. Cut dining out 60% → also hits
   the number and isn't. The user needs to see and choose between plans, not
   receive one generic tip.
5. **Explaining why.** A recommendation with no reasoning is a suggestion to
   ignore. "You've paid for this app 14 times and opened it twice" changes
   behavior in a way "reduce Entertainment spending" does not.

No mainstream app does all five. Most do (1) shallowly and stop there. The
gap between *reporting* and *a specific, explained, achievable plan* is what
Wizard is built to close.

## Why this is hard, not just unbuilt

Translating "save $10k" into a concrete plan needs the same pieces no matter
who builds it: transaction-level categorization good enough to trust,
recurring-charge detection that doesn't miss irregular-interval subscriptions,
a forecast that's honest about its own error, and a recommendation layer that
can simulate several plans and rank them by how survivable they are — not
just by dollar amount. Each piece is individually well-understood
(classification, time-series forecasting, rule-based + learned
recommendation); the hard part is composing them so the user gets one page
that says "do this," instead of five dashboards that say "here's data."

## The second problem this project takes on

A finance app is also a product, and most portfolio "case studies" for a
product are a PDF someone wrote after the fact, disconnected from anything
the software actually did. Wizard's second half — the PM Agent — is an
attempt to make the case study real: it reads the Copilot's own usage
telemetry, synthetic support tickets, and experiment results, and produces
the research → prioritization → PRD → architecture proposal → experiment →
analysis → iteration cycle from that data, not from someone narrating it
after the fact. See `docs/ROADMAP.md` for when that gets built (it needs the
Copilot to exist first — you can't analyze telemetry that doesn't exist yet).

## Who this is for right now

This ships without a real user base. See `USER_RESEARCH.md` for how research
was done without one, and `PERSONAS.md` for who it's built for.
