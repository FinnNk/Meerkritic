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
