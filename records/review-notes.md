# VS1 operational validation review

Material evidence/persistence change, explicitly authorised as PR #7's dependent
stack batch. Base 843ff161d49e096d1da2a55cacf75acac03e97f3 is the exact reviewed
annotation candidate. One canonical diary and history integrator; no owner merge.

Full integrator self-review covers each proposition and their aggregate. A
fresh-context source/boundary challenge reviewed catalogue/log publication and
the external-reference index, without running tests or giving platform approval.

VR-01: log catalogue writes/checksum verification could throw after an authoritative
job transition committed. Diagnostic exports now warn for filesystem, SQLite and
integrity errors, leaving explicit inspection strict. Tests cover each class.
VR-02: INSERT OR IGNORE could conceal a conflicting absolute catalogue path.
Publication now compares existing identity metadata and rejects conflicts.
Runtime relocation is explicitly outside the current contract. Tests additionally
retain an orphan file after failed edit indexing and interleave old/new log exports
to prove the latest pointer cannot regress. No tests/architecture contracts weakened.

Frozen proposition plan:

1. P1 catalogue and structured lifecycle-log snapshots. Complete file first,
   immutable metadata second, accepted result reference last. Logs derive from
   committed events, with immutable history and monotonic latest pointer. Own tests,
   migration, CLI and operational documentation at this checkpoint.
2. P2 external DER reference index and read-only harness view. Bind explicit
   pair/round/heads/event sequence, retain file hashes, detect changed/unavailable
   evidence. Never imply ledger/bundle qualification or owner acceptance. Own tests.
3. P3 reserve policy-transition and structured-handoff schemas required by the
   VS1 backlog. Independent routing-only contract, no switching/runtime persistence.
4. P4 aggregate data-to-annotation verification and operational reproduction guide.
   Uses the established contracts; does not supply missing P1/P2 correctness tests.

The initial three-proposition sketch gained P3 when the final audit found that
continuity paths had been documented but their explicitly required schemas were
not yet reserved. This scope change remains material. Alternative: separate the
catalogue and logs. Current log metadata depends directly on atomic publication;
a further split would add overhead without removing much shared knowledge. Revisit
if independent log recovery/retention policies grow. P2 remains independently assessable.

Design clarity: meaningful file/index and query ports; no source/framework leakage
into core logic, no forwarding-only facade or new service. Diagnostics are explicitly
secondary to committed state. The index remains a reference cache, not another
evidence store. Reserved schemas do not add unused execution configuration.

Development live check: fresh pinned 1030-record public dataset; three real local
llama.cpp/MAF successes, Accept/Edit/Reject with test-only notes, one actual closed-port
provider failure and one interrupted claimed job recovered without replay. WAL,
three annotation events, source coverage 1, result decisions 3, usage export and
DuckDB aggregate verified. Method/output identities retained in live.py/live.json.
Repeat against the exact frozen semantic checkpoint before publication; keep both.

Limits: Windows/Python3.12 only, pinned local GPU fixture, no model-quality inference,
no billed hosted call, no hosted CI. Local runtime and canonical DER paths are not
portable without migration/re-indexing. Full owner acceptance/integration pending.
