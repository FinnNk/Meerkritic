# Review a pinned series

## Mode and identity

Default `full`; other modes: `next`, `commit <id-or-sha>`, `aggregate`, `boundaries`,
`tests`, `changes --from <round> --to <round>`. Record pair, round, semantic base/tip,
manifest hash, client/model/session and independence (self-review, fresh session or
external reviewer). A role change in an author session is still self-review.
Never edit source, rewrite history, post comments or issue platform approval here.
Reports may be written to an authorised external evidence store; otherwise return
report content for the integrator to save. Isolated test execution needs authority.

## Full trajectory

1. Read objective, governing contracts, assumptions, proposition map and base context.
   Challenge the author’s account of what matters. Verify the current round identity.
2. Review each semantic commit in dependency order, against its parent and declared
   proposition. Inspect implementation, relevant tests, unchanged callers and contracts.
   Do not assume a commit description or passing test proves a promise.
3. After each unit, record verified/unsupported claims, evidence, limits and findings.
   Carry forward concise contracts, not unexamined author conclusions. Reopen details
   when dependencies require it. Use log/show/blame/diary selectively; no obligatory
   full diary read. Later-code inspection is allowed but cannot validate an earlier
   checkpoint using code or tests absent from that checkpoint.
4. Inspect the aggregate base-to-tip result for composition, cross-cutting invariants,
   compatibility, operational risks and obligations omitted from the opening narrative.
5. Run or inspect risk-proportionate verification. Record checks not run and reasons.
   Review test replacements/retirements by their current contract obligations.
6. Report evidence-backed findings, severity, confidence and validation suggestions.
   Distinguish confirmed issues from hypotheses and design/boundary concerns. No quota
   of findings; “none found” is not correctness or platform approval.

## Scoped modes

- `next`: read the SHA-bound cursor, revalidate the round, perform minimal orientation
  and prior-contract rehydration, review the next unit. Append a new report; never
  advance a cursor on failure. Changing round invalidates automatic carry-forward.
- `commit`: include whole-change/prerequisite context, review only the specified unit;
  report that aggregate and remaining-unit coverage are outstanding.
- `aggregate`: final interactions only; do not claim prior local review happened.
- `boundaries`: load boundary-design.md; assess framing, evidence placement, forward
  obligations and excessive fragmentation. No code fixes or mechanical size verdicts.
- `tests`: load test-evidence.md; examine purpose, continuing obligations, replacements
  and availability at each checkpoint. Existing tests can suffice.
- `changes`: load review-rounds.md; compare exact old/new snapshots and bases, inspect
  affected propositions/dependencies and aggregate consequences. Record narrowly what
  was carried forward and why. Identical-looking patches do not auto-transfer approval.

## Output

Use assets/review-report.md and review.schema.json. For a complete `full` report,
orientation, every semantic commit and aggregate review must be recorded. The validator
checks identity/scope consistency only; factual review execution must be auditable.
Partial or blocked work stays partial. Do not silently copy old reviewed-SHA lists.

A supplied reviewer profile may deny edits yet ask before shell execution. That is
not an OS sandbox. Never use the shell to evade tool restrictions. If history access
is denied, request a bounded export and record the restriction rather than guessing.
