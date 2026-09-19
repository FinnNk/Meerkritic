# Discoveries and dispositions

- MAF dependency resolution initially failed offline because msgspec was not cached;
  pinned dependencies were then fetched. Windows cache/evidence ACLs required elevated
  authorised execution. Git ownership was handled by an object-identical owned mirror,
  not a global trust exemption. One mistyped verification SHA failed before checkout;
  the corrected exact SHA was verified. Ruff line-length/import failures were repaired.
- Initial real MAF provider-failure test became a framework failure when an exception
  instance travelled through workflow message copying. Plain measurement/error data
  fixed it. The original failing log remains in r1. No framework removal was proposed.
- Fresh-context review found post-line stream limits and missing read-side Host checks.
  Raw chunks are now bounded and all routes have Host checks; regression tests pass.
- Review requested process death, publication/final-write failure and job-level failure
  provenance evidence. These were added before the first semantic freeze.
- First reconstructed candidate passed all checkpoints but self-review extended bounded
  response reading to preflight. Superseded-candidate.bundle and its logs are retained.
- R1's frozen revised candidate passed 71 tests; scoped reviewer recheck found EOF could
  arrive after deadline and still report success. R2 applies a final deadline check and
  regression test. Documentation accurately limits the guarantee: a blocked synchronous
  read can return after the elapsed deadline, bounded by the per-request I/O timeout;
  late completion is refused. Hard real-time cancellation is not claimed or required.
- Source record 2 produced exact quotes with unsupported semantic extrapolation. This is
  retained as model-quality limitation, not silently tuned away or treated as a bake-off.
  A comparative model/prompt quality decision would need a pre-registered EDR.
- All content changes went through the diary. Earlier evidence and r1 snapshots remain
  immutable. R2 reruns every exact checkpoint; no earlier green result is carried forward.
