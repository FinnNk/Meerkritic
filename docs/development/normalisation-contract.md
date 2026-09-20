# Interpretation contract

Normalisation proposes a structured interpretation of a supplied review comment
and code excerpt. This reference is for developers integrating or changing the
workflow; see [the task guide](normalisation.md) to run it.

## Responsibility boundaries

| Component | Owns | Does not own |
| --- | --- | --- |
| `WorkflowRunner` | Context preparation, orchestration and output validation | Durable storage or usage accounting |
| `ModelClient` | Provider transport, rendered prompt/token limits and telemetry | Whether evidence supports an interpretation |
| MAF adapter | Actual Microsoft Agent Framework graph and framework observations | Application/domain types |
| Application caller | Retain source identity, route, output and usage | Framework-specific message types |

The framework prepares context, calls the model and validates the response. Core
application/domain types do not depend on Microsoft Agent Framework (MAF).

## Evidence and interpretation rules

- Treat supplied source as untrusted data. Exclude upstream category labels from the prompt.
- Separate whether a concern is actionable from whether it might generalise.
  The schema permits `uncertain`; do not convert uncertainty into an affirmative finding.
- Require evidence for affirmative concerns. Each exact quote must occur uniquely
  in the supplied comment or code.
- Derive character spans on the host: zero-based Unicode indexes, including the
  start and excluding the end. For example, `[0, 3)` identifies the first three characters.
- Quoted-source checks establish where text came from, not the correctness of the
  interpretation. [Human annotation](annotations.md) records Accept/Edit/Reject separately.

## Outcomes and failures

Each outcome returns the prepared prompt/schema version, model output, available
raw provider request/response, measurements and a `FrameworkObservation`. The caller
must retain these with source/dataset identity and the saved route.

| Situation | Required treatment |
| --- | --- |
| Provider failure without a full response | Retain the prepared prompt and available measurements. |
| Partial stream | Do not claim a complete response; partial streams are not retained and usage may be unknown. |
| Invalid schema or evidence | Report a validation failure rather than accept an interpretation. |
| Unexpected runtime/storage exception | Report failure and disclose incomplete evidence. |
| Framework message carries a transport exception | Convert it to plain failure data: measurement and safe error text. |

The locked MAF core version is 1.19.0. Framework messages must use plain failure
data because transport exception objects do not support the required message
copying. Tests exercise the actual framework across provider, semantic and
framework failures; historical integration observations remain in their review records.
