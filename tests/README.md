# Tests

Application tests arrive with the behaviour they verify. This bootstrap contains
no application behaviour and therefore no application behaviour tests. The three
architecture negative controls prove that both Import Linter and Tach reject a
domain-to-adapter dependency and web access through shared worker composition.
A separate Import Linter control rejects direct web-to-SQLite access; external
product boundaries are Import Linter's responsibility, not Tach's module graph.
They require the intended contract diagnostic, not just a failing command.
The canonical quality command discovers `test_*.py` through Python's standard
`unittest` runner. These controls do not establish VS1 functionality.

Use `unit/`, `integration/` and `e2e/` as real tests are introduced. Fixtures must
be small, synthetic or explicitly permitted for redistribution. Full datasets,
private examples, model outputs and credentials do not belong here.
