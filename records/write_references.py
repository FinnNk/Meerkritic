exec(compile(open('WORKSPACE/extras/der-evidence/vs2-interaction/r2/write_tasks.py',encoding='utf-8-sig').read().split("write('README.md'")[0],'<helpers>','exec'))
write('docs/development/README.md',r'''
# Develop and review Meerkritic

Use this guide to prepare a change, check it and present it for review. For running
the application, start with the [task guides](../README.md). Read [AGENTS.md](../../AGENTS.md)
before implementation; it defines the active scope and required working practices.

## Set up and check

1. Use Python 3.12 and run commands from the repository root.
2. Install the locked dependencies:

   ```text
   uv sync --locked
   ```

3. Run the canonical quality command:

   ```text
   uv run --locked python tools/check.py
   ```

   | Check | Purpose |
   | --- | --- |
   | `ruff format --check .` | Python formatting |
   | `ruff check .` | Configured lint and import-order rules |
   | `lint-imports --no-cache` | High-level dependency contracts |
   | `tach check` | Declared module boundaries and cycles |
   | `python -m unittest discover -s tests -p test_*.py` | Behaviour, integration and failure checks |

The runner uses this checkout's source and interpreter environment. Use the same
command locally and in review checkouts. See [tests](../../tests/README.md) for what
it establishes and [workflow verification](verification.md) for live checks.

Ruff covers first-party Python and project TOML. Pinned third-party skills are
excluded as vendor source; their hashes are retained in `docs/source-manifest.json`.
Do not extend that exclusion or weaken contracts, tests or ignores merely to get
green checks without explicit owner approval.

## Prepare a change

1. Identify the active batch in the maintained plan and inspect the working tree.
   Start a branch from its integrated baseline or an explicit stacked predecessor.
2. Classify the change as routine, material or critical before substantive work.
   Architecture-contract and evidence-policy changes are material. Use the pinned
   [Double-Entry Review skill](../../.agents/skills/double-entry-review/SKILL.md)
   where required, with one history integrator and evidence outside worktrees.
3. Describe the intended review commits. Each should establish a complete behaviour
   or obligation, including its necessary tests, failure handling and documentation.
4. Implement using the [Python style](python-style.md), [commenting](code-comments.md)
   and [documentation](documentation-style.md) guides. Check actual callers as well
   as declared interfaces.
5. Reconcile affected guides, glossary, backlog and [ADR statuses](../adr/README.md#lifecycle-review).
   Check whether a significant evidence-dependent choice needs an [EDR](../edr/README.md).
6. Verify the result and review the combined change before publication.

## Review boundaries

Semantic commits are the primary units of detailed review: each explains one
complete promise. A PR can contain several related capabilities. Balance useful
review boundaries against the overhead of many small PRs; use neither file count
nor a line limit as the deciding rule.

| Author/reviewer check | What to establish |
| --- | --- |
| Complete promise | State what the commit establishes and which earlier contracts it needs. |
| Plausible split | Challenge bundled independent claims; explain the coupling if keeping them together. |
| Evidence at the right point | Include required implementation, tests and operational documentation when the capability first appears. |
| No reliance on later fixes | Verify each required checkpoint with its own source, tests and locked environment. |
| Separate editorial work | Guidance updates and backfills of existing code comments/docs have their own commits. |
| Aggregate review | Revisit interactions and unchanged descriptions made stale by the change. |

For material changes, preserve actual implementation chronology in the DER diary,
then reconstruct the review sequence. Do not manufacture a tidy diary. Follow the
[DER boundary guidance](../../.agents/skills/double-entry-review/references/guidance/boundaries.md)
and the [milestone method](milestone-review.md) for the relevant checks.

When a dependent batch needs its own PR:

1. Stack it on its immediate unmerged predecessor and state the review/merge order.
2. Use additional stacked splits when complexity warrants them. Independent work
   need not form an artificial stack.
3. After the parent lands, update the child's base and verify the resulting revision
   under the applicable DER requirements. The owner approves and merges each PR.

## Write commits and PRs

Use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

```text
type(optional-scope): concise description
```

- Use `feat` for features, `fix` for fixes and appropriate types such as `docs`,
  `test`, `refactor`, `perf`, `build`, `ci` or `chore` for other changes.
- Use meaningful scopes, such as `routing` or `datasets`, and British English prose.
- Mark incompatible contracts with `!` or a `BREAKING CHANGE:` footer explaining
  the impact and migration. Apply this to diary and semantic commits alike.
- Keep any squash-merge title conforming. This convention is not server-side enforcement.

### Agent pull requests

Follow the [writing guide](documentation-style.md#pr-descriptions) and
[PR template](../../.github/pull_request_template.md). Lead with the problem and
resulting behaviour, then provide the commit map, meaningful validation and limits.

On first mention, give a relevant project code its descriptive title, for example
**ADR-0012 (Apply review intent in explicit batches)**. Later mentions may use the
code alone. Avoid references the reader does not need; preserve owner amendments
when updating descriptions or comments.

The `meerkritic-agent[bot]` App publishes branches and PRs. Use its authentication
as well as its Git author identity, keep credentials outside Git, and follow the
[owner-feedback convention](app-bot-feedback.md).

## Acceptance and milestones

- Main requires a PR, one approving review and resolved review threads. New reviewable
  pushes dismiss earlier approvals; someone other than the latest pusher must approve.
- Main blocks force pushes and deletion. Only administrators may merge through the
  separate merge gate; the App has no bypass. The owner merges on GitHub.
- Owner-authored PRs still require another reviewer. Local checks do not imply hosted
  CI execution; inspect current repository rules when qualifying a revision.
- After each slice or agreed milestone, perform the [architecture and guidance review](milestone-review.md)
  before starting the next. Record findings, remedies, evidence and future-work revisions.
- Keep owner acceptance, DER readiness, integration and milestone completion distinct.

Current delivery status belongs in the [backlog](../../IMPLEMENTATION_BACKLOG.yaml)
and [slice reviews](../slice-reviews/README.md), rather than in these instructions.
''')
write('docs/development/routing.md',r'''
# Model routing reference

Routing chooses a model that meets a task's needs and explains that choice. It does
not call a provider. Use [routing commands](routing-operations.md) to preview choices
or inspect retained usage.

## Inputs and selection

| Input or output | Meaning |
| --- | --- |
| `TaskRequirements` | Capabilities, privacy, context and other constraints supplied by the application |
| Model inventory | Versioned available models and their declared capabilities |
| Routing policy | Ordered preferences and constraints; model names live in configuration |
| `RoutingDecision` | Selected model or explicit refusal, versions, context budget and reasons |

Resolve a policy in this order:

1. Invocation override.
2. Task override.
3. Project default.
4. System default.

Unknown/inactive versions are errors. A one-off model override retains the policy
and cannot bypass constraints. Internal/local-only tasks require local models;
project or policy settings can also require locality for public input. Verify
operator-declared locality, capabilities and availability before execution.

| Selection rule | Behaviour |
| --- | --- |
| Hard constraints | Filter privacy, lifecycle, health, capabilities, input/output capacity, excluded reviewer families and hard budgets. |
| Eligible choices | Follow policy order, preferring models inside a supplied soft budget. |
| Hard cost budget | Require compatible currency and versioned quotes; absent/incompatible quotes fail the check. |
| Refusal | Return a decision without a selected model; it does not authorise a remote fallback. |
| Provider failure | An infrastructure observation, not a reason to automatically escalate reasoning strength. |

Cost quotes are caller-supplied estimates, not guaranteed provider charges. Health
and quotes apply to this invocation; callers must refresh them before use.

Input and output capacity are separate. The context strategy reduces usable input
space and reserves output capacity. The workflow adapter must render/count actual
prompt tokens; a selected route alone does not prove that a prompt fits.

## Usage and spend

`Measurement` describes outcome, token counts and timings. Adapters must use these
accounting conventions:

| Value | Convention |
| --- | --- |
| Input tokens | Include cached tokens. |
| Output tokens | Include reasoning tokens when exposed. |
| Unavailable count | `null`, never an invented zero. |
| Estimated hosted spend | Use the price catalogue effective at invocation start; retain its version/currency. |
| Cached-input pricing | Count cached input once; different cache rates require a known cached count. |
| Missing price or required count | Leave the estimate unknown. |
| Provider-reported spend | Retain separately from the estimate. |
| Local execution | Report local/zero API spend, excluding electricity and hardware. |

The compact display shows model, input/output tokens, spend basis and elapsed time.
Provider failures and invalid model output remain distinct outcomes; routing does
not automatically retry either.

## Persistence contract

| Operation | Guarantee |
| --- | --- |
| `RoutingService.route` | Save the decision and exact inventory/policy snapshots before returning, including refusals. |
| Worker invocation | Act only on a returned decision and bind its identity before model work. |
| Record retry | Accept identical identity/content without duplicate events; reject conflicting content. |
| `RoutingService.complete` | Retain one completion per decision. Identical concurrent retries return its original ID. |
| Conflicting completion | Reject changed measurements, outcomes or price-version content without partial writes. |

Each route call represents a new invocation. See
[ADR-0005: Retain immutable routing versions and invocation records](../adr/ADR-0005-retain-immutable-routing-provenance.md)
for the retention decision.

## Examples and reserved interfaces

`config/routing/example.json` is synthetic: it deliberately rejects a remote first
choice for local-only input. It supplies no live endpoint, credentials or weights.
See the [configuration guide](../../config/README.md) for runnable examples.

`routing.continuity` defines records for future policy transitions and agent handoffs:

- A transition retains both policies, requesting actor, reason and time; a no-op is invalid.
- A handoff carries structured task context and evidence references, not an implicit transcript.
- These schemas do not currently execute switching, persist a durable session or
  perform a handoff. Add runtime/persistence support only for a concrete workflow.

Health, budget and context records already participate in selection. Context
construction, provider calls and completion storage belong to the live workflow.
''')
write('docs/development/normalisation-contract.md',r'''
# Interpretation contract

Normalisation proposes a structured interpretation of a supplied review comment
and code excerpt. This reference is for developers integrating or changing the
workflow; see [the task guide](normalisation.md) to run it.

## Responsibility boundaries

| Component | Owns | Does not own |
| --- | --- | --- |
| `WorkflowRunner` | Context preparation, orchestration and output validation | Durable storage or usage accounting |
| `ModelClient` | Provider transport, rendered prompt/token limits and telemetry | Whether evidence supports an interpretation |
| MAF adapter | Actual Microsoft Agent Framework graph and framework observations | Application/domain types |
| Application caller | Retain source identity, route, output and usage | Framework-specific message types |

The framework prepares context, calls the model and validates the response. Core
application/domain types do not depend on Microsoft Agent Framework (MAF).

## Evidence and interpretation rules

- Treat supplied source as untrusted data. Exclude upstream category labels from the prompt.
- Separate whether a concern is actionable from whether it might generalise.
  The schema permits `uncertain`; do not convert uncertainty into an affirmative finding.
- Require evidence for affirmative concerns. Each exact quote must occur uniquely
  in the supplied comment or code.
- Derive character spans on the host: zero-based Unicode indexes, including the
  start and excluding the end. For example, `[0, 3)` identifies the first three characters.
- Quoted-source checks establish where text came from, not the correctness of the
  interpretation. [Human annotation](annotations.md) records Accept/Edit/Reject separately.

## Outcomes and failures

Each outcome returns the prepared prompt/schema version, model output, available
raw provider request/response, measurements and a `FrameworkObservation`. The caller
must retain these with source/dataset identity and the saved route.

| Situation | Required treatment |
| --- | --- |
| Provider failure without a full response | Retain the prepared prompt and available measurements. |
| Partial stream | Do not claim a complete response; partial streams are not retained and usage may be unknown. |
| Invalid schema or evidence | Report a validation failure rather than accept an interpretation. |
| Unexpected runtime/storage exception | Report failure and disclose incomplete evidence. |
| Framework message carries a transport exception | Convert it to plain failure data: measurement and safe error text. |

The locked MAF core version is 1.19.0. Framework messages must use plain failure
data because transport exception objects do not support the required message
copying. Tests exercise the actual framework across provider, semantic and
framework failures; historical integration observations remain in their review records.
''')
write('docs/development/structure.md',r'''
# Repository structure and dependencies

Run commands from the repository root. In the original workspace it is named
`working`, with a sibling `extras` directory for local data; a clone may have a
different name. Runtime data and review evidence must remain outside Git worktrees.

## Find code and documentation

| Location | Responsibility |
| --- | --- |
| `src/semantic_reviewer/domain/` | Research records, valid states and domain rules |
| `src/semantic_reviewer/application/` | Use cases and the storage/runtime interfaces they need |
| `src/semantic_reviewer/routing/` | Model requirements, selection, policies and usage accounting |
| `src/semantic_reviewer/adapters/` | SQLite, filesystem, datasets, analytics, MAF and providers |
| `src/semantic_reviewer/web/` | FastAPI routes, forms and templates |
| `src/semantic_reviewer/bootstrap.py` | Shared dependency construction without web imports |
| `src/semantic_reviewer/asgi.py` | Web application assembly |
| `src/semantic_reviewer/worker.py` | Separate worker entry point |
| `config/` | Small public dataset manifests, model profiles and versioned routing configuration |
| `tools/` | Commands, quality checks and explicit maintenance tools |
| `tests/` | Behaviour, integration and workflow tests using permitted fixtures |
| `docs/` | [Task guides, references, decisions and history](../README.md) |
| `.agents/skills/` | Pinned independent review/design tooling |

Create finer packages or resource directories only when real work needs them;
empty directories are not an architecture plan.

## Dependency rules

| Layer | May depend on | Must hide or avoid |
| --- | --- | --- |
| Domain | Its own domain concepts | Routing, application, adapters and external frameworks |
| Routing | Its own reusable selection/accounting contracts | Domain, application and concrete providers |
| Application | Domain and routing | Concrete persistence, web and MAF types |
| Web | Application operations and allowed core records | Direct persistence or composition access |
| Adapters | The contracts they implement | Imports back into web assembly |
| Shared composition/worker | Concrete dependencies needed for execution | Direct or indirect web imports |

Import Linter defines high-level contracts; Tach enforces concrete module dependencies
and cycles. Callers should not manage SQL transactions, Parquet layouts or provider
response objects. Add interfaces when actual callers and implementations need them,
not as a forwarding layer for each entity. Concrete model names stay out of domain
and application routing logic.

## Local data and evidence

- Keep datasets, derived Parquet, SQLite, large outputs and model weights outside Git.
- Version small public manifests, methods, safe summaries and hashes when useful.
- Keep DER review evidence in its external store. The harness only indexes references.
- EDRs own empirical plans/results; ADRs own design decisions. Link their evidence
  rather than creating competing copies.
- A local path records where evidence lives; it is not proof that another person can reproduce it.

See [configuration](../../config/README.md) and [operational evidence](operational-evidence.md).
''')
write('docs/architecture/README.md',r'''
# Compare architecture and recognise stale views

An architecture snapshot records declared modules, imports, dependency rules and
public interfaces. A comparison shows what was added or removed. The web view also
warns if the current code differs from the saved snapshot.

## Capture and publish a comparison

You need Python 3.12, the locked environment and two clean checkouts with known Git
commits. Run from the **after** checkout's repository root. Use its generator for
both snapshots; `<baseline-checkout>` is the path to the earlier checkout.

1. Create the external output directory if needed, for example with
   `New-Item -ItemType Directory -Force ../extras` in PowerShell.
2. Capture both snapshots:

   ```text
   uv run --locked python tools/architecture.py snapshot --root <baseline-checkout> > ../extras/architecture-before.json
   uv run --locked python tools/architecture.py snapshot > ../extras/architecture-after.json
   ```

3. Generate the difference (called a *delta*):

   ```text
   uv run --locked python tools/architecture.py delta ../extras/architecture-before.json ../extras/architecture-after.json > ../extras/architecture-delta.json
   ```

4. Record both Git commit IDs and the generator's commit with the external evidence.
5. Publish the pair to the same data directory as your web application:

   ```text
   uv run --locked python tools/architecture.py publish-view ../extras/architecture-before.json ../extras/architecture-after.json --data-root ../extras/runtime
   ```

6. Open **Architecture**. Expect before/removed/added/after counts, expandable records
   and an indication of whether the saved after-snapshot matches the current source.

Use PowerShell 7 or another shell that writes UTF-8 for these redirections. When
using Windows PowerShell 5.1, pipe output to `Set-Content -Encoding utf8` instead.

## Interpret the view

| Item | Meaning |
| --- | --- |
| Source fingerprint | A checksum of relevant filenames and contents, including Python, SQL, templates/assets, configuration and the dependency lock |
| Stale warning | Code or configuration differs from the saved after-snapshot. Recapture explicitly before relying on it. |
| Matching fingerprint | The recorded source matches; it does not prove checks passed. |
| Changed record | Represented as a removal plus an addition |
| Projection hash | Identity of the stored before/after/delta view |
| No published view | Run the explicit publish command for this runtime. |

Reads verify the stored content and recompute its delta; they never silently
regenerate evidence. Body-only edits can make a view stale even if imports and
signatures are unchanged. Newline differences between checkouts are normalised.
Documentation, tests, model weights and runtime datasets are outside the fingerprint.

## Reference and limits

- Schema 3 contains modules, imports, boundaries, contracts and public interfaces.
  Interface records include signatures, annotations, defaults, decorators, async,
  class bases and annotated fields. Constructors are included; other underscore-prefixed
  declarations are omitted.
- Imports are syntax-level records, including function-local and type-checking
  imports. They are not runtime call paths or exhaustive dynamic dependency analysis.
- Snapshots describe syntax, not inferred types or behavioural compatibility.
  Check inherited/dynamic members and runtime conventions separately.
- Use the same generator and Python version for a comparison. The harness requires
  schema 3 on both sides; archived pairs of schema 1 or 2 remain comparable by the CLI.
  Preserve originals when regenerating evidence with a newer generator.
- Import Linter and Tach remain the enforced checks. Diagrams and this view are
  presentations of typed data; DER retains the authoritative review evidence.

The shared generator is `src/semantic_reviewer/adapters/architecture.py`;
`tools/architecture.py` is its command-line entry point.
''')
write('config/README.md',r'''
# Configuration

Configuration files describe datasets and model choices. Pass the intended file
explicitly to the command; the application does not load `.env` automatically.

| Location/example | Purpose |
| --- | --- |
| `datasets/` | Public source URL, revision, hash and licence manifests |
| `routing/example.json` | Synthetic selection example; not a live provider inventory |
| `routing/llama-local.json` | Tested local normalisation configuration |
| `routing/discovery-local.json` | Local normalisation, embedding, synthesis and guidance policies |
| `models/nomic-embedding-fixture.json` | Pinned embedding model identity and input preparation |

- Keep versions referenced by existing runs. Changed content requires a new version.
- Use command-line options for current workstation settings, such as `--data-root`,
  `--routing` and `--endpoint`. See [local setup](../docs/development/local-inference.md)
  and [discovery setup](../docs/development/discovery.md).
- `.env.example` only records reserved future names; no loader consumes it.
- Keep secrets, machine-specific absolute paths, private manifests and datasets out of Git.
- The imported research routing YAML is historical advice, not active configuration.
''')
write('.env.example',r'''
# Reserved future settings only: the application does not read .env files.
# Use the documented command-line options for current runtime configuration.
MEERKRITIC_DATA_ROOT=
MEERKRITIC_RUNTIME_ROOT=
MEERKRITIC_DER_EVIDENCE_ROOT=
''')
write('tests/README.md',r'''
# Run and understand the checks

From the repository root, with Python 3.12:

```text
uv sync --locked
uv run --locked python tools/check.py
```

Expect Ruff, Import Linter, Tach and all `test_*.py` unittest tests to pass.
The runner selects this checkout's source and environment.

| Area | Examples of coverage |
| --- | --- |
| Data and annotations | Integrity, real SQLite/DuckDB/Parquet, immutable edits, progress and restart |
| Routing and models | Version retention, privacy/context rules, usage and actual MAF graphs with deterministic model responses |
| Worker and evidence | Process exclusion, recovery without automatic replay, publication and atomic events |
| Discovery and rules | Fixed selections, embeddings/grouping, synthesis, inherited evidence and concurrent decisions |
| Research interaction | Saved/apply distinction, whole-batch rollback, discussion, advice-only responses and unknown completion |
| Web and architecture | Escaping, bounded input, source freshness, corrupt projections and forbidden imports |

`test_vs1_path.py` retains its historical filename and joins the input-to-annotation
path, restart and usage export. Other tests cover later workflows. Live-model
compatibility is checked separately using [workflow verification](../docs/development/verification.md);
a deterministic test response does not establish model quality.

## Add or review tests

- Test the promised behaviour and meaningful failure boundaries, not a copy of the implementation.
- Keep tests near related behaviour; introduce subdirectories only when they improve navigation.
- Architecture negative controls must fail for the intended forbidden dependency.
  A setup failure or arbitrary nonzero exit is not evidence of that boundary.
- Use small synthetic or explicitly permitted fixtures. Full datasets, secrets and
  live outputs remain in external runtime/evidence storage.
- Label automated decisions as test data, not human research labels.
- For editorial changes, check links, commands and rendering without introducing
  brittle tests that merely match prose. Follow the [documentation checklist](../docs/development/documentation-style.md#author-and-reviewer-checks).
''')
# Preserve the original milestone account, adjusting links for its archival location.
p=R/'docs/development/vs1-verification.md';s=p.read_text(encoding='utf-8')
for target in ('local-inference.md','normalisation.md','operational-evidence.md'):s=s.replace(']('+target+')','](../development/'+target+')')
write('docs/slice-reviews/VS1-verification.md','> Historical verification account. Its status statements describe the recorded milestone.\n> For current instructions, use [workflow verification](../development/verification.md).\n\n'+s)
p.unlink()
p=R/'docs/slice-reviews/VS1-progress.md';p.write_text(p.read_text(encoding='utf-8').replace('../development/vs1-verification.md','VS1-verification.md'),encoding='utf-8',newline='\n')
p=R/'docs/README.md';p.write_text(p.read_text(encoding='utf-8').replace('development/vs1-verification.md','development/verification.md'),encoding='utf-8',newline='\n')
write('docs/development/verification.md',r'''
# Verify a local workflow

Use a disposable data directory to check that an installation works from source
input to reviewed output. Keep its commands, source revision, configuration and
results outside the repository. Never run failure experiments on live research data.

## Prepare

1. Check out the exact commit to verify in an isolated checkout.
2. Install with `uv sync --locked` and run `uv run --locked python tools/check.py`.
3. Choose a fresh external data directory and use it for every command and process.
4. Follow [local inference setup](local-inference.md) to verify/start the generation server.
5. [Register the public sample and serve it](../../README.md#browse-the-sample).
   Confirm that you can browse comments and code.

## Exercise the workflows

| Step | Action | Expected observation |
| --- | --- | --- |
| 1 | Submit normalisation while the worker is stopped, then run a worker with `--once`. | HTTP queues promptly; the worker later records output or an inspectable failure. |
| 2 | Inspect a successful result. | Source, structured interpretation, quotes, model usage and framework observation are available. |
| 3 | Accept, Edit and Reject separate successful results. Label automated decisions as test decisions. | Original output stays unchanged; edits and decisions remain after restart. |
| 4 | Freeze explicit test annotations using the [selection guide](selections.md). | Included/excluded records and exact chosen versions are inspectable. |
| 5 | Start the embedding server and [discovery worker](discovery.md), then embed and group. | Ordered vectors, groups, representatives and outliers retain source references. |
| 6 | [Request a candidate rule](rules.md). | A proposed rule or a valid insufficient-evidence result is retained with the model trace. |
| 7 | [Save and apply a decision draft](research-interaction.md). | Saving changes no rule decision; applying records the batch and history. |
| 8 | Send explicitly selected discussion as guidance. | The response is advisory and leaves rule definitions/decisions unchanged. |
| 9 | [Publish an architecture view](../architecture/README.md). | It identifies saved source and warns when that source changes. |

Model output varies. Retain failed attempts; do not bypass validation merely to
obtain a successful example. If no valid rule is proposed, record that outcome and
which dependent checks could not run.

## Challenge failure and recovery

Perform these only in the disposable runtime:

- Use an unavailable loopback model endpoint for one request. Expect a provider
  failure, not automatic selection of a stronger model.
- Interrupt a worker after it claims a job. Restart after the process exits and
  confirm interruption/unknown completion, retained history and no automatic replay.
- Save a rule draft, change one target through another explicit operation, then
  apply the old draft. Expect no partial decisions and a retained conflict draft.
- Restart the web application and worker. Inspect decisions, events and progress.
- [Export usage](routing-operations.md#export-completed-usage) and query it with DuckDB.
  Unavailable counts must remain null.
- Inspect `job-log`, and run `index-artefacts` after an upgrade as described in
  [operational evidence](operational-evidence.md).

## Record the result

- Identify the exact code commit, lockfile, Python/platform and local model/server versions.
- Retain commands, configuration, source/model hashes, run/result IDs and actual outcomes.
- Record unrun steps and their reasons, partial failures and reproduction limits.
- Keep software-test decisions separate from human labels. Compatibility does not
  establish the quality of a model, prompt or grouping method.
- Use the [EDR process](../edr/README.md) before a significant comparative decision.

Windows/Python 3.12 is the tested platform. Synthetic hosted-price tests are not
billed hosted calls. A model file hash cannot attest which bytes another running
process loaded. No independent reproduction or hosted CI execution follows from
these instructions alone; report only what was actually checked.
''')
