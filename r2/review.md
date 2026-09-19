# Full self-review — round r2

Scope: orientation, five ordered semantic propositions, tests, boundaries and aggregate.
Actor: Codex desktop/GPT-6. This is author self-review, not independent approval.
The fresh-context reviewer separately challenged the mutable candidate and rechecked r1.
Their concrete findings and gaps are recorded in discoveries.md and resolved or explicitly
bounded in r2. They did not approve this final revision or execute its canonical gates.

P0: ADR0005 acceptance is grounded in owner-approved PR5 and verified integrated main,
not inferred from code presence. Index and confirmation agree; ADR0006 remains proposed.
P1: literal loopback, proxy/redirect rejection, model identity and rendered context checks
precede generation. Byte bounds/deadline checks cover preflight, completion chunks and
EOF. Typed measurements preserve unknowns. Invalid/truncated/provider responses fail;
no reasoning escalation or retry is hidden. Network waiting limitation is explicit.
P2: domain types exclude MAF/provider imports; graph steps prepare/infer/validate.
Untrusted source is JSON data, upstream labels excluded. Exact unique quotes derive
character spans; schema success does not prove interpretation correctness. Framework
completion is distinct from provider/semantic failure. Prompt and raw successful reply
return for persistence; incomplete streams and catastrophic runtime evidence are limited.
P3: atomic claims and one-running constraint, per-root OS lock, ownership checks, short
transactions, heartbeat inspection and explicit interrupted failure avoid silent replay.
Model work is outside database transactions. Routing is persisted before invocation and
usage before job completion. Atomic immutable files precede database references; orphan
files and retained usage after later failure are documented and tested. SQL bodies contain
metadata, not prompts. Recovery assumes cooperating processes and a local filesystem.
P4: POST enqueues only; global Host and mutation Origin checks protect the local browser.
Escaped output, hash-verified result reads, bounded history and queued/running refresh
expose failures/provenance. Existing source-browser tests remain and use a valid local
test URL. Token counts remain unknown until provider completion. No annotation action
or misleading completed-slice claim is introduced.

Aggregate: composition stays behind existing Import Linter/Tach boundaries; no ignore or
contract weakening. MAF and transport dependencies are introduced at their own complete
checkpoints. The CLI worker and web share only external data-root state. Source records
remain unmodified, and model names remain configured data. Mainline ancestry contains
only the five semantic commits, never diary or archive history. Final equality covers
all tracked source/tests/docs/locks. No tests were retired or weakened for green checks.

Design clarity: interfaces hide provider transport, framework graph, queue transactions
and immutable publication. JobService's coordination is cohesive for this single slice;
no distributed queue or speculative actor abstraction was added. Security ownership is
now application-wide rather than repeated handler policy. No further material design
finding was established. No unsupported performance/model-quality conclusion is drawn.

Required Windows/Python3.12 checkpoint evidence is complete in verification-summary.json.
Runtime model/browser evidence is in live.json. Other operating systems were not executed;
POSIX lock implementation is not represented as verified. Hosted CI is not configured.
Remaining limitations: human annotation/progress and full VS1 completion remain outstanding;
single-user local runtime only; operator intervention for a hung worker; no model-quality
acceptance; unknown usage on incomplete calls; bounded I/O can return after elapsed deadline.
No unresolved code finding within the stated candidate contract. Owner review is pending.
