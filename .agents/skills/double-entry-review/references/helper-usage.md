# Mechanical helper interface

Use Python 3.10+ and Git; the runtime has no third-party Python dependencies.
`python3 <skill-dir>/scripts/der.py --help` lists executable helper commands.
These are distinct from the skill's agent operations: there is no executable
`der.py reconstruct`, `publish`, `review`, or `integrate execute`.

| Helper | Action |
|---|---|
| `doctor` | Local runtime/client availability; no model invocation |
| `status --repo R` | HEAD, branch, tracked/untracked worktree state |
| `equivalence --repo R --diary D --semantic S [--diary-base B --semantic-base B2]` | Resolve and compare full tracked trees; optional base/ancestry checks |
| `inventory --repo R --base B --tip S` | Ordered commit identities and per-commit/final diff statistics |
| `snapshot --repo R --store E --pair P --round r1 --diary-base B --semantic-base B2 --diary D --semantic S` | Create an equivalent-pair manifest and self-contained bundle in a new external round directory |
| `check-round --manifest M [--repo R]` | Check round structure, bundle digest/heads and recorded object identities |
| `validate-review --manifest M --report J` | Validate report schema, snapshot binding and coverage claims |
| `record --repo R --store E --pair P --event J --expected-last none-or-hash` | Append a versioned local event using a compare-and-swap predecessor |
| `ledger --store E --pair P` | Verify chain and return latest event digest/count |
| `route <skill-operation...>` | Parse the supported command vocabulary and return required references; never execute it |

All helper output is JSON. Exit 0: requested mechanical check/action succeeded.
Exit 1: integrity/equivalence mismatch. Exit 2: invalid request, missing data, unsafe
path or Git failure. Exit 3: occupied local lock/stale predecessor/concurrent update.
No output verdict certifies code correctness, review quality or authority.

Snapshot creation reads only explicit pinned objects from the source repository.
It creates a temporary bare repository, imports those histories through local Git
transport and bundles that temporary repository. Source refs/worktree are not updated.
The bundle includes reachable ancestry, not LFS payloads or submodule repositories.
This can be large for an established repository; provision storage and review sensitive
historical content before creating/exporting it. The source must not be shallow.
The round's manifest is written once. Existing round paths are refused, even for the
same requested content; reuse its manifest instead. Interrupted private staging
folders may remain and require inspection before manual cleanup.

Review JSON is a compact scope/evidence index, not an exhaustive prose report. Store
a detailed findings report separately when useful. A valid schema does not prove the
agent actually inspected code or ran a check; review/test execution needs raw evidence.

The helper minimises external Git execution paths by disabling external diff/textconv,
replacement objects, lazy fetch and optional locks for inspection. It is not a sandbox
for a malicious repository, and no general Git wrapper can guarantee that. Inspect
untrusted repositories with OS isolation and restricted credentials.
