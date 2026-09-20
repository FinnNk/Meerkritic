# Python style

This policy applies to maintained first-party Python. It adopts selected ideas
from Google's Python Style Guide, not the entire guide. Unlisted upstream rules
are reference material, not additional requirements. See
[ADR-0004: Adopt a selective Python style guide](../adr/ADR-0004-adopt-selective-python-style.md)
for scope and rationale.

## Adopted scope

| Area | Project rule | Google reference section |
| --- | --- | --- |
| Documentation | Follow the [commenting convention](code-comments.md), including complete caller contracts and class meaning. | 3.8 |
| Expressions | Use straightforward expressions and comprehensions; expand them when control flow becomes difficult to follow. | 2.7, 2.10, 2.11 |
| State | Prefer explicit dependencies and avoid mutable global state and mutable default arguments. | 2.5, 2.12 |
| Errors | Catch expected failures narrowly; validate external input explicitly rather than with assertions. Explain actual failure conditions in error messages. | 2.4, 3.10.2 |
| Resources | Make ownership and cleanup explicit, normally through context managers. | 3.11 |
| Functions | Keep a coherent purpose; length is a review signal rather than a mandatory splitting threshold. | 3.18 |
| Types | Annotate public interfaces and clarify difficult internal types without repeating obvious local information. | 3.19 |

## Project choices and precedence

- Ruff owns formatting, import ordering and configured lint rules. Retain the existing 100-character limit. This adoption does not add Pylint, another formatter or blanket docstring linting.
- Keep absolute imports. Direct imports of clearly named classes, types and functions are permitted; module-qualified names are useful when they clarify origin or prevent ambiguity.
- Use British English and imperative docstring summaries. Four spaces indent Python blocks and docstring sections.
- Import Linter and Tach remain authoritative for module dependencies. Style preferences do not justify weakening these contracts, tests or ignores; the existing explicit-approval requirement applies.
- Framework callbacks may rely on framework inference. Treat annotations that alter HTTP validation or serialisation as behavioural changes, with their own evidence, rather than incidental style corrections. Prefer annotations on application-owned interfaces; do not add `Any` merely to claim coverage.
- Keep useful explanations under review rather than enforcing word counts, universal section lists or fixed function lengths. This guide works alongside software-design-clarity; splitting a coherent operation merely to shorten it can make the design worse.

These explicit project choices take precedence over the selected upstream advice. Other Google conventions, including module-only symbol imports, its line limit, its lint tooling and per-file licence boilerplate, are not adopted by this decision. Existing licensing and source-attribution arrangements continue to apply.

## Applying and maintaining the policy

1. Review the rules relevant to the change and its actual callers.
2. Keep comments for new/changed code with that code in semantic history.
3. Separate existing-code backfills and guidance updates from application.
4. Preserve imported research and third-party skills in their original form.
5. Run `uv run --locked python tools/check.py`.

When materially changing existing code, review the relevant style and caller
contracts. Broader cleanup should be bounded and separately reviewable; do not
claim that every historical style choice has been eliminated.

Reference baseline: Google's guide at revision [`3b8822983dc779c498961cc86332a28c07590f64`](https://github.com/google/styleguide/blob/3b8822983dc779c498961cc86332a28c07590f64/pyguide.md), dated 11 September 2026 and accessed 19 September 2026. The [rendered guide](https://google.github.io/styleguide/pyguide.html) is convenient for reading; later upstream edits do not automatically change this policy. Review and record any future changes to the adopted scope.
