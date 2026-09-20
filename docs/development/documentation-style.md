# Writing documentation people can use

Write for a technically aware reader who is new to Meerkritic. Help them complete
a task or understand a decision without first learning the implementation or the
project's delivery history. These rules apply to maintained guides, references,
agent instructions and PR descriptions. Preserve imported originals and historical
evidence; use the [commenting convention](code-comments.md) for Python docstrings.

## Choose the reader and purpose

| Document | Lead with | Keep elsewhere |
| --- | --- | --- |
| Task guide | What the reader will achieve, prerequisites and steps | Detailed implementation contracts and delivery history |
| Operations guide | Setup, expected results, diagnosis and recovery | A chronological account of previous tests |
| Technical reference | Purpose, terms, behaviour, constraints and examples | Instructions already owned by another guide |
| Contribution policy | Required actions, who performs them and when | Past PR narratives |
| PR description | The problem and resulting behaviour | The author's work diary and raw logs |
| Plan, ADR or milestone record | The relevant decision, scope and evidence | Unrelated history; retain necessary milestone references |

A document can serve more than one purpose if its sections make the distinction
clear. Link to detail when it would interrupt the reader's task; do not create a
new document merely to shorten an existing one.

## Explain before naming

- Use plain English first. Introduce a necessary specialist term where it first
  matters; a glossary link supplements that explanation rather than replacing it.
- Prefer concrete verbs and named objects: say what is saved, checked or changed.
- Keep implementation names in reference sections unless they help the reader act.
- Use the exact UI label for a button or page; put identifiers and commands in code.
- Write in British English. Preserve literal commands, filenames, quoted upstream
  text and standard licence wording.

| Avoid in an introduction | Prefer |
| --- | --- |
| Version-fenced decisions | Reject the decision if the rule changed after the draft was saved. |
| Freeze the effective interpretation | Save a fixed copy of the accepted interpretation or its human edit. |
| Terminal-state fencing | Only the worker that claimed the job may record its result. |
| Source-bound architecture projection | A saved architecture view that warns when the code has changed. |

Do not replace precise terms with vague prose in technical contracts. Explain
terms such as atomic, idempotent and compare-and-swap when readers need them.

## Structure instructions for use

Use **numbered steps when order matters**, bullets for independent actions and
tables for choices, states or repeated task/result comparisons. Do not bury a
procedure in a paragraph. Use short paragraphs for explanations and rationale.

Before publishing a procedure:

1. State prerequisites, working directory, required shell and services.
2. Give complete commands. Mark placeholders and explain where their values come
   from; use the locked project environment consistently.
3. Say what success looks like and what the reader should do next.
4. Place consequential cautions beside the affected step. Provide a recovery action
   for likely failures, not just an error name.

Use tables when they make information easier to compare, not to disguise long
paragraphs inside cells. A state table should explain the meaning and next action.
For a complex workflow, use a small diagram only if it clarifies relationships
better than a short list. Avoid screenshots that will quickly become stale.

## Describe the current system

- Task guides describe the behaviour of their checkout. Remove past milestone
  framing and PR/commit chronology; keep history in plans, ADRs and review records.
- Mention current or future milestones sparingly, only when a limitation or next
  step actually depends on them. File paths and test names may retain historical IDs.
- Check unchanged documents affected by a change: counts, defaults, states, labels,
  configuration examples and claims that an implemented feature is still proposed.
- Distinguish working configuration from illustrative or reserved configuration.
  Do not suggest that a file is loaded when no code reads it.
- Put shared policy in one authoritative guide. Link from other documents and keep
  only the qualification necessary at the point of use.
- Retain material limits: tests do not establish model quality; research claims
  need their evidence. Avoid repeating irrelevant disclaimers in every paragraph.

## PR descriptions

Start with the problem and what the change lets someone do. Include a short
before/after example where it helps. Use the [PR template](../../.github/pull_request_template.md)
as a prompt, removing sections that do not apply.

- Describe each semantic commit by the complete behaviour or obligation it adds.
- Keep the ordered commit map for substantial changes, plus meaningful validation
  and unresolved limitations. Explain what the checks establish.
- Link detailed logs, exact identities and reproduction methods in the evidence
  archive; do not copy the implementation diary into the description.
- State dependencies and owner decisions needed now. Use milestone codes only when
  relevant, with their descriptive titles on first mention.
- Rewrite the description around the final change when scope changes. Preserve
  owner amendments and do not claim tests, independence or approval that did not occur.

### Validation summary

Lead with one compact summary, populated from retained evidence:

> **Standard checks:** Passed · revision `abc1234` · [Evidence]

Replace the illustrative revision and evidence placeholder when publishing. State
the environment once where relevant. Prefer text to badges: it stays readable
without colour or an image service and can link to evidence for an exact revision.
Do not give each routine tool a table row.

1. Read the retained records and logs for the stated revision. Compare the recorded
   execution with every required check in that revision's `tools/check.py`, including
   both Ruff checks, Import Linter, Tach and the test suite. An overall success flag
   alone does not prove that all expected checks ran.
2. Use **Passed** only when every required check ran and passed. Otherwise use
   **Failed**, **Partial**, **Not run** or **Blocked**, naming missing, skipped or
   failed required checks. Report skipped tests separately; do not count them as
   passed or hide them behind a successful suite exit status.
3. Derive statuses and counts from the evidence, not the last PR. Link immutable
   records or logs; keep commands, detailed environments and reproduction details
   there. Name older integration evidence separately from current-head results.
4. Add a test breakdown only when it helps the reviewer. Use categories the suite
   actually defines; do not infer unit/integration categories from test names.
   A documentation-only change usually needs just the recorded test total.
5. Explain changed coverage by behaviour when useful. Authors supply this explanation;
   counts alone do not establish coverage. Added/removed/altered test counts are
   optional, need a stated comparison base and reliable test-identity comparison,
   and must account for renames or moves. Diff line counts are not test counts.
6. Include relevant change-specific evidence, such as documentation checks, migrations,
   live workflows or DER equivalence. Use a small table for meaningful comparisons;
   use short prose or bullets for a single result or material exception.
7. After a head change, refresh affected evidence and the summary. Preserve owner
   edits outside the generated section and check the published result.

For an informative test breakdown, use:

| Test category | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |

For changed coverage, use:

| Behaviour | Coverage change |
| --- | --- |

Fill only useful tables and remove empty ones from the PR. An agent or renderer
may populate statuses and counts from existing evidence, but must check the expected
checks before reporting success. The summary is not another evidence store or a
new validation gate. Keep prose for consequential exceptions; put licence/status
announcements and study decisions in their relevant sections.

## Author and reviewer checks

Apply these before presenting a change, at semantic review and at aggregate review:

- [ ] Can a reader identify the purpose and first useful action from the opening?
- [ ] Are necessary terms introduced before use, with concrete objects and verbs?
- [ ] Are procedures steps or tables, with prerequisites and expected outcomes?
- [ ] Do commands, paths, UI labels and stated behaviour match this revision?
- [ ] Can a reader recover from likely failures without reading implementation code?
- [ ] Is current guidance free of unnecessary milestone history and duplicated policy?
- [ ] Do links work, and does the rendered Markdown remain easy to scan?
- [ ] Are evidence claims and limitations precise without overwhelming the task?
- [ ] Does the PR validation summary match retained evidence for its stated revision,
      account for every expected standard check and expose missing or skipped checks?
- [ ] Do test breakdowns use recorded categories/counts and explain useful coverage
      changes without giving routine tools unnecessary space?

Review meaning, not a word count or checklist score. Check examples against the CLI
and relevant code; run safe examples in a disposable runtime where useful. Never
exercise mutating instructions on a user's research data just to verify a guide.
Do not add brittle prose-matching tests or weaken software checks for editorial work.

Guidance changes have their own semantic commit. Backfills of existing documentation
have separate commits; comments and documentation required by new code normally
belong with that code. Preserve the true implementation diary before reconstruction.
