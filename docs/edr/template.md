# EDR-NNNN: <decision title>

<!-- Copy to NNNN-short-decision-name.md. Replace placeholders and remove these instructions. Keep sections concise; use "not applicable — reason" where needed. Freeze the registered plan sections and append subsequent changes. -->

- Status: draft
- Created: YYYY-MM-DD
- Owner: <name>
- Decision-maker(s): <name(s)>
- Registered on: <date/time with timezone; pending until registration>
- Registered plan: <full Git commit SHA containing the completed plan, repository URL and path; pending until committed>
- Evidence outcome: <pending | supports | does not support | inconclusive>
- Implementation: <not planned | pending | implemented; link if available>
- Related records: <research question, slice, ADR, DER reference, predecessor/successor as applicable>

## Registered plan

<!-- Complete and commit this section before decision-bearing collection/analysis. Record that commit SHA in the header afterwards, before running. Do not edit this section once registered; append amendments below. -->

### Decision and hypothesis

- **Choice and significance:** <what may change, why it matters, and why evidence could change the choice>
- **Options and comparator:** <candidate option(s), baseline/control or null expectation; justify an absent comparator>
- **Hypothesis:** <falsifiable prediction, with population and expected direction or magnitude>
- **Prior knowledge and exposure:** <existing evidence, pilot results, data already inspected and possible contamination>

### Data and design

- **Unit and target population:** <for example repository, observation or workflow run; scope of the claim>
- **Sample and selection:** <source/pinned revision, size or bounded selection rule, inclusion/exclusion rules and rationale>
- **Partitions and independence:** <pilot/development/evaluation separation; repository-level holdouts where required; duplicates, related sources and leakage controls, or why not applicable>
- **Labels and adjudication:** <label meaning, human procedure, blinding/agreement where relevant; preserve weak versus verified negatives>
- **Comparison procedure:** <paired/randomised/order controls, repetitions and seeds where relevant>

### Measures and decision rule

| Measure | Definition and aggregation | Threshold or interpretation | Role |
| --- | --- | --- | --- |
| <measure> | <including denominator, handling missing/failed observations and uncertainty if needed> | <pre-set criterion> | <primary / guardrail / secondary> |

- **Rule:** <which result leads to which choice; include guardrail failures, ties, trade-offs and inconclusive results>
- **Stopping rule and limits:** <fixed sample/run budget or pre-set sequential rule; time/cost limits and treatment of early stopping>
- **Analysis:** <planned calculations/comparisons, exclusion rules and uncertainty method appropriate to the claim>

### Method and reproduction plan

- **Code and commands:** <method/script path and intended command; pin the executed commit in each run entry>
- **Environment:** <dependency lockfile, runtime and relevant platform/hardware constraints>
- **Configuration:** <versioned configuration, prompts, routing/inventory/price revisions and seeds where relevant; no credentials>
- **Data identity:** <source URL/identifier, pinned revision, content hashes, preprocessing/selection procedure and licence/access conditions>
- **Outputs:** <where original run outputs, raw measurements, analysis and checksums will be stored>
- **Independent reproduction:** <steps, expected outputs/tolerances and what can be shared; restrictions and fallback documentation if reproduction is difficult>

## Amendments and deviations

<!-- Append entries. Never rewrite the registered plan. An amendment affecting future work must be committed and identified before that work; disclose results already seen. -->

None recorded.

<!-- Entry format:
- Date/time:
- Plan clauses affected and change:
- Reason; evidence already visible:
- Classification: prospective amendment / execution deviation / exploratory analysis
- Amendment commit and effective run(s):
- Validity implications and mitigation:
-->

## Runs and evidence inventory

No runs recorded.

<!-- Add one compact entry per run, or link an immutable manifest with these fields:
- Run ID and date/time:
- Effective registered plan/amendment reference:
- Code commit; exact command; configuration; environment/dependency references; seeds:
- Data revision/hash; actual selection/split identifiers:
- Provider/model/version, request settings and timestamp if relevant:
- Outcome, exclusions/failures and deviation references:
- Raw outputs, measurements and analysis locations; checksums:
- Access/licence conditions and shareable reproduction instructions:
-->

## Results and interpretation

Pending.

<!-- Append dated analyses. Report every primary measure and guardrail against the registered threshold, sample counts, missingness/failures and uncertainty as appropriate. Link evidence entries. Distinguish registered analyses from exploratory findings. State supports / does not support / inconclusive with limitations; preserve negative and superseded results. -->

## Decision

Pending.

<!-- Record date, decision-makers, action chosen and why. Apply the registered decision rule or explicitly justify a departure. Distinguish the evidence result from judgement and implementation. Link a resulting ADR where the choice is architectural; link implementation separately when it exists. Record reconsideration triggers if useful. -->

## History

| Date/time | Status or event | Author | Reference / reason |
| --- | --- | --- | --- |
| YYYY-MM-DD | draft | <name> | Initial question and plan. |

<!-- Append registration, status transitions, amendments, analyses, decision and implementation references. Header/index describe current state; this history preserves dated progression. -->
