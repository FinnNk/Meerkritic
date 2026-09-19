# Design and root-cause review

Apply this lens alongside the existing contract and test review, not instead of it. A well-explained series can still leave an unnecessarily complicated system. Passing tests establish their asserted observations; they do not settle whether responsibility sits in the right place.

## Before adding a fix

For a consequential change, identify the governing requirement or invariant, the mechanism producing the problem, the component that owns the rule, and any existing implementation. Inspect relevant unchanged consumers. Distinguish intended behaviour from a historical accident that a test happens to preserve.

When the choice matters, compare a local patch with an alternative that resolves the cause at its owner. Which knowledge must callers retain? Where would the next change to this rule need coordinated edits? Does the change remove an obligation, move it behind a useful contract, or add another way to express it? Prefer the smallest coherent change that resolves the obligation without unnecessary lasting complexity; it need not be the smallest diff.

Examples:

- Two entry points repair the same invalid state differently. Before adding a third repair, check whether the shared state owner can enforce the invariant. Do not generalise two genuinely different policies just because their current code looks alike.
- A new fallback makes one request succeed but hides an invalid configuration. Check the intended failure contract before retaining silent recovery as a permanent second execution path.
- A necessary compatibility bridge may temporarily accept two representations. State the intended end-state and removal condition; do not remove compatibility merely to improve a metric.

Do not turn each fix into a redesign. Where resolving the cause exceeds the agreed scope, expose the trade-off and seek the needed decision. A legitimate bounded mitigation should name the residual cause, risk, owner and a concrete revisit or retirement trigger. Do not describe it as eliminating the cause.

## Review the resulting design

Look for material maintenance consequences: duplicated rule ownership, growing special-case branches or flags, caller-side compensation, leaked representation details, and added public interfaces that distribute rather than hide complexity. Large cohesive modules and short helpers are neither good nor bad by size alone. A split is useful when it improves responsibility and the knowledge needed to use a contract, not when it merely relocates lines.

A design concern can warrant action without a failing test. Ground it in the changed code and relevant consumers, the governing intent, a likely maintenance consequence and a proportionate alternative. Distinguish a present correctness defect, an evidence-backed design concern, a boundary concern, a preference and an untested hypothesis. Do not relabel all maintainability concerns as style, or invent findings to satisfy a quota.

For the final aggregate review, revisit responsibilities and interactions across the series: has a clear local change introduced duplicate mechanisms or coordinated obligations elsewhere? Keep the author's rationale open to challenge. A fresh reviewer should assess the contracts and evidence, not merely affirm the proposed story.

Tests remain essential evidence for supported behaviour, including refactors and transitional contracts. Keep the existing test-retention, checkpoint-isolation and negative-control requirements. This guidance prescribes no test-writing order and makes no claim about which development tradition caused a particular design.
## Optional external design skill

This bundled guidance is sufficient on its own. When the host has installed a compatible
software-design review skill (for example `software-design-clarity`), it may invoke that
skill for consequential design work and retain its output as additional review evidence.
Do not make external skill availability a DER readiness requirement unless repository
policy explicitly does so.
