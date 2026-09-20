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
