# Architecture evidence

The intended boundaries are described in
[the structure guide](../development/structure.md) and enforced by the root
`pyproject.toml` Import Linter contracts and `tach.toml` module declarations.

VS1 will introduce deterministic typed snapshots from those contracts and Python
module metadata, with before/after/delta at slice boundaries. Selected shareable
snapshots may be committed here with source revision and generator version.
Diagrams are projections, not a second architecture source of truth.

No application architecture snapshot generator or runtime is claimed by this
documentation bootstrap. Material-review evidence remains in the external DER store.
