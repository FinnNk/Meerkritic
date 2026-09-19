# Routing batch setup

Classification: material, assessed 2026-09-19 before implementation. Hard triggers: privacy/locality selection contract; versioned routing and usage provenance; persistent schema. Host policy: research-pack/11_DOUBLE_ENTRY_REVIEW_INTEGRATION.md. Reassess on scope growth. No EDR: implementing prescribed requirements, not selecting models using comparative evidence.

Base: 2a7b118042c087dc0ed58f7068bee7f1433c64c0. Pair vs1-routing, round r1; diary change/vs1-routing-diary in extras/der-checkouts/vs1-routing. One integrator: Codex desktop, GPT-6, session meerkritic-vs1-routing-2026-09-19 (CLI version not exposed). Pinned DER alpha.2, method revision 7, guidance revision 3. Canonical evidence: extras/der-evidence, outside application worktrees. Owner authorised continuing build, App publication and owner-only merge. No approval/merge claimed.

Required context: Windows/Python 3.12 with checkpoint-owned uv environment and locked dependencies; canonical tools/check.py, architecture before/after/delta, tests for privacy, configuration, pricing, migration/transaction/idempotence and CLI. No hosted CI required. No Git mode changes. No live inference in this batch; availability and model quality remain unverified. Snapshot/helper preflight uses owned isolated clone because the original repo has mixed Windows ownership.

Baseline attempt encountered the host Temp ACL and incomplete dependency installation (baseline-checks.log). Retried with the already approved extras/der-tmp directory, preserving the failure; see baseline-checks-retry.log. This is infrastructure setup, not a failed application assertion.

Design-clarity answers:

- Router: select a model from versioned configuration and explicit task requirements. Hide filtering, override precedence and reason construction; callers rely on fail-closed eligibility and immutable decision provenance, and need not know model names or provider APIs. One router is clearer than repeating privacy checks in each workflow.
- Usage accounting: validate reported tokens/times and estimate spend using a retained price version. Hide accounting rules and unknown-versus-zero distinctions; callers supply observations, not pricing arithmetic. No cost-based model choice is claimed.
- Routing journal: atomically retain the configuration and decision before execution, then retain completed usage and events. Hide SQL and immutable identity checks. Keep small metadata in SQLite; no prompts, datasets or artefact bodies. A simple journal is sufficient; no event-sourced application or generic persistence framework.

Provisional propositions: (1) eligible selection with complete override/privacy tests and docs; (2) usage/failure accounting with versioned pricing and tests/docs; (3) durable decision/usage journal and route inspection CLI with migration/restart/idempotence tests/docs. Reassess from the frozen result. One combined commit would mix independently reviewable pure selection, accounting and storage guarantees; splitting by models/tests/docs would create incomplete checkpoints. Keep related propositions in one PR. No independent reviewer was invoked; final review will be labelled self-review.

Compatible extension points: explicit provider health, budget input, context strategy and escalation link now; policy transitions/handoffs can later add immutable records without rewriting decisions. No speculative orchestration or automatic switching.
