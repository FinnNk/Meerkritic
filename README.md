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

Meerkritic is in early development; there is no runnable review application yet.
You can explore the design and work with the development environment.

With **Python 3.12** and **uv** installed, run these commands from the repository
root:

```sh
uv sync --locked
uv run --locked python tools/check.py
```

This installs the locked development dependencies, checks formatting and
architecture boundaries, runs lint checks and runs the tests. See the
[development guide](docs/development/README.md) for details.

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
