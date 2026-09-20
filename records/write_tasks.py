from pathlib import Path
R=Path('WORKSPACE/extras/der-checkouts/vs2-interaction')
def write(name,text):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n',encoding='utf-8',newline='\n')
write('README.md',r'''
# Meerkritic

**Code review grounded in engineering evidence.**

Meerkritic explores how recurring concerns in code reviews, issue discussions and
source code can become reusable checks. It is an experimental project for
developers and researchers who want to understand why a finding matters and
whether a proposed change improves the code.

Its design centres on three ideas:

- **Traceable evidence.** Connect observations, rules and findings to the material
  that supports them.
- **Inspectable checks.** Express concerns as explicit rules, using deterministic
  tools where sufficient and model-assisted analysis where needed.
- **Human judgement.** Make interpretations available for review and correction,
  and evaluate proposed fixes against the code and its tests.

## Browse the sample

You need **Python 3.12** and **uv**. Run commands from the repository root.
The browser is a local web application, called the *harness* in some project records.

1. Install the locked dependencies:

   ```text
   uv sync --locked
   ```

2. Download and register the public review-comment sample:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime register crc-py-manual-4176ac0
   ```

   This downloads about 2.5 MB, checks its checksum and registers 1,030 records.
   Keep the data directory outside the repository and use the same path throughout.

3. Start the web application:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime serve
   ```

4. Open [localhost:8000](http://127.0.0.1:8000) and choose the dataset to browse
   comments alongside their code. The server accepts connections on this computer only.

## What would you like to do?

| Task | Guide |
| --- | --- |
| Turn a comment and its code into a structured interpretation | [Run normalisation](docs/development/normalisation.md) |
| Accept, correct or reject a model interpretation | [Review annotations](docs/development/annotations.md) |
| Save fixed inputs for discovery | [Select annotations](docs/development/selections.md) |
| Group similar concerns | [Run discovery](docs/development/discovery.md) |
| Propose and challenge a reusable check | [Review candidate rules](docs/development/rules.md) |
| Save several decisions or ask the model for advice | [Use the review workspace](docs/development/research-interaction.md) |
| Inspect changes to the code's architecture | [Publish and read architecture views](docs/architecture/README.md) |

Model work needs a separate local model server and worker; browsing does not.
Agent advice never applies rule edits or human decisions automatically.
See the [documentation index](docs/README.md) for setup, operations and developer references.

## Contributing

- Use [GitHub issues](https://github.com/FinnNk/Meerkritic/issues) to ask questions,
  report problems or suggest improvements.
- Read the [project instructions](AGENTS.md) and [development guide](docs/development/README.md).
- Work on a branch, use Conventional Commits and run
  `uv run --locked python tools/check.py` before submitting changes for review.

## Licence

Meerkritic is licensed under the [MIT licence](LICENSE.md), copyright 2026 Finn Newick.
Imported material and third-party skills retain their own notices; see
[source attribution](docs/sources.md).
''')
write('docs/README.md',r'''
# Documentation

Start with [browsing the sample](../README.md#browse-the-sample). These guides describe
how to use the code in this checkout. The [glossary](../CONTEXT.md) explains project terms.

## Use the application

| Goal | Read |
| --- | --- |
| Understand the public sample and recover dataset files | [Datasets](development/datasets.md) |
| Start a local model server | [Local inference setup](development/local-inference.md) |
| Ask a model to interpret a review comment | [Normalisation](development/normalisation.md) |
| Review and correct interpretations | [Annotations](development/annotations.md) |
| Choose a fixed set of reviewed inputs | [Selections](development/selections.md) |
| Group concerns and inspect their sources | [Discovery](development/discovery.md) |
| Propose, challenge and revise rules | [Candidate rules](development/rules.md) |
| Save decisions or send selected discussion for advice | [Research interaction](development/research-interaction.md) |

## Operate and inspect

| Goal | Read |
| --- | --- |
| Inspect model selection or export usage | [Routing commands](development/routing-operations.md) |
| Inspect logs, stored outputs and change-review references | [Operational evidence](development/operational-evidence.md) |
| Compare architecture and recognise stale views | [Architecture evidence](architecture/README.md) |
| Check an installation from input to reviewed result | [Workflow verification](development/verification.md) |

## Develop and review

- [Development workflow](development/README.md), [repository boundaries](development/structure.md)
  and [test guide](../tests/README.md).
- [Writing documentation](development/documentation-style.md),
  [Python style](development/python-style.md) and [code comments](development/code-comments.md).
- [Routing reference](development/routing.md) and
  [interpretation contract](development/normalisation-contract.md).
- [Milestone review method](development/milestone-review.md).

## Decisions, plans and history

These records serve different purposes from current operating instructions:

- [Architecture decisions](adr/README.md) explain consequential design choices.
- [Empirical decisions](edr/README.md) retain hypotheses, methods, results and choices.
- [Implementation backlog](../IMPLEMENTATION_BACKLOG.yaml) and [slice reviews](slice-reviews/README.md)
  describe delivery status and evidence.
- [Original research](research/README.md) and [source attribution](sources.md)
  preserve the supplied material and its provenance.
''')
# The verification guide is added in the later reference backfill; avoid an early broken link.
p=R/'docs/README.md';p.write_text(p.read_text().replace('(development/verification.md)','(development/vs1-verification.md)'),encoding='utf-8',newline='\n')
write('docs/development/annotations.md',r'''
# Review model interpretations

An *annotation* is your Accept, Edit or Reject decision on one successful model
interpretation. Each model run has its own decision; reviewing several runs for
one source still counts as reviewing one original observation.

## Review a result

First [run normalisation](normalisation.md) and open a successful job.

1. Read the original comment, code, proposed interpretation and quoted evidence.
2. Choose an action:

   | Action | What is saved |
   | --- | --- |
   | **Accept** | Your acceptance of the model's original interpretation |
   | **Edit** | A complete corrected interpretation, alongside the original |
   | **Reject** | Your rejection; the source counts as reviewed, not accepted |

3. For **Edit**, expand the structured interpretation and edit its JSON fields.
   The same schema and source-quote checks apply as for model output. Invalid
   drafts stay visible for correction.
4. Submit the decision. It is saved immediately; there is no draft/apply stage for
   source annotations. The page shows your decision separately from the model result.
5. Open **Annotation progress and review queue** to find the next unreviewed result.

An identical retry returns the saved decision. A different decision for the same
result is refused. Source annotations cannot currently be reopened; the
[review workspace](research-interaction.md) reopens **rule reviews**, not annotations.
The JSON editor is the current editing interface.

## Read progress and history

| Display | Meaning |
| --- | --- |
| Successful results | Model runs available for human review |
| Reviewed results | Results with an Accept, Edit or Reject decision |
| Source coverage | Distinct original observations reviewed, regardless of repeat runs |
| Source history | The latest 100 decisions for that source across model runs |

Pending pages can shift as decisions are saved. Return to the first page to refresh
that queue. Progress counts come from one consistent database snapshot.

## Use the command line

Run from the repository root after `uv sync --locked`, using the same external
data directory as the web application. Copy the job ID from its page or the `jobs` command.

```text
uv run --locked python tools/run.py --data-root ../extras/runtime annotate <job-id> accept
uv run --locked python tools/run.py --data-root ../extras/runtime annotate <job-id> reject
uv run --locked python tools/run.py --data-root ../extras/runtime annotate <job-id> edit --edited-json <file> --notes "Reason for the correction"
uv run --locked python tools/run.py --data-root ../extras/runtime progress <dataset-id>
```

Choose one annotation command per result. For an edit, `<file>` must contain the
complete interpretation, not just changed fields. The command prints the saved
annotation; `progress` reports result counts and distinct-source coverage.

## Retention and recovery

- The original result and its evidence are never overwritten. Edited JSON bodies
  are immutable files; SQLite stores their references, decision metadata and events.
- A decision and its event are saved together. An interrupted file write cannot
  publish a partial decision, although a complete unreferenced file may remain.
- Preserve unexpected files for diagnosis. See [operational evidence](operational-evidence.md).
- The application is for one local reviewer. A recorded name or decision is not
  authenticated proof of who performed the review. Automated test decisions must
  remain labelled test data; see [research selections](selections.md#use-human-reviewed-data).
''')
write('docs/development/normalisation.md',r'''
# Interpret a review comment with a local model

Normalisation turns a comment and its code excerpt into a structured interpretation:
what concern was raised, which evidence supports it and whether it might apply elsewhere.
You review the result; a successful model call does not establish that it is correct.

## Before you start

- Install Python 3.12 and run `uv sync --locked` from the repository root.
- [Register a dataset and start the web application](../../README.md#browse-the-sample).
- [Start the local generation server](local-inference.md) on port 8081.
- Use the same external data directory for the web application and worker.

## Submit and review a job

1. Start the worker in a separate terminal:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime worker --routing config/routing/llama-local.json
   ```

   Keep this terminal running. Use the [discovery worker](discovery.md#start-the-worker)
   instead if you also need grouping and rule synthesis; run only one worker per data directory.

2. In the web application, open a dataset and choose **Normalise** beside a record.
3. Open the resulting job page. It refreshes every three seconds while queued or running.
4. Read the interpretation, quoted evidence and available model usage. Unknown token
   counts display as `?`; local spend describes API spend, not hardware costs.
5. [Accept, edit or reject](annotations.md) a successful interpretation.
   **Normalisation jobs** lists recent and failed jobs.

Refreshing a result page does not submit another job. Pressing **Normalise** again
creates a separate model run.

## Process one job from the command line

Stop the continuous worker first. These commands queue the first source record,
process at most one available job and list job results:

```text
uv run --locked python tools/run.py --data-root ../extras/runtime normalise crc-py-manual-4176ac0 0
uv run --locked python tools/run.py --data-root ../extras/runtime worker --routing config/routing/llama-local.json --once
uv run --locked python tools/run.py --data-root ../extras/runtime jobs
```

Source indexes start at zero. If other work is already queued, `--once` may process
that work first; inspect the returned job ID rather than assuming which job ran.

## Diagnose a problem

| Symptom | Meaning and next action |
| --- | --- |
| Job stays queued | Check that a worker uses the same data directory and a compatible routing file. |
| Another worker owns the directory | Use the existing worker, or stop it before starting another. Do not remove its lock to force recovery. |
| Provider or context failure | Inspect the job error, server and context limits. Fix the cause before a new explicit submission. |
| Worker interrupted | Restart only after the old process has stopped. Previously running jobs become failed; calls are not automatically repeated. |
| Worker is still alive but appears hung | Inspect and stop that process before recovery. An overdue heartbeat alone does not authorise a second worker. |
| Result is missing or has changed | Preserve the evidence and restore verified bytes from backup; do not edit a checksummed result in place. |

A provider may have completed a call before the worker stopped. Inspect its route,
usage and stored output before submitting again. Use a local disk; network shares
are not a verified runtime environment.

## Storage and developer detail

- Results are complete JSON files under `results/<sha256>.json`. SQLite stores job
  metadata and references, and records each state change with its event.
- A failed database write can leave an unreferenced result file. Keep it for inspection.
- Checksums are verified when results are read. A successful job must have a result
  and no error; a failed job must have an explanation.
- [Operational evidence](operational-evidence.md) covers logs and indexing;
  [routing commands](routing-operations.md) cover usage export.
- [The interpretation contract](normalisation-contract.md) describes schema,
  evidence validation and Microsoft Agent Framework boundaries.

The supplied model configuration is a tested compatibility example, not an empirical
model recommendation. The adapter permits local loopback inference only; the web
application expects same-origin submissions on a trusted single-user computer.
''')
write('docs/development/selections.md',r'''
# Save fixed inputs for discovery

A *selection* is a saved copy of explicitly chosen annotations and their source
material. It records which interpretation to use and which records to exclude.
Later annotations cannot change an existing selection.

## Create a selection

You need reviewed results from the [annotation workflow](annotations.md). No model
server or worker is needed for these commands.

1. Open each reviewed job and copy its annotation ID. Choose one annotation version
   per source record, all from the same dataset.
2. Save a request outside the repository, for example `../extras/selection-request.json`:

   ```json
   {
     "dataset_id": "crc-py-manual-4176ac0",
     "annotation_ids": ["replace-with-an-actual-annotation-id"],
     "purpose": "fixture",
     "holdout_repositories": []
   }
   ```

   `fixture` means software-test data. Use it while trying the workflow; do not
   describe these inputs as a human-labelled research sample.
3. From the repository root, register the selection using the annotation data directory:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime freeze-selection ../extras/selection-request.json
   ```

4. Copy the returned selection ID. The response also gives included/excluded totals
   and the first registration time. Inspect the complete saved content with:

   ```text
   uv run --locked python tools/run.py --data-root ../extras/runtime selection <selection-id>
   ```

5. Open **Frozen annotation inputs** in the web application and select that ID.
   It checks the stored content and displays ten records per page. The catalogue
   itself lists metadata; opening a selection verifies its body.

## Understand inclusion and exclusion

| Input | Treatment |
| --- | --- |
| Accepted annotation | Include the original model interpretation. |
| Edited annotation | Include the verified edit and retain the original result hash. |
| Rejected annotation | Exclude the interpretation. Rejection does not prove the source is a valid negative example. |
| Repository listed as a holdout | Exclude it even if accepted; repository matching ignores case. |
| Rejected and held out | Show the holdout exclusion and retain the Reject decision. |

A *holdout* is material reserved from the current discovery work for later evaluation.
The request declares holdouts; the application does not discover them for you.
Selecting a holdout still reads and retains its source, so record that exposure.
An all-excluded selection can be saved but cannot supply discovery inputs.

## Use human-reviewed data

For a research selection, set these fields in addition to the dataset and annotation IDs:

```json
{
  "purpose": "research",
  "curator": "Name of the person confirming review",
  "human_review_attested": true
}
```

- This records the curator's claim that the included decisions were human-reviewed.
  The application does not authenticate that claim.
- Do not attest automated test decisions. Fixture selections cannot carry this attestation.
- Before a decision-bearing comparison, register its sample, splits, methods and
  contamination controls using the [EDR process](../edr/README.md).

## Limits and recovery

| Condition | Behaviour or action |
| --- | --- |
| Request exceeds 256 KB, 100 distinct annotations or one dataset | Reduce or correct the request. |
| Saved snapshot exceeds 32 MB | Reduce the explicit selection; nothing is silently truncated. |
| Same request is retried | Return the first identity/time without a duplicate event. Input order and curator details are part of identity. |
| Request content changes | Create a different selection; existing content is not replaced. |
| Source evidence is missing or corrupt | Freezing fails. Restore verified evidence before retrying. |
| Saved snapshot is missing or corrupt | Inspection/retry fails; restore trusted bytes rather than editing it in place. |

Bodies live at `<data-root>/selections/<sha256>.json`; SQLite contains small metadata
and events. Files are published before the metadata transaction, so interruption
may leave a complete unreferenced file. Retry registration rather than overwriting it.

Keep original source, result and edit files for full reproduction. A selection can
still show its copied content if originals are offline; that does not establish
that every original artefact remains available. See
[ADR-0009: Freeze explicit annotation selections before discovery](../adr/ADR-0009-freeze-explicit-annotation-selections.md)
for the implemented retention decision.
''')
write('docs/development/research-interaction.md',r'''
# Save rule decisions and ask for advice

Use **Review workspace** to save several rule decisions before applying them.
Use **Guidance** to send selected discussion to a model for advice. Saving a draft,
posting a message and requesting advice are separate actions.

## Save and apply a draft

Start with candidates in the [rule registry](rules.md).

1. Open **Review workspace**, or a rule's **Stage decisions, defer or reopen** link.
2. Choose actions and rationales for up to twenty rule versions, and enter your name.
3. Choose **Save draft only**. The draft survives restart; rule decisions have not changed.
4. Open the saved draft and inspect its target versions and actions.
5. Choose **Apply this saved batch**. All its decisions and events are saved together.

If any rule or its evidence changed after you prepared the draft, **none of the
batch is applied**. The page identifies the conflicting version and preserves the
draft. Inspect that rule before correcting the target revision or action and saving
again. An applied draft cannot be edited; start a new one. Repeating an identical
Apply request returns the original receipt.

## Choose the next review action

| Current review state | Meaning | Available next action |
| --- | --- | --- |
| Pending | A new rule version awaits review. | Promote, reject or defer |
| Answered | A promote/reject decision has been recorded. | Reopen before another decision |
| Deferred | Review has been set aside. | Reopen when ready |
| Reopened | Review is active again; earlier answers remain recorded. | Promote, reject or defer |
| Superseded | A newer rule definition replaces this version. | Follow the replacement link to review it |

Reopening returns the rule to candidate status and preserves earlier answers.
Revising the definition creates a new pending task and marks the old one superseded.
Evidence added after a decision is shown as newer than that decision.

Immediate promote/reject on a rule page follows the same rules as batch application.
Promotion retains a research candidate; it does not deploy or validate a detector.
These controls apply to rules. [Source annotations](annotations.md) still save
Accept/Edit/Reject immediately and cannot be reopened.

## Add discussion and send guidance

A message belongs to the exact rule version on which it was posted. It remains
there after a revision. Posting it does not invoke a model or apply a decision.

1. Add a discussion message on a rule page.
2. Open **Guidance**, or use the rule's guidance link to put that rule first.
3. Choose the rule versions and explicitly select the messages to include.
   The form shows up to six rules and the latest twenty messages per rule.
4. Enter one instruction describing the advice you want, then submit.
5. Inspect the saved request and wait for the worker's response. Later messages or
   rule revisions do not enter the request you already sent.

The [discovery worker](discovery.md#start-the-worker) supports guidance. To run only
normalisation and guidance, start the generation server and use this command from
the repository root, after stopping any other worker on the same data directory:

```text
uv run --locked python tools/run.py --data-root ../extras/runtime worker --routing config/routing/discovery-local.json --endpoint http://127.0.0.1:8081
```

This uses the supplied policy version 3 and does not load an embedding runtime.
Model work runs in the worker, outside web requests.

## Read a response or recover a failed request

| State or message | Meaning and next action |
| --- | --- |
| Queued | Waiting for a worker with an eligible route. Check the worker's data directory and routing file. |
| Running | The worker is processing the saved request. Usage refreshes every five seconds. |
| Responded | Advisory text and its source/request history are available. Apply any chosen change yourself through rule review. |
| Failed | Inspect the error and retained output; invalid or invented version references are refused. |
| Unknown | The worker stopped before completion was recorded. It may have finished externally; inspect before making a new explicit submission. |
| Historical context | A target has changed since submission. Compare the advice with the current rule before acting. |
| Context too large | Reduce the selected material. Requests above 18,000 characters are refused; the model's token limit is checked separately. |

No response edits a rule or applies a decision. Recovery never automatically
resends. Duplicate requests with the same identity and content return the existing
batch; changed content requires a new request. Stale targets are refused before queueing.

Names and rationales are local claims, not authenticated identities. Submitted
context and responses are immutable external files; SQLite holds queue metadata,
small claims, receipts and events. See [operational evidence](operational-evidence.md)
for the distinction between stored output and a successful operation.
''')
