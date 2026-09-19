# Verification environment correction

Inspection of p1-environment.json showed that uv run had retained previously installed
web packages even though P1's lock excludes them. The source checkout was correct, but
that environment does not establish strict checkpoint dependency isolation. Preserve
all earlier logs and rerun every checkpoint in a separate checkout with a fresh venv
created by uv sync --locked. Use the *-isolated logs/environment records as final
qualification. No code, lock, tests or assertions change because of this correction.
