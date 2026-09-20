# Development observations

2026-09-20: Initial focused synthetic run passed all eight tests. Ruff found B905
on the intended prefix zip. Fixed by slicing candidates to the attempted prefix
and using strict=True; no contract or ignore weakened. A subsequent sandbox-only
format invocation could not read the host-owned uv cache. Resumed in the already
authorised host context; no ACL or global configuration changed.

Review of persistence found the predecessor field was not shape-checked. Added
checks for a null initial predecessor and a SHA-256 predecessor for attempt records.
This binds metadata shape, not proof that every historic file is present; the guide
states the independent chain-audit limitation. No source checks or human judgements
have been fabricated. Every test fixture is explicitly synthetic.
