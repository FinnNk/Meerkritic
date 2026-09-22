# CodeGraph setup verification

Evidence for application revision `ea9d8c4367b6b35806d360ecbf4187d57a410978`. This archive is separate from application history and contains no human assessments or index database.

- `verification.json`: scope, revision, environment, checks and limits.
- `quality.log`: canonical project checks, including 253 passing tests.
- `summary.json`: symbol, caller, exclusions and add/rename/delete refresh checks.
- `docs-check.json`: documentation links and imported-source integrity.
- `verify_setup.py` and `check_docs.py`: methods; adjust local ROOT/R/NODE paths to reproduce in a disposable checkout. Install the pinned tool and Python dependencies first. The refresh script creates and removes two previously absent synthetic files.

The detailed command transcript remains in the local evidence directory. Setup instructions and the package lock are in the application commit. These are installation checks, not evidence of improved navigation efficiency.
