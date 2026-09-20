# Inspect and challenge candidate rules

Open a successful clustering run and **Queue rule synthesis for this group**.
The discovery-enabled worker uses the generation endpoint as well as the embedding
configuration described in [discovery operations](discovery.md). The request pins
the cluster result and frozen selection. It sends the representative followed by
up to five other eligible interpretations, in frozen order, retaining uncertainty.
The exact supplied IDs are in the trace; selection totals are not the number sent.

Inspect the resulting candidate in **Rule registry**. Its statement, scope,
applicability, violation and exclusions are a proposal. Evidence links open the
original observations and interpretations; the synthesis trace retains prompt,
schema, route, usage, framework observation and raw output. Insufficient evidence
is a useful successful result with no invented candidate. Invalid JSON or invented
support fails visibly and preserves raw output. Provider failure is distinct.

## Evidence and research decisions

Attach positive, counterexample, false-positive, false-negative or unresolved
evidence from the same frozen selection. Repository holdouts remain excluded.
Rejected interpretations may be weak evidence; they are not verified negatives.
Choose verified only when explicitly attesting that claim for this rule version,
with your name and rationale. A source match establishes provenance, not validity.

Promote or reject a current candidate with a rationale. Promotion means a reviewed
research candidate; it does not validate, enforce or deploy the rule. Concurrent
changes produce a conflict and preserve submitted values for correction. Decision
retries with the same identity and content return the original decision.

Revise to create an immutable child version. Prior decisions remain historical.
Every evidence classification carries forward with a parent link and weak status;
verification must be reassessed against the new definition. A revision cannot
silently discard counterexamples. Each version is bounded at 1,000 links, and a
revision exceeding that limit fails without changing the current version.

## Failures, provenance and limits

The workflow bounds context to six examples and 12,000 characters; the concrete
adapter also checks real template/token budgets before inference. No truncation
or automatic stronger-model fallback occurs. Routing policy version 2 introduces
the synthesis task while retaining version 1 for historical resolution. Model
names and deployment controls remain outside the domain and task prompt.

The detail page refreshes running telemetry every five seconds. Unknown counts
remain unknown; local spend excludes hardware/electricity accounting. Completed
usage retains inventory/policy versions and provider measurements where exposed.

Files, rule registration and job finalisation are deliberately separate steps.
An interruption may leave an orphan complete file or a complete candidate whose
job reports interrupted/unknown completion. Inspect the registry and original
trace before explicitly submitting again. Recovery never automatically repeats
the call. Historical rule bodies and claims remain unchanged.

Equivalent commands use the same operational services:

```text
python tools/run.py --data-root <external-runtime> synthesise <cluster-run-id> <group-number>
python tools/run.py --data-root <external-runtime> discovery <run-id>
python tools/run.py --data-root <external-runtime> rules
python tools/run.py --data-root <external-runtime> rule <version-sha256>
```

Immediate research decisions and the [staged review workspace](research-interaction.md)
share the same decision contract. Fixture selections
and automated decisions remain labelled software tests, never human study labels.
EDR-0001 remains draft; no comparative method adoption is implied.

## Compatibility observations

On 20 September 2026, the pinned Nomic/llama.cpp embedding fixture and Qwen3-4B
generation fixture completed selection, real MAF embedding, clustering, real MAF
synthesis and candidate publication on isolated synthetic interpretations. The
trace retained exact supplied references, policy version 2, framework version and
known input/output tokens. External DER `vs2-rules/r1` retains methods and results.

Earlier live runs returned valid insufficiency results. Inspection exposed an
ambiguous task instruction forbidding generalisation while requesting a prospective
rule. Prompt version `rule-synthesis-v2` distinguishes a provisional shared invariant
from demonstrated generalisability and makes clear that novelty is not required.
Both earlier outputs are retained; this is a functional contract clarification,
not a comparative quality assessment or a claim that the new prompt is better.
