---
name: software-design-clarity
description: >
  Review or design software with a complexity-first lens inspired substantially
  by John Ousterhout's A Philosophy of Software Design. Use for architecture,
  API/module design, refactoring, PR review, and agent-generated code where the
  main question is whether the design reduces or increases cognitive burden.
license: MIT
---

# Software Design Clarity

Use this skill when a task involves a meaningful software-design decision, architectural boundary, abstraction, refactor, or review of agent-generated code.

The skill is **advisory**. Do not manufacture abstractions merely to satisfy it.

## Core objective

Evaluate a design primarily by the complexity it imposes on future developers:

- dependencies they must understand;
- information they must discover;
- special cases they must remember;
- implementation details that leak across boundaries.

Prefer the design that reduces total cognitive burden.

## Core principles

1. Prefer deep modules with small interfaces.
2. Hide volatile design decisions behind module boundaries.
3. Ensure adjacent layers provide meaningfully different abstractions.
4. Avoid pass-through wrappers and shallow modules.
5. Pull unavoidable complexity downward.
6. Design invalid states out where practical.
7. Treat expected outcomes as states/results, not exceptional control flow.
8. Avoid exposing configuration that callers do not genuinely need to choose.
9. Prefer strategic simplification over tactical fixes.
10. Keep terminology and recurring patterns consistent.
11. Use comments for rationale, invariants, and non-obvious constraints.
12. For important abstractions, define the interface/contract before implementation.

## Modes

### Design mode

Use before implementing a significant abstraction.

Ask:

- What complexity will this module hide?
- What design decision is being encapsulated?
- What must callers know?
- What should callers *not* know?
- Is the interface smaller than the complexity behind it?
- Can invalid states be made impossible?
- Is each exposed configuration parameter genuinely a caller decision?

### Review mode

Use on an implementation or PR.

Look especially for:

- shallow wrappers;
- pass-through methods;
- duplicated concepts;
- accidental knowledge crossing boundaries;
- tactical flags or one-off special cases;
- unnecessary configuration;
- expected outcomes implemented as exceptions;
- comments that merely restate code;
- layers that forward calls without changing abstraction level.

### Refactoring mode

Use when code works but accumulated complexity is the concern.

Prioritise the few changes that most reduce conceptual burden.

Do not generate a long catalogue of low-value style issues.

## Required review output

When using this skill in review mode, structure the result around:

1. **Complexity introduced or removed**
2. **Module depth**
3. **Knowledge/dependency leakage**
4. **Layer quality**
5. **Tactical special cases**
6. **Highest-leverage simplifications**

If no material design issue exists, say so plainly.

## Guardrails

Do not:

- split modules merely because they are large;
- create indirection merely to create layers;
- add interfaces for speculative future flexibility;
- expose implementation knobs "just in case";
- recommend abstraction when a simpler direct implementation is clearer;
- treat these heuristics as inviolable laws.

Prefer simplicity over ritual.

For fuller explanations and examples, consult:

- `references/principles.md`
- `references/design-smells.md`
- `references/review-questions.md`
- `references/examples.md`
- `references/bibliography.md`
