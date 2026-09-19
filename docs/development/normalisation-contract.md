# Normalisation contract

The normalisation workflow turns a supplied comment and code excerpt into a proposed issue
interpretation. The real Microsoft Agent Framework (MAF) graph prepares context,
calls the model and validates output. Application/domain types never depend on MAF.
`WorkflowRunner` hides orchestration; `ModelClient` hides transport, rendered token
budgets and provider telemetry. The provider does not decide whether evidence supports
an interpretation. These are separate failure and review boundaries.

The prompt treats source as untrusted data and excludes upstream category labels.
The schema separates actionable concern from generalisability and permits `uncertain`.
Affirmative concerns require evidence. Exact quotes must occur uniquely in the supplied
comment or code; the host derives zero-based, half-open Unicode character spans.
This proves where quoted text came from, not whether the model's judgement is correct.
No rule is accepted automatically. Accept/Edit/Reject is a subsequent VS1 batch.

Each workflow outcome returns the prepared prompt/schema version, model output,
raw provider request/response where available, measurements and a `FrameworkObservation`.
Its caller must retain these alongside source/dataset identity and the persisted route.
The workflow itself does not own durable storage or usage accounting. Provider failures
retain the prepared prompt even when no complete response exists. Partial streams are
not retained; their usage may be unknown. Unexpected runtime/storage exceptions can
leave incomplete evidence and are reported as failures, never fabricated success.

MAF core 1.19.0 is pinned. Its workflow messages must carry plain failure data:
transport exception objects failed message copying in the initial integration test.
The adapter translates these objects into a measurement and safe error string. Tests
exercise the actual framework, including provider, semantic and framework failures.
