# Configuration

Configuration files describe datasets and model choices. Pass the intended file
explicitly to the command; the application does not load `.env` automatically.

| Location/example | Purpose |
| --- | --- |
| `datasets/` | Public source URL, revision, hash and licence manifests |
| `routing/example.json` | Synthetic selection example; not a live provider inventory |
| `routing/llama-local.json` | Tested local normalisation configuration |
| `routing/discovery-local.json` | Local normalisation, embedding, synthesis and guidance policies |
| `models/nomic-embedding-fixture.json` | Pinned embedding model identity and input preparation |

- Keep versions referenced by existing runs. Changed content requires a new version.
- Use command-line options for current workstation settings, such as `--data-root`,
  `--routing` and `--endpoint`. See [local setup](../docs/development/local-inference.md)
  and [discovery setup](../docs/development/discovery.md).
- `.env.example` only records reserved future names; no loader consumes it.
- Keep secrets, machine-specific absolute paths, private manifests and datasets out of Git.
- The imported research routing YAML is historical advice, not active configuration.
