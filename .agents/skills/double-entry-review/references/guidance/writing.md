# Explain the change to its reviewer

Apply this component when drafting or updating commit messages, proposition records, PR descriptions, review comments and explanatory code comments. Assume the reader knows the project's purpose, but not this change, its internal identifiers or the author's implementation journey.

## Put the specific change first

Lead with the problem or constraint that makes the change worth reviewing, then explain the chosen change, its observable effect and relevant limits. Include rationale or rejected alternatives where they illuminate a real decision. This is a useful order of explanation, not a requirement for five headings or repeated boilerplate.

A PR describes the overall outcome and how its review units fit together. A commit describes its own contribution, prerequisites and the contract at that checkpoint, including temporary limitations. Do not repeat the whole PR narrative in every commit or claim a later checkpoint's guarantee early.

Translate specialist mechanisms into the concrete input, checks, result or side effect that matters. Define or remove opaque unit IDs and acronyms on first meaningful use; keep identifiers as navigation aids, not substitutes for explanation. Omit project introductions and assertions applicable to almost any PR, such as "improves maintainability" or "adds tests", unless the text explains the specific improvement or obligation.

Summarise what the evidence establishes before listing commands, hashes and log links. Distinguish observed results from intended effects and unavailable verification. Keep detailed audit records accessible without turning the opening paragraph into an operational transcript.

## Take a second editorial pass

Once substantive content is stable, give commit messages and comments a proportionate second pass: "Can this be about 50% shorter without losing clarity or precision?" This is a challenge, not a quota or gate. Remove repetition, generic background and roundabout phrasing; retain meaningful claims, scope, conditions, failure behaviour, side effects, evidence, rationale, uncertainty and identifiers needed for navigation. Compare the revised meaning with the original and leave it unchanged if shortening loses information or introduces telegraphic jargon. Reviewers tighten their own comments; this does not authorise rewriting another owner's prose.

Allow PR descriptions more room for orientation, rationale and the review map. Try the gentler challenge: "Could this be about 10% shorter without losing clarity or precision?" Remove repetition and improve navigation, but leave the description unchanged if shortening would lose useful context or meaning. Both percentages are unvalidated heuristics, not quality criteria, required reductions or grounds for rejecting text. Choose prose or a table for clarity rather than compression alone.

## Use tables for relationships, not decoration

A small table can clarify repeated mappings between inputs or preconditions and outputs or postconditions, or comparable data. Pair each condition with its corresponding outcome; separate lists can imply combinations that the contract does not permit. Keep a simple contract as a sentence. Comparing missing, malformed and valid configuration files may justify a condition/outcome table; "negative sizes are rejected" does not need one.

In code comments, keep tables short and readable in source without relying on Markdown rendering. Retain the design rationale in prose, and do not lose failure behaviour, side effects or limits merely to shorten cells. Data tables should identify units and distinguish zero from missing, unmeasured or failed results. Choose the form that exposes the relationship without adding a mandatory template.

## Keep prose and updates readable

Use one Markdown source line per prose paragraph or ordinary bullet, with blank lines around lists and after headings. Do not hard-wrap prose for a terminal width or insert manual line breaks to control the reader's display. Preserve line structure where it carries meaning, such as code blocks and tables.

Before updating an existing PR description, read its current text and relevant metadata, compare the proposed edit and preserve owner amendments outside the requested change. Do not regenerate from a stale local template. Read back the result to check formatting and retained content. Read-before-write is not an atomic lock: if concurrent edits are evident, reconcile the differences or stop the affected update rather than overwriting blindly. Authority to edit prose does not authorise rewriting commits, changing the PR base or altering unrelated metadata.

## Fictional contrasts

- Opaque: "Completes cfg-2 with canonicalised projection." Useful: "Configuration preview now rejects unknown option names and shows the resolved defaults without changing the saved configuration." Keep `cfg-2` only if it helps locate a review unit. Use this explanation only when those are the actual checks and effects.
- Generic: "This PR improves reliability and adds tests." Useful: "A failed export previously replaced the last usable file. The writer now validates the new output before publication; the failure tests confirm that the previous file remains available." Report passing tests only when the recorded evidence supports that claim, and state any narrower guarantee.
- An owner has added "Older clients still require the previous format." A later edit to explain a new format must retain or explicitly resolve that limitation, not replace the entire description with the author's earlier draft.
