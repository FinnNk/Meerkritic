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

Meerkritic is in early development. The local harness can register a public sample
and browse review comments alongside their code context. A local worker can normalise
an observation into an evidence-linked interpretation. Human annotation is still in development.

With **Python 3.12** and **uv** installed, run these commands from the repository
root:

```sh
uv sync --locked
uv run --locked python tools/run.py --data-root ../extras/runtime register crc-py-manual-4176ac0
uv run --locked python tools/run.py --data-root ../extras/runtime serve
```

Open [localhost:8000](http://127.0.0.1:8000) to browse the 1,030-record sample.
Registration downloads about 2.5 MB and verifies the pinned source checksum. Keep
the data root outside the repository; use the same path for registration and serving.
The server binds to this computer only.

To run model normalisation, follow the [local workflow guide](docs/development/normalisation.md)
to start llama.cpp and the worker, then choose **Normalise** beside an observation.
Inspect results, provenance and failures from **Normalisation jobs** in the harness.

Run `uv run --locked python tools/check.py` for formatting, lint, architecture and
behaviour checks. See the [dataset guide](docs/development/datasets.md) for source
provenance, storage and recovery, or the [development guide](docs/development/README.md)
for the contribution workflow.

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
