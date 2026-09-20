# Architecture evidence

Generate deterministic typed JSON from Tach, Import Linter and Python metadata:

```sh
uv run --locked python tools/architecture.py snapshot > ../extras/architecture-after.json
uv run --locked python tools/architecture.py snapshot --root <baseline-checkout> > ../extras/architecture-before.json
uv run --locked python tools/architecture.py delta ../extras/architecture-before.json ../extras/architecture-after.json > ../extras/architecture-delta.json
```

Use pinned clean checkouts and record their Git identities beside the outputs in
external review evidence. Schema version 3 contains typed module, import, boundary,
contract and public interface records. Interfaces include declared callable signatures
(annotations, defaults, decorators and async), class bases and annotated fields.
The delta includes changed settings; changed records appear
as removed plus added. Ordering is deterministic with no machine paths or timestamps.

Imports are syntax-level dependencies, including external imports and those inside
functions/type-checking blocks. They are not runtime call paths or exhaustive dynamic
import resolution. Import Linter and Tach remain the enforced checks. Later diagrams
are projections of these typed records. No Archify dependency is introduced.

Interface records describe syntax, not inferred types or behavioural compatibility.
Inherited/dynamic members and undocumented runtime conventions need manual review.
Constructors are included; other underscore-prefixed declarations are omitted.
For a before/after comparison use the same generator and Python version on both
checkouts: regenerate both sides with schema 3 rather than mixing schema versions.
Archived pairs of schema-1 or schema-2 snapshots can still be compared. Preserve the
original evidence and record the newer generator's revision alongside regenerated data.

## Harness view and freshness

Publish a pair explicitly to an external runtime, then open **Architecture**:

```text
uv run --locked python tools/architecture.py publish-view <before.json> <after.json> --data-root ../extras/runtime
```

The canonical generator now lives in `adapters/architecture.py`; the command and
harness use that implementation. Schema 3 adds a deterministic source fingerprint
over declared Python sources, SQL/templates/web assets, configuration files and
the dependency lock. File names and contents participate; checkout newlines are
normalised. A behaviour-only edit can therefore mark the projection stale even
when static imports and public signatures are unchanged.

The view identifies its immutable projection hash and both source fingerprints,
shows before/removed/added/after counts and the full typed records. Reads verify
the stored hash and recompute the delta, then compare the current source fingerprint.
They never silently regenerate review evidence. A stale warning means recapture is
needed; matching fingerprints do not prove the quality checks passed. Documentation,
tests, model weights and runtime datasets are outside this source fingerprint.
DER retains canonical review evidence; this local view is a projection, not a
second readiness ledger or a replacement for exact Git/checkpoint identities.
