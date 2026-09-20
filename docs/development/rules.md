# Inspect and challenge candidate rules

A rule candidate describes a concern that might become a reusable code check.
Its evidence is inspectable, but proposing or promoting it does not prove that
it generalises or deploy a detector.

## Propose a candidate

You need a successful [clustering run and discovery-enabled worker](discovery.md).

1. Open a group and choose **Queue rule synthesis for this group**.
2. Wait for the worker, then inspect the result. It may propose a rule or explain
   that the supplied examples are insufficient; both are legitimate outcomes.
3. Open the candidate in **Rule registry**. Read its statement, scope, applicability,
   violation definition and exclusions.
4. Follow evidence links back to the original observations and interpretations.
   The model sees the representative and up to five other included examples, not
   necessarily the whole group. Its trace identifies exactly what was supplied.

The synthesis trace retains the prompt, schema, model selection, usage, framework
observation and raw output. Invalid JSON or invented support is refused and retained
for inspection. A provider failure is reported separately from invalid model output.

## Challenge and decide

| Action | Effect and responsibility |
| --- | --- |
| Add evidence | Choose positive, counterexample, false-positive, false-negative or unresolved evidence from the same saved selection. |
| Mark evidence verified | Attest that classification for this exact rule version with your name and rationale. A source match alone does not establish validity. |
| Promote | Retain a reviewed research candidate. This does not validate, enforce or deploy it. |
| Reject | Record why the current candidate should not be retained. |
| Revise | Create a new definition version; keep the original and its decisions. |
| Stage several actions | Use the [review workspace](research-interaction.md) to save a draft and apply it explicitly. |

Repository holdouts remain excluded. Rejected interpretations can supply weak
(unverified) evidence; rejection does not establish a verified negative example.
A false positive is a reported violation judged incorrect; a false negative is a
missed violation. State why the classification applies to this rule.

When revising:

- Evidence classifications carry forward with parent links and **weak** status.
  Reassess verification against the changed definition.
- Counterexamples cannot be silently discarded. Each version has a 1,000-link limit;
  a revision exceeding it is refused without changing the current version.
- Changes made after you prepared a decision cause a conflict. Submitted values
  remain available for correction; identical decision retries return the original.
- Reopen an answered or deferred rule review before another decision.

## Inspect failures and usage

| Condition | Next action |
| --- | --- |
| Insufficient evidence | Inspect the explanation; a successful run may produce no candidate. |
| Context too large | Reduce selected material. Synthesis permits six examples and 12,000 characters; the model's actual token budget is checked too. |
| Invalid output or references | Inspect the retained raw output and supplied IDs; no candidate is accepted from invalid support. |
| Interrupted job | Check the registry and original trace before submitting again: a complete candidate may exist even if final job registration failed. |
| Unknown token count | Treat it as unavailable, not zero. Running telemetry refreshes every five seconds. |

Recovery never automatically repeats the call or selects a stronger model. Current
routing configuration is `config/routing/discovery-local.json`; older policy versions
remain available to interpret stored runs. Model controls stay outside rule logic.

## Command-line equivalents

Run from the repository root using the same data directory as the web application.
Copy a cluster run ID/group number from discovery, or a version ID from the rule page.

```text
uv run --locked python tools/run.py --data-root ../extras/runtime synthesise <cluster-run-id> <group-number>
uv run --locked python tools/run.py --data-root ../extras/runtime discovery <run-id>
uv run --locked python tools/run.py --data-root ../extras/runtime rules
uv run --locked python tools/run.py --data-root ../extras/runtime rule <version-id>
```

The first command queues work. The others inspect runs, the registry or a specific
version. Test selections and automated decisions remain test data; significant
method choices follow the [empirical decision process](../edr/README.md).
