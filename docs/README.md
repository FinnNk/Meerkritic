# Documentation

Start with [browsing the sample](../README.md#browse-the-sample). These guides describe
how to use the code in this checkout. The [glossary](../CONTEXT.md) explains project terms.

## Use the application

| Goal | Read |
| --- | --- |
| Understand the public sample and recover dataset files | [Datasets](development/datasets.md) |
| Start a local model server | [Local inference setup](development/local-inference.md) |
| Ask a model to interpret a review comment | [Normalisation](development/normalisation.md) |
| Understand assessment fields | [Field meanings and worked steps](development/assessment-fields.md) |
| Read original formatting without changing model evidence | [Preserved source views](development/preserved-source.md) |
| Edit an assessment without JSON | [Assessment form](development/assessment-form.md) |
| Review and correct interpretations | [Annotations](development/annotations.md) |
| Choose a fixed set of reviewed inputs | [Selections](development/selections.md) |
| Group concerns and inspect their sources | [Discovery](development/discovery.md) |
| Propose, challenge and revise rules | [Candidate rules](development/rules.md) |
| Save decisions or send selected discussion for advice | [Research interaction](development/research-interaction.md) |
| Prepare and human-review inputs for a grouping study | [Study preparation](development/study-preparation.md) |
| Run the registered methods, rate masked groups and reproduce the report | [Study comparison](development/study-comparison.md) |

## Operate and inspect

| Goal | Read |
| --- | --- |
| Inspect model selection or export usage | [Routing commands](development/routing-operations.md) |
| Inspect logs, stored outputs and change-review references | [Operational evidence](development/operational-evidence.md) |
| Compare architecture and recognise stale views | [Architecture evidence](architecture/README.md) |
| Check an installation from input to reviewed result | [Workflow verification](development/verification.md) |

## Develop and review

- [Development workflow](development/README.md), [repository boundaries](development/structure.md)
  and [test guide](../tests/README.md).
- [Writing documentation](development/documentation-style.md),
  [Python style](development/python-style.md) and [code comments](development/code-comments.md).
- [Screenshot capture notes and demonstration setup](images/README.md).
- [Routing reference](development/routing.md) and
  [interpretation contract](development/normalisation-contract.md).
- [Milestone review method](development/milestone-review.md).

## Decisions, plans and history

These records serve different purposes from current operating instructions:

- [Architecture decisions](adr/README.md) explain consequential design choices.
- [Empirical decisions](edr/README.md) retain hypotheses, methods, results and choices.
- [Implementation backlog](../IMPLEMENTATION_BACKLOG.yaml) and [slice reviews](slice-reviews/README.md)
  describe delivery status and evidence.
- [Original research](research/README.md) and [source attribution](sources.md)
  preserve the supplied material and its provenance.
