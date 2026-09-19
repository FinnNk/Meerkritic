# Principles

This reference expands the software-design guidance used by the skill.

The material is written in original words and is inspired substantially by John Ousterhout's *A Philosophy of Software Design*. It operationalises those ideas for modern engineering and coding-agent workflows.

## 1. Complexity is the primary design cost

Complexity appears when a developer must know too much unrelated information, follow too many dependencies, remember too many special cases, or search too hard for important behaviour.

Two recurring causes are:

- **dependency** — a change requires knowledge of or changes to other parts of the system;
- **obscurity** — important information exists but is hard to discover.

A successful design reduces both.

Useful questions:

- How many concepts must a caller understand?
- How many modules must change together?
- Is important behaviour obvious from the interface?
- Does this change reduce or increase the amount of context a developer needs?

## 2. Prefer deep modules

A deep module provides substantial capability through a comparatively small interface.

A shallow module exposes nearly as much complexity as it hides.

Prefer:

```text
AgentRuntime
  start()
  resume()
  cancel()
```

over an interface that exposes every runtime detail to callers.

Depth is about information hiding, not lines of code.

## 3. Let information hiding drive boundaries

A strong boundary hides a design decision that is likely to vary.

Examples:

- inference engine;
- persistence format;
- agent runtime;
- repository execution mechanism;
- architecture renderer.

Callers should depend on stable concepts rather than implementation products.

## 4. Adjacent layers should differ in abstraction

A layer is valuable when it changes how the problem is represented.

A sequence such as:

```text
Controller → Service → Manager → Repository
```

is not automatically architecture if each layer simply forwards the same arguments.

Prefer boundaries where each layer reduces, transforms, or hides complexity.

## 5. Avoid pass-through methods and shallow wrappers

Pass-through methods create the appearance of encapsulation while preserving the same cognitive burden.

Ask:

> If this layer disappeared, would callers lose a useful abstraction or only a forwarding function?

## 6. Design errors out of existence

Prefer APIs and state models that make invalid combinations unrepresentable.

Examples:

- immutable rule versions once used by completed experiments;
- explicit job state transitions;
- typed outcomes rather than loosely related status flags.

The best error handling is often a design in which the error state cannot occur.

## 7. Expected outcomes should usually be explicit states

Examples such as:

- rule not applicable;
- job cancelled;
- user deferred a decision;
- agent made no change;

are normal domain outcomes, not exceptional failures.

Represent them explicitly.

Reserve exceptions for abnormal conditions.

## 8. Pull complexity downward

If complexity is unavoidable, place it in a lower-level module so every caller does not need to understand it.

For example, callers of a result store should not need to understand Parquet layout, DuckDB connection rules, and manifest conventions separately.

## 9. Avoid unnecessary configuration

Each configuration parameter exports an implementation decision to callers.

Ask:

> Is this genuinely something callers should decide, or should the module choose a sensible policy internally?

Flexibility has a complexity cost.

## 10. Prefer strategic programming

Tactical programming optimises for making the current task pass.

Strategic programming invests in a design that leaves future work simpler.

Coding agents are particularly good at tactical fixes, such as:

- one-off flags;
- special-case branches;
- local wrappers;
- duplicated paths.

Review agent-generated code for whether it leaves the system conceptually simpler.

## 11. Consistency reduces cognitive load

Use the same terms and lifecycle concepts consistently.

If every long-running activity is a `Job`, do not casually introduce `Task`, `Operation`, `Execution`, and `Process` for equivalent concepts.

Consistency reduces the number of ideas developers must hold simultaneously.

## 12. Comments should explain what code cannot

Useful comments explain:

- rationale;
- invariants;
- non-obvious constraints;
- rejected alternatives;
- assumptions.

Avoid comments that merely translate code into English.

## 13. Define important interfaces before implementation

Before implementing a significant abstraction, state:

- what it does;
- what it hides;
- what callers may rely on;
- what callers must not need to know.

Writing this first often exposes shallow or leaky designs before they become code.

## 14. General-purpose interfaces can be simpler

A slightly more general abstraction can sometimes be simpler than several task-specific ones.

However, avoid speculative frameworks.

Generality should emerge around concepts already proven to recur.

## 15. Design quality is distinct from dependency legality

Static architecture tools can answer:

> Is this dependency allowed?

They cannot fully answer:

> Is this abstraction good?

Both checks are needed.
