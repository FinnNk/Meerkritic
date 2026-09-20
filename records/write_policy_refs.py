exec(compile(open('WORKSPACE/extras/der-evidence/vs2-interaction/r2/write_tasks.py',encoding='utf-8-sig').read().split("write('README.md'")[0],'<helpers>','exec'))
write('docs/development/code-comments.md',r'''
# Code comments and docstrings

Give callers enough information to use an operation without reading its body.
Explain relevant effects, failures and constraints. Prefer the shortest complete
explanation; brevity must not hide part of the contract.

## What to document

| Location | Explain |
| --- | --- |
| Exposed functions/methods, entry points and HTTP handlers | What callers can rely on, including effects, bounds and expected failures |
| Classes | What instances represent and significant state or evidence rules |
| Internal logic | Non-obvious intent, required ordering and reasons for choices |
| Interfaces | The shared caller contract; concrete implementations add only their specific behaviour |
| Tests | Unusual setup or constraints when the test name is insufficient |

Do not narrate statements, repeat obvious annotations or add comments solely for
coverage. For example, explain why files must be published before metadata makes
them discoverable, rather than saying that the next line writes a file.

## Write a docstring

1. Start with an imperative summary, such as “Return a page of observations.”
   A single sentence is enough for a simple contract.
2. For richer contracts, use Google-style `Args`, `Returns` or `Yields`, and `Raises`
   sections where needed, with four-space section indentation.
3. Describe meaning, bounds, units, ordering, empty results and caller-relevant
   failures. Omit empty/redundant sections and incidental implementation exceptions.
4. Describe decorated functions as callers experience them. A context manager
   returns a managed context; callers need not see a generator API.
5. For class fields that need explanation, use `Attributes`. Distinguish expected
   values from validation actually performed by the class.

Keep British English and the project's 100-character limit. Google is a source
for selected conventions, not an adopted whole-project standard. See
[ADR-0003: Document caller contracts and non-obvious intent](../adr/ADR-0003-document-caller-contracts-and-intent.md)
and the [Python style guide](python-style.md).

## Review and maintain

- Compare interfaces with implementations and real consumers: return meaning,
  bounds, side effects, failure conditions, payload conventions and configuration.
- Update stale comments when behaviour changes. A present docstring does not prove
  that its contract is complete.
- Keep comments for new/changed code in that code's semantic commit. Existing-code
  backfills and changes to guidance have separate commits.
- Preserve actual diary chronology before reconstructing review commits.
- Keep imported research and third-party skill files intact.

Use the [milestone contract challenges](milestone-review.md) and
[documentation checklist](documentation-style.md#author-and-reviewer-checks).
These are judgement checks, not docstring-count targets or new lint exemptions.
''')
p=R/'docs/development/python-style.md';s=p.read_text(encoding='utf-8')
start=s.index('The initial application was');end=s.index('\nReference baseline:',start)
s=s[:start]+'''When materially changing existing code, review the relevant style and caller
contracts. Broader cleanup should be bounded and separately reviewable; do not
claim that every historical style choice has been eliminated.
'''+s[end:]
s=s.replace('This is Meerkritic\'s style policy for maintained first-party Python. It adopts selected ideas from the Google Python Style Guide, not the guide in its entirety. Unlisted upstream rules are reference material, not additional project requirements. The adopted scope and rationale are recorded in [ADR-0004: Adopt a selective Python style guide](../adr/ADR-0004-adopt-selective-python-style.md).', '''This policy applies to maintained first-party Python. It adopts selected ideas
from Google's Python Style Guide, not the entire guide. Unlisted upstream rules
are reference material, not additional requirements. See
[ADR-0004: Adopt a selective Python style guide](../adr/ADR-0004-adopt-selective-python-style.md)
for scope and rationale.''')
s=s.replace('Review the rules relevant to each change and run `uv run --locked python tools/check.py`. Comments on new or changed code belong with that code in semantic history; existing-code backfills have their own commit. Guidance updates remain separate from application. Imported research and third-party skills retain their original form.', '''1. Review the rules relevant to the change and its actual callers.
2. Keep comments for new/changed code with that code in semantic history.
3. Separate existing-code backfills and guidance updates from application.
4. Preserve imported research and third-party skills in their original form.
5. Run `uv run --locked python tools/check.py`.''')
p.write_text(s,encoding='utf-8',newline='\n')
write('docs/edr/README.md',r'''
# Record an evidence-dependent decision

An Empirical Decision Record (EDR) keeps a significant question, hypothesis, method,
results and decision together. Commit the plan before collecting or analysing the
evidence that will decide the choice. This is *pre-registration*.

Use one Markdown file per decision, copied from [the template](template.md) and
named `NNNN-short-decision-name.md`. Keep it proportionate to the question.

## Decide whether an EDR is needed

Both conditions must hold:

1. The choice materially affects research validity, product behaviour, cost,
   performance or a lasting design direction.
2. A plausible result could change which option you choose.

| Example | EDR needed? |
| --- | --- |
| Record token counts during a run | No; this is incidental telemetry. |
| Change a routing default based on measured quality and cost | Yes. |
| Run ordinary correctness tests or implement a prescribed architecture | No. |
| Select an interpretation/grouping method based on evaluation results | Yes. |
| Replace a component because measured operational problems remain unacceptable | Yes. |

Research-pack hypotheses are starting points, not already registered experiments.

## Follow the process

| Step | Action | Record |
| --- | --- | --- |
| Frame | Identify the choice, alternatives, testable prediction and smallest useful investigation. | Prior knowledge, pilot work and data already seen |
| Register | Agree the comparison, sample, measures, thresholds, stopping rule and method. Commit the plan before decision-bearing work. | Exact registered-plan reference, as described below |
| Run | Execute the registered method. | Code, commands, configuration, environment, data identities, failures and exclusions |
| Analyse | Report all planned primary results, including negative or inconclusive outcomes. | Uncertainty, limits and separately labelled exploratory analysis |
| Decide | Record the chosen action, decision-maker and rationale. | Any departure from the registered decision rule |
| Link | Connect the implementation and relevant reviews; use an ADR for a lasting architecture decision. | Updated index and retained history, even if no change is chosen |

To register the plan:

1. Fill and commit the template's plan sections before decision-bearing collection or analysis.
2. Copy that commit's full SHA into the record's registered-plan field. A commit
   cannot contain its own SHA.
3. Commit the reference, registration date and `registered` status **before the first run**.
   A retained local or project-remote commit is sufficient; no external registry is required.

Use statistical significance tests, power calculations or large comparisons when
the claim needs them, not for every investigation. A bounded decision may need only
a small reproducible measurement. Generalisation claims require stronger sampling
and validation, including prescribed repository holdouts and careful negative labels.

## Status and outcome

Update the header and index together, and append a dated history entry.

| Status | Meaning |
| --- | --- |
| `draft` | Question/method still being prepared; no registered evaluation has begun |
| `registered` | Committed plan identified before decision-bearing work |
| `running` | Collection or analysis under way against that plan |
| `analysed` | Results and limitations recorded; decision still open |
| `decided` | Explicit decision and rationale recorded; implementation is separate |
| `withdrawn` | Stopped without a decision; retain reasons and evidence |
| `superseded` | Replaced by a linked later record; retain history/results |

The usual order is draft, registered, running, analysed, decided. Record these
separately from status:

- Evidence outcome: `supports`, `does not support` or `inconclusive`.
- Implementation: `not planned`, `pending` or `implemented`, with a reference.

A successful experiment or decided EDR does not itself complete a milestone or
Double-Entry Review (DER) review.

## Amend a plan honestly

- Leave registered plan sections unchanged. Append a dated amendment naming the
  affected clauses, reason, evidence already seen and implications for validity.
- For a prospective change, commit and identify the amendment before affected work.
- Preserve failed runs when correcting an implementation/method error; record whether
  outcomes were visible before the correction.
- Label unplanned analysis or changes made after seeing relevant results as exploratory.
  They cannot become retrospectively pre-registered.
- Register new confirmatory work before collecting or examining its evidence.
  Use a new EDR for a materially different question.

Existing datasets are allowed: registration precedes the deciding analysis, not
necessarily dataset creation. Disclose earlier access, summaries, pilots and overlap.
If results were already inspected, record that honestly instead of claiming registration.

## Make the work reproducible

Keep a compact evidence inventory with enough information for another person:

| Item | Include |
| --- | --- |
| Code/environment | Exact commit, commands, configuration, lock/versions, relevant platform and seeds |
| Data | Source/revision, selection/query, identities or hashes, access/licence and preprocessing |
| Design | Evaluation units, splits, duplicates, related-source contamination controls and label review where relevant |
| Results | Original measurements/outputs, analysis and immutable references/checksums |
| Reproduction | Procedure, expected result or tolerance and explicit limits |
| Variable model services | Exposed model/provider version, prompt/routing revision, settings and timestamps |

Commit small shareable methods and summaries. Keep large/private datasets, credentials
and raw artefacts outside Git. Use durable public evidence locations where possible;
a local path alone is not an independently reproducible package. When sharing is
restricted, record why and provide the closest permitted substitute, such as hashes,
aggregates, synthetic examples or an executable method. Claim independent reproduction
only after it has actually occurred.

EDRs own empirical plans/results/decisions. [ADRs](../adr/README.md) own architectural
rationale. DER owns review chronology/evidence outside worktrees. Link their records
rather than duplicating evidence stores.

## Index

No EDR is registered yet. The current draft is:

| EDR | Decision | Status | Evidence outcome |
| --- | --- | --- | --- |
| [EDR-0001](0001-discovery-grouping-method.md) | Choose an initial discovery grouping method | draft | pending |
''')
# Keep ADR lifecycle meanings; make creation instructions actionable and put purpose first.
p=R/'docs/adr/README.md';s=p.read_text(encoding='utf-8')
start=s.index("The active format");end=s.index('Record a decision')
format_text=s[start:end];s=s[:start]+s[end:]
s=s.replace('Use sequential filenames `ADR-NNNN-kebab-title.md`. Copy the template and keep the\nindex below in step with each status change. The date records the latest status\nchange. Name the actual decision-makers; distinguish their decision from an\nagent\'s proposal or implementation. Record consultation only when it occurred.', '''## Create or update a record

1. Copy the [MADR template](template.md) to `ADR-NNNN-kebab-title.md`, using the next number.
2. Name the actual decision-makers. Distinguish their decision from an agent's
   proposal or implementation; record consultation only when it occurred.
3. Keep the index in step with each status change. The date is the latest status-change date.
4. Include a linked identifier and short title for related records; retain history.''')
s=s.replace('## Index\n', '## Format and attribution\n\n'+format_text+'## Index\n')
p.write_text(s,encoding='utf-8',newline='\n')
# Foundational plain-English glossary, then preserve specialist reference headings with clearer definitions.
p=R/'CONTEXT.md';s=p.read_text(encoding='utf-8')
s=s.replace('# Project Context Glossary','# Project glossary').replace('This file defines stable project vocabulary only. Keep definitions concise; put design rationale in ADRs or design documents.', 'Stable vocabulary only. Guides explain terms at the point of use; design rationale belongs in ADRs.')
intro='''
## Harness
The local web application used to browse source material, run workflows and review results.

## Normalisation
Turning a source comment and code excerpt into a structured proposed interpretation.

## Interpretation
A model's or reviewer's account of a concern, its supporting evidence and possible wider use.

## Annotation
A human Accept, Edit or Reject decision on a particular model result. An edit retains a corrected interpretation alongside the original.

## Fixture
Synthetic or permitted example data/configuration used to check software behaviour; it is not a human-labelled research sample.

## Frozen selection
A saved copy of explicitly chosen annotations and source material. Later decisions cannot change its inputs. See annotation selection for the recorded fields.

## Embedding
A numerical representation of text used to compare examples for similarity.

## Holdout
Material reserved from the current development/discovery work for later evaluation. Reading it is still data exposure and must be recorded where relevant.

## Immutable
Stored content that is never edited in place. Corrections create a new version and retain the old one.

## Atomic
A group of state changes that is saved entirely or not at all; a failed batch cannot leave some decisions applied.

## Idempotent retry
Repeating the same request identity and content returns the existing result without applying the operation again.

## Provenance
The retained source, versions, transformations and decisions that explain where a result came from.
'''
s=s.replace('\n## Embedding run',intro+'\n## Embedding run',1)
s=s.replace('One explicit invocation over a frozen selection, retaining ordered annotation\nidentities, a pinned model profile and immutable vectors.', 'One requested conversion of selected text into vectors, retaining input order,\nannotation identities and the exact model profile.')
s=s.replace('Deterministic grouping over one pinned embedding artefact, with explicit algorithm\nparameters, membership, representatives and outliers.', 'Grouping one saved set of embedding vectors using recorded parameters. Results\nidentify members, representatives and ungrouped examples (outliers).')
s=s.replace('The paired-history review method used for material software PRs/changes in the factory.', 'A software review method retaining both actual implementation chronology and a\nreconstructed sequence of commits organised for review.')
s=s.replace('A separate current pointer and revision counter fence operational writes.', 'A separate current-version record and counter let writes reject changes made since\nthe caller read the rule.')
s=s.replace('A hash-bound view of typed before/after snapshots and their delta. Its source\nfingerprint detects stale source content; it is not a quality-check or DER verdict.', 'A saved view of before/after architecture records and their differences. A source\nchecksum detects code/configuration changes; the view does not certify quality or review readiness.')
s=s.replace('at a specific commit/slice point','at a specific code revision')
p.write_text(s,encoding='utf-8',newline='\n')
p=R/'AGENTS.md';s=p.read_text(encoding='utf-8').replace('model routing. VS1 completion requires real MAF workflow execution.','model routing. Validate agentic workflows through real MAF execution.')
p.write_text(s,encoding='utf-8',newline='\n')
p=R/'docs/development/milestone-review.md';s=p.read_text(encoding='utf-8').replace('Use the VS1 review as an example, not a required number or catalogue of findings.', 'Use a prior completed review as an example, not a required number or catalogue of findings.')
p.write_text(s,encoding='utf-8',newline='\n')
p=R/'docs/slice-reviews/README.md';s=p.read_text(encoding='utf-8').replace('[VS2 is active](../plans/VS2-plan.md); its first frozen-input batch is under review.', '[VS2 has a final software candidate](VS2-review.md), including its\n[milestone review](VS2-milestone-architecture-review.md). Owner acceptance and the\nhuman-labelled empirical comparison remain outstanding; see the [plan](../plans/VS2-plan.md).')
p.write_text(s,encoding='utf-8',newline='\n')
