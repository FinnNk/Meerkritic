# Feedback, review rounds and publication

## Revise

1. Pin feedback to its round, commit/proposition and source thread. Preserve exact
   feedback as data. Assess acceptance/rejection/deferral under agreed decision rights; a later contradiction or new evidence may reopen or supersede an earlier disposition, which must be recorded append-only rather than overwritten;
   unresolved product/contract questions return to the responsible person. Do not
   invent a contract. Discussion-only decisions need not create source commits.
2. Apply authorised accepted changes chronologically to the diary. Record appropriate
   verification and test-disposition reasoning. Never backdate or erase discoveries.
   When repository policy and current authority cover a routine repair, preserve the
   failure and apply the repair diary-first without asking the owner to re-authorise
   the same scope.
3. Freeze the verified diary; update the boundary plan as needed. Reconstruct corrections
   into the propositions they complete; add a proposition only for a distinct obligation.
4. Verify checkpoints/tip and equivalence. Preserve old framing and map split/combined
   proposition identities. Do not automatically resume publishing from `revise`.

Stop and ask for direction when repair would choose a new contract, broaden scope or
authority, absorb an independent defect, or exceed agreed cost/delay bounds. Repair
authority never grants publication, review-request, force-update or integration
authority.

## Round prepare (local)

Keep an active published round stable while preparing the next. Archive every head
actually exposed, including exceptional direct edits, before replacing it. A direct
edit must be reconciled into the diary with its true provenance, never disguised.

The helper `snapshot` creates a local self-contained Git bundle and a manifest of
an equivalent frozen pair. This proves neither behavioural verification nor durable
remote retention. Review the reachable history for sensitive material before archiving.
Copy/replicate the bundle to the agreed durable store and verify access before publication.

Prepare: round ID, bases/tips/trees, verification records, proposition map, what-matters
account, changes since previous round, feedback/test-disposition mappings and limitations.
Keep review bookkeeping outside application trees. Return a locally-prepared/not-ready
assessment of each local gate and list outstanding hosted contexts. An archive can exist
while the revision is neither hosted-qualified nor ready for owner review.

## Compare revisions

Run `git range-diff OLD_BASE..OLD_TIP NEW_BASE..NEW_TIP` with immutable SHAs, retain
raw output and Git version. Matching is heuristic, not a machine integrity proof.
A tip-to-tip diff includes upstream changes when bases differ; explain those separately.
Re-review affected propositions and their dependencies plus aggregate consequences.
Narrow carry-forward requires a recorded scope; reconstructed series need explicit
final confirmation even if the final tree did not change.

## Round publish (remote; never implicit)

Load host-operations.md. This operation publishes an exact revision for qualification;
it does not automatically request owner review. Check specific authority for the exact
repo/PR/branch/update, local checkpoint and tip verification, equivalence, and accessible
retention of previous/new snapshots. Fetch and inspect the remote head, preserve it, and
use an explicit expected-SHA lease for an authorised rewrite. On mismatch, stop and
reconcile; never blind force.

Record every remote write as it succeeds. If a later archive, branch or PR step fails,
report the actual partial state and mark publication `partial`; the locally prepared
candidate remains the last completed stage. Never claim the multi-step publication was atomic.
Export accessible comments, reviews, replies and timeline records with paging/access
limits. A PR description or cached SHA is not an archive. Publication is neither hosted
qualification, owner-review readiness nor final approval.

## Hosted qualification

Qualify the complete repository-required hosted context set against the published exact
head and base. Record workflow, run ID, attempt, synthetic merge SHA where applicable,
individual job/context results and immutable log or artefact references. A rerun attempt
is a new result set: do not combine passing jobs from different attempts unless repository
policy explicitly defines that aggregation and the record makes it visible. After a
diagnosed infrastructure or flaky failure, a new complete attempt may establish hosted
qualification when repository policy permits and the root-cause disposition is retained;
the earlier failed attempt remains in the record. Never splice selected passing jobs from
different attempts into an apparently complete result.

A failure, missing job, skipped required context, stale head/base or partial rerun leaves
the revision unqualified. Preserve the attempt, return any repair through the diary, and
publish a new round when identities change.

## Owner-review readiness

Offer a revision for owner review only after it is locally prepared, published and fully
hosted-qualified, with routine defects resolved and limitations made explicit. Identify
the exact final head and review scope. Requesting review and platform approval remain
separate authorised actions; neither publication nor an agent recommendation supplies them.

## Stacks / base refresh

Every pair must use matching predecessor trees and exact predecessor round IDs. On
base refresh, preserve old diary generations and semantic rounds. Treat conflict
resolution as implementation work, verify it, then publish reviewed replacements.
Default to versioned semantic rounds. An agreed append-during-review variant may keep
feedback commits temporarily; curate and reapprove the final series before integration.
When rebasing changes commit SHAs, compare ordered proposition trees and record their
mapping. Do not transfer hosted check or approval status from old SHAs solely because
the resulting content is equivalent.
