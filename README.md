# Meerkritic

**Code review grounded in engineering evidence.**

Meerkritic explores how recurring concerns in code reviews, issue discussions and
source code can become reusable checks. It is an experimental project for
developers and researchers who want to understand why a finding matters and
whether a proposed change improves the code.

Its design centres on three ideas:

- **Traceable evidence.** Connect observations, rules and findings to the material
  that supports them.
- **Inspectable checks.** Express concerns as explicit rules, using deterministic
  tools where sufficient and model-assisted analysis where needed.
- **Human judgement.** Make interpretations available for review and correction,
  and evaluate proposed fixes against the code and its tests.

## Getting started

Meerkritic is in early development. The data import CLI registers the pinned public
CRC-Py sample and preserves its source records and provenance. Observation browsing
is introduced in the next review commit.

With **Python 3.12** and **uv** installed, run from the repository root:

```sh
uv sync --locked
uv run --locked python tools/run.py --data-root ../extras/runtime catalogue
uv run --locked python tools/run.py --data-root ../extras/runtime register crc-py-manual-4176ac0
```

Registration downloads about 2.5 MB, verifies its pinned checksum and prints the
registered metadata for 1,030 records. Repeating it returns the same registration.
Keep the data root outside the repository.

Run `uv run --locked python tools/check.py` for the quality gates and tests.
See the [dataset guide](docs/development/datasets.md) for provenance and recovery,
or the [development guide](docs/development/README.md) for contribution guidance.

## Learn more

- [Repository layout and dependency boundaries](docs/development/structure.md)
- [Project glossary](CONTEXT.md)
- [Empirical decisions: hypotheses, methods and results](docs/edr/README.md)
- [Architecture decisions and their rationale](docs/adr/README.md)

## Contributing

Use [GitHub issues](https://github.com/FinnNk/Meerkritic/issues) to ask questions,
report problems or suggest improvements. For code and documentation changes, read
the [project instructions](AGENTS.md), work on a branch and use Conventional
Commits. Run the quality checks before submitting changes for review.
