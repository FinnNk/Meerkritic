<!-- Follow docs/development/documentation-style.md. Remove inapplicable sections.
Lead with the problem and resulting behaviour; explain terms before using them.
Retain owner amendments when updating an existing description. -->

Describe what changes for the reader and why it matters.

<!-- Where a screenshot clarifies the workflow or visible change, include one
illustration or a useful before/after pair. Follow the writing guide's screenshot
guidance: shareable data, descriptive alt text/caption, immutable image URL and
capture notes. Screenshots supplement instructions and validation evidence. -->

## Review sequence

<!-- For a substantial series, list commits in order and the complete promise each
establishes. Name any unmerged prerequisite and the required review/merge order. -->

| Commit | What it establishes |
| --- | --- |

## Validation

<!-- Populate from retained evidence for the stated revision, not the last PR.
Use docs/development/documentation-style.md#validation-summary. Confirm every
expected standard check ran and passed; name any missing, skipped or failed check.
Link immutable evidence. Keep tables only where the breakdown helps review. -->

**Standard checks:** Not run · revision <!-- short SHA --> · <!-- evidence link -->

<!-- State environment once if relevant. A passing overall flag alone is not enough:
compare the recorded execution with the required checks in tools/check.py.
For documentation-only changes, a test-total line usually suffices.
For software changes, use recorded test categories when useful:

| Test category | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |

Explain changed coverage where it helps review:

| Behaviour | Coverage change |
| --- | --- |

Use only categories the suite defines and counts the evidence supports. Do not
infer added/removed/altered test counts from changed lines or filenames.
Add change-specific evidence and material exceptions; omit empty tables and
routine tool-by-tool rows. -->

## Decisions and remaining work

<!-- Include only relevant owner decisions, limitations and follow-up. Expand
project codes with their descriptive titles on first mention. Do not turn a
passing test or author self-review into an empirical claim or owner approval. -->
