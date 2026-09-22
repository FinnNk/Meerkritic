# Writing documentation people can use

Use the reusable [technical-documentation skill](../../.agents/skills/technical-documentation/SKILL.md) for maintained guides, references, READMEs, agent instructions and PR descriptions. It contains the general writing method and author/reviewer checks. This guide adds Meerkritic's local choices and repeats useful shared reminders; both apply. Repetition here does not mean the advice is specific to this project.

The repository copy is versioned with the project. The same skill folder can be installed in a personal skills directory for other projects; it has no Meerkritic, Python or GitHub dependency. When changing the general advice, update the repository copy and deliberately refresh any personal copy. A personal installation is not required to read these instructions.

## Shared advice and local choices

| Topic | Shared advice | Meerkritic choice |
| --- | --- | --- |
| Audience | Explain necessary terms for the intended reader. | Default to a technically aware reader unfamiliar with Meerkritic. |
| Language and encoding | Use explicit UTF-8; preserve literals and confirm saved-text corruption before repair. | British English for maintained prose; preserve standard licence wording. |
| Current guides | Describe current behaviour and keep delivery chronology in historical records. | Describe this checkout; retain relevant history in plans, ADRs and review records. |
| Terminology | Explain terms where needed; a glossary supplements the explanation. | The glossary is [CONTEXT.md](../../CONTEXT.md). |
| Code documentation | Follow the host project's docstring and comment conventions. | Use the [commenting convention](code-comments.md) and [Python style guide](python-style.md). |
| Instructions | Use steps or tables with prerequisites, complete commands, expected outcomes and likely recovery actions. | State the working directory, shell and services; use the locked project environment. |
| Research claims | Software checks do not establish model quality or empirical validity. | Keep hypotheses, methods, observations and decisions in [EDR records](../edr/README.md). |
| Preserved material | Preserve imported originals and historical evidence. | This includes imported research and pinned third-party skills. |

Keep useful local explanations when they prevent misunderstanding. For example:

| Implementation term | Plain-English explanation |
| --- | --- |
| Version-fenced decision | Reject the decision if the rule changed after the draft was saved. |
| Frozen effective interpretation | A fixed copy of the accepted interpretation or its human edit. |
| Terminal-state fencing | Only the worker that claimed the job may record its result. |
| Source-bound architecture projection | A saved architecture view that warns when the code has changed. |

## Screenshots that help readers act

Follow the skill's [screenshot guidance](../../.agents/skills/technical-documentation/references/screenshots.md). The distinction here is:

- **Shared reminders:** capture the actual interface using shareable demonstration data; label prepared outputs. Use descriptive filenames, relative document links, immutable revision URLs in PRs, useful alt text and a caption explaining the state. Retain capture details and reproduction limits.
- **Local choices:** use the synthetic harness in a separate runtime, modestly sized PNGs in `docs/images/`, and capture records beside the images. Keep runtime databases and raw captures outside application Git worktrees. Do not create research judgements or invoke models merely to furnish illustrations.
- **Local reproduction:** reuse the [demonstration fixture and capture conventions](../images/README.md). Existing overview and focused-panel widths are useful defaults, not requirements to crop away necessary context.
- **Shared maintenance:** review affected images after UI changes. Inspect them at the intended display size and in the rendered document when accessible; explicitly record unavailable checks. Preserve historical captures rather than rewriting their provenance.

Screenshots supplement text and behaviour checks. They do not establish that a saved judgement, model call or workflow is correct.

## PR descriptions

Use the [PR template](../../.github/pull_request_template.md), the skill's [PR guidance](../../.agents/skills/technical-documentation/references/pr-descriptions.md) and the project [review-boundary method](README.md#review-boundaries).

- **Shared reminders:** lead with the concrete problem and resulting behaviour. State dependencies, decisions needed now and material limitations. Read the current description before updating it, preserve owner amendments and verify the published result. A passing check or author self-review is not owner approval.
- **Local review structure:** keep the ordered semantic-commit map for substantial changes, describing each complete promise. Name unmerged prerequisites and the review/merge order for stacked PRs.
- **Local evidence practice:** keep logs, full identities and reproduction details in the relevant evidence archive. Retain the true diary independently of the description whenever DER applies.

### Validation summary

Lead with one compact summary populated from retained evidence for the stated revision. Use readable text and a stable evidence link; do not list each routine tool in a table. Missing checks must remain conspicuous.

The procedure below repeats the reusable skill's validation method. The named command/tool set and DER evidence references are Meerkritic-specific; honest statuses, useful counts and preservation of owner edits apply generally.

1. Read the stated revision's `tools/check.py` and compare actual execution with every expected command: both Ruff checks, Import Linter, Tach and the test suite. An overall success flag alone is insufficient.
2. Report **Passed** only when every required check ran and passed. Otherwise use **Failed**, **Partial**, **Not run** or **Blocked**, naming missing/skipped/failed required checks. Report skipped tests separately.
3. State the relevant environment once. Derive counts and status from retained records; identify older integration evidence separately from current-head results. A documentation-only change generally needs the recorded test total and relevant document checks.
4. Use recorded suite categories for a useful test breakdown. For added/removed/altered counts, state the comparison base and compare reliable test identities, accounting for moves and renames. Changed lines/files are not test counts. Explain changed coverage by behaviour where helpful.
5. Add change-specific evidence such as documentation checks, migrations, live workflows or DER equivalence. Use tables for useful comparisons, not a row per standard tool. Link detail in the existing evidence store.
6. Refresh affected evidence and the summary after a head change. Preserve owner text outside generated sections and read back the result.

The summary is not another evidence store or a new gate. Follow the reusable guidance for [summary examples and table choices](../../.agents/skills/technical-documentation/references/pr-descriptions.md#compact-validation-summary).

## Author and reviewer checks

Apply the skill's [tick-box review checklist](../../.agents/skills/technical-documentation/SKILL.md#review-before-delivery) before presenting a change, at semantic review and at aggregate review. The checks below combine shared reminders with Meerkritic's local choices so reviewers can use them directly:

- [ ] British English, exact UI labels and saved UTF-8 text are intact; commands use the locked project environment.
- [ ] Current guides match this checkout, including affected unchanged guides and images. Imported originals and historical records remain intact.
- [ ] Research claims retain their evidence limits; screenshots use shareable fixtures and retain capture provenance.
- [ ] The PR summary accounts for every expected standard check at the stated revision, including missing or skipped checks, and links the appropriate evidence.
- [ ] Commit boundaries follow the project's semantic review process. Apply the skill's [conditional commit advice](../../.agents/skills/technical-documentation/SKILL.md#keep-documentation-changes-reviewable): guidance changes have their own commit; existing-document backfills have separate commits. Documentation and comments required by new code normally belong with that code.

Review meaning, not a checklist score. Verify safe examples in disposable runtimes where useful; never mutate the owner's research data merely to validate instructions. Do not add brittle prose-matching tests or weaken software checks for editorial work. Preserve the true implementation diary whenever DER applies.
