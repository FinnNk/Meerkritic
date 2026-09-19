# Clean integration

## Check

`integrate check` inspects, but never merges. Confirm three independent gates:

1. Qualification: corresponding frozen pair equal; every required checkpoint/tip context
   passed for exact identities; archives retained; hosted qualification covers the exact
   final head, base and run attempt.
2. Owner review: curated propositions, feedback disposition and material test changes are
   explained; required acceptance and platform approval cover the exact final head/scope.
3. Integration: separate authority names the PR/revision/method; actual target/base and
   result are identified and checked. A merge queue's tested synthetic commit may differ
   from the eventual merge; record both and assess differences. Earlier PR-tree evidence
   is not final integration evidence.

Inspect the incoming commit list and ancestry, not only net content. No diary or
archive merge to preserve history. A content-preserving regrouping is still a visible
revision requiring checkpoint checks and final confirmation.

## Execute

Only when explicitly authorised for the exact PR/revision/merge method, with appropriate
client tools and credentials. Load host-operations.md. Repository protection, approval
and merge-queue policy take precedence; never change them to get a merge through.
Default recommendation: rebase-and-merge the final semantic series if allowed. Squash
is suitable when the whole PR is one logical mainline change; merge commits preserve
an explicit boundary. Neither is a new equivalence guarantee.

If the target advances or a conflict requires new content, follow the refreshed-round
path instead of quietly integrating unreviewed resolution. Re-run every context whose
tested source or target assumptions changed.

A semantic series rebased or regrouped before owner acceptance/integration has new
checkpoint identities and needs fresh checkpoint evidence, hosted qualification and
approval. When an already authorised integration itself creates new mainline SHAs, keep
the earlier checks/approval bound to the reviewed head: do not relabel the new SHAs as
having those statuses. Instead verify the ordered proposition-tree mapping and every
repository-required post-merge context. A mapping/content mismatch returns through a new
round. Record actual mainline commits; do not promise old SHAs survive rebase or squash.

## Record

`integrate record` records a merge already performed, verifying the actual remote/local
facts available; do not perform the merge itself. Retain final approval, checks, exact
integration base/result/tree, incoming mainline commits, proposition-to-mainline mapping,
ordered proposition tree comparisons, tested context and archive locations. Distinguish
the merge result from any earlier synthetic merge and record the exact post-merge checks.
Use [the integration-record template](../assets/integration-record.md) for a compact,
durable record. Missing facts remain unknown. Preserve archived review rounds after
deleting working branches only under an explicit retention/cleanup decision.

Return readiness, approval and actual integration status separately. A helper's
successful equivalence check is never authority or a replacement for review.
