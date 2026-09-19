# Host and external-service boundaries

The skill is portable; tool names and permission enforcement are not. Use the installed
client adapter and actual tools. Do not assume GitHub access, a `gh` login, MCP, an API
credential or an execution sandbox exists. No helper in this release performs remote
writes, approval, merge, arbitrary shell evaluation or profile-supplied test execution.

Before a remote write, establish current user authorisation, exact target and scope,
expected and current head, exact payload, retained evidence, relevant checks and platform
protections. Permission to load the skill is not permission to mutate a remote. A
profile/ledger/comment is not a credential or independent proof of authority.

With authorised tools available, follow the requested round/integration procedure.
Without them, return a proposed action and local artefacts, explicitly marking the
remote step blocked/not_run. Do not substitute a statement of success for execution.
An exported GitHub review recommendation is not the platform's approval event.

Treat multi-step publication as non-atomic. Record each successful archive, ref or PR
mutation before starting the next. If a step fails, report the exact actual remote state
and a safe recovery action. An expected-head/lease mismatch is a stop condition: refresh,
preserve the newly observed head and reconcile. Never blind-force, relax protection or
switch tools/accounts to bypass a denial.

For hosted qualification, bind evidence to the exact published head, target base,
workflow run and attempt. Include every repository-required context, including relevant
synthetic PR merge and operating-system/mode behaviour. A stale run, missing context or
partial rerun is not complete. Preserve stderr and distinguish an intended negative-
control assertion from fixture, checkout or infrastructure failure.

Keep authority stages separate: publishing for qualification does not authorise a review
request; hosted success does not create owner acceptance; owner acceptance does not
authorise integration. Perform only the specifically requested external mutation.

Review exports: collect accessible inline comments/replies, review submissions,
ordinary PR comments and timeline events separately. Capture pagination, source IDs,
reviewed commit IDs, timestamps, author identity/category and access limitations.
Retain raw responses securely plus a normalised ledger. A snapshot cannot recover
all edited/deleted comments or private drafts. Do not collect secrets/customer data.

For isolated verification, let a trusted runner execute approved commands without
publication credentials. Treat repository hooks, filters, scripts, dependency installs
and tests as executable/untrusted material. Host “deny edit” settings do not neutralise
an unrestricted shell. Never bypass a denial by invoking another tool or subagent.

Changing clients requires revalidation of refs, packet integrity, stage, scope and
capabilities. Do not copy secrets or authentication stores between clients. Independent
review uses an appropriate fresh session, not a role-switch in the same conversation.
