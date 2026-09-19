# Materiality and when Double-Entry Review is required

Double-Entry Review is most valuable where a curated proposition history materially
improves reviewability, provenance or risk control. It should not become mandatory
ceremony for every small edit merely because an agent made the change.

The host repository/project owns the final applicability policy. This skill provides a
default decision shape that can be tightened or broadened locally.

## Classifications

- **Routine** — ordinary review/verification is sufficient; DER is optional unless explicitly requested.
- **Material** — DER is required by the host policy.
- **Critical** — DER is required and the host should normally add stronger independent review/evidence gates.

Classification is about review risk and cognitive burden, not diff size alone.

## Default hard triggers

Treat a change as at least `material` when it does one or more of the following, unless
the host policy explicitly records a narrower exception:

- changes a public/API contract, persistent schema, event/protocol format or compatibility guarantee;
- changes architecture boundaries or dependency direction;
- introduces/removes a major abstraction, provider/runtime boundary or durable state owner;
- changes security, privacy, authentication, permissions or data-handling guarantees;
- changes concurrency, transaction, durability, recovery or state-machine semantics;
- changes the meaning, identity or retention of evidence/provenance used to justify correctness;
- changes release/integration/build machinery in a way that can alter delivered artefacts;
- makes a broad behavioural change whose correctness depends on coordinated modules;
- requires a durable/cross-cutting ADR under repository policy;
- intentionally accepts residual risk or a bounded mitigation instead of removing the underlying cause.

A hard trigger makes DER required under the default policy regardless of line count.

## Strong indicators

When no hard trigger applies, DER is normally recommended/default-to-required when two
or more of these indicators are present:

- multiple complete propositions are needed to explain the change clearly;
- implementation chronology was exploratory or contains useful discoveries/dead ends;
- several modules must change together to establish one obligation;
- a reviewer needs non-obvious domain/history context to understand the diff;
- correctness cannot be established by one obvious deterministic check;
- an agent or human exercised meaningful design judgement among plausible alternatives;
- temporary implementation states would be misleading as the final review narrative;
- feedback is likely to require a distinct revision round;
- commit-by-commit proposition review would materially reduce reviewer cognitive load;
- failure would have significant operational/maintenance consequences;
- the change is difficult to reverse safely.

This `two or more` rule is a host-policy heuristic, not a scientific score. Do not add
weights or numerical precision unless a host project has evidence that doing so helps.

## Routine examples

Ordinary review is normally enough for:

- typo or small documentation corrections;
- formatting-only changes;
- straightforward dependency updates with no behavioural/contract implications;
- isolated copy/styling changes;
- small deterministic bug fixes with one clear cause and one clear test;
- mechanical refactors fully constrained by deterministic tooling;
- generated-file refreshes with no design decision;
- straightforward missing tests that do not change production behaviour.

Any of these may become material when scope or semantics change.

## Reassess on scope growth

Materiality is not a one-time label. Reassess when implementation discovers a new
contract, state transition, migration, architecture boundary, security/privacy effect,
or other scope expansion.

If a routine change becomes material:

1. preserve the true chronology already created;
2. record the new assessment and trigger(s);
3. establish the DER pair from the actual current provenance rather than inventing an earlier diary;
4. continue diary-first from that point.

Imported or pre-existing history remains imported provenance; never fabricate chronology.

## Agent authorship

Agent-generated does **not** automatically mean material. Treat meaningful agent design
judgement as an indicator. A mechanical, strongly verified agent edit can remain routine.

## Reviewer-value check

When classification remains ambiguous, ask:

> Would a competent reviewer materially benefit from seeing this change as an ordered
> series of complete propositions rather than one ordinary diff/history?

A clear `yes` is strong evidence for `material`.

## Materiality record

Record at least:

```yaml
classification: routine | material | critical
hard_triggers: []
indicators: []
rationale: ...
assessed_at: ...
reassess_on_scope_change: true
host_policy: ...
```

Use [the materiality template](../assets/materiality-assessment.md) when a durable record
is useful. The assessment does not grant Git/host authority and does not certify the
change as correct.
