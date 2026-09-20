# Prepare a human-reviewed grouping study

This guide separates preparing trustworthy inputs from judging the groups produced
by a method. The project's first grouping study is still a proposal. Its exact
sample, methods and decision criteria belong in
[EDR-0001](../edr/0001-discovery-grouping-method.md#concrete-proposal-for-owner-review).
The comparison runner and rating pack are not available yet.

## Agree the study before preparing inputs

1. Read the EDR's proposed workload, sampling procedure, rating rubric and decision rule.
2. The owner agrees or amends those choices. Record the agreement and any prior
   exposure to the source material; software PR approval alone does not supply it.
3. The agent prepares the source order, repository holdout list and exclusion log
   according to that procedure, before generating or judging interpretations.
4. Verify selected source identities and access terms. Keep unresolved sources out
   of the research sample with recorded reasons; retain the original imported data.
5. Freeze the normalisation configuration and choose a dedicated external data
   directory. Use it consistently for the web application and worker. Keep software
   test decisions separate from human research annotations.

The agent can build and test the comparison tooling with synthetic fixtures while
the owner reviews inputs. Synthetic tests cannot supply missing human judgements.

## Review each interpretation

Use the existing [normalisation workflow](normalisation.md) to produce the queued
interpretations and [annotation controls](annotations.md) to record your review.
Work through the prepared order; do not choose only promising-looking concerns.

![The existing Human assessment panel offers Accept, Edit and Reject, with optional notes and a structured editor.](../images/annotation-assessment.png)

These are the existing input-review controls, shown with
[synthetic demonstration data](../images/README.md). They are not the proposed
group-rating interface, and these example decisions do not enter the study.

| Step | What the human reviewer checks |
| --- | --- |
| Read the source | Read the supplied comment and code, with the verified original reference where available. Distinguish preprocessed text from the original. |
| Check meaning | Does the interpretation accurately describe the concern, rather than invent an unstated requirement? |
| Check evidence | Do the quoted excerpts support its claims? Is uncertainty or limited applicability retained? |
| Accept | Use when the existing interpretation is usable as written. This does not validate a future rule or detector. |
| Edit | Correct a usable interpretation while keeping it grounded in the supplied source. Save the edited structured result. |
| Reject | Use when the interpretation cannot serve the study. Record a short reason; rejection is not a verified negative example. |

Keep failures and skipped records in the preparation log. Follow the EDR's cap and
shortfall rule; do not quietly add more sources or rerun models for preferred answers.
If a saved annotation is mistaken, preserve it and record the correction explicitly
before freezing the selected version. The source-annotation UI cannot reopen it.

## Freeze and register

| Handoff | Agent prepares | Human contribution |
| --- | --- | --- |
| Input selection | Exact annotation IDs, verified result/edit hashes, source identities, duplicate/exposure/holdout exclusions and a fixed selection | Confirm which decisions were genuinely human-reviewed; give the curator name for the attestation |
| Reproduction | Tested runner, fixed methods/configuration, commands, environment, output identities and synthetic failure checks | Review consequential changes to the agreed method |
| Registration | Completed EDR plan commit, then a second commit recording that SHA, registration date and status | Agreement on the plan; no group ratings collected early |

Follow the [selection guide](selections.md#use-human-reviewed-data) and
[EDR registration process](../edr/README.md#follow-the-process). Registration requires
actual identities and working methods. A proposed filename or blank field is insufficient.

## Rate groups after registration

1. The agent runs the two registered configurations and prepares the method-masked pack.
2. Read all members in each presented group. Use the EDR rubric to record coherent,
   not coherent or uncertain, with a short reason.
3. Complete the selected ratings before seeing method identities or comparative scores.
   Record any suspected unmasking or missing information.
4. The agent freezes the ratings, reveals the mapping and reports counts, coverage,
   failures, costs where available and limitations.
5. The owner records adoption, no adoption or the next action for inconclusive evidence.
   Any implementation change and full slice closure are recorded separately.

Keep large or restricted inputs and raw outputs outside source control. Share a
small permitted summary, methods, hashes and access instructions. State reproduction
limits explicitly; one person's ratings are not independent agreement between raters.
