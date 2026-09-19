# Software Design Clarity Skill Integration

This project consumes the independent **`software-design-clarity`** skill.

The skill is intentionally maintained outside this project so it can be shared and published independently.

## Role in this project

```text
Ruff
    code conventions

Import Linter + Tach
    dependency/module architecture enforcement

software-design-clarity
    abstraction/design quality
```

Use the skill for:

- significant module/API design;
- new architectural boundaries;
- substantial refactoring;
- review of agent-generated structural changes;
- slice-level design review.

The project-specific trigger points and acceptance rules are recorded in `06_IMPLEMENTATION_HANDOVER.md` and `IMPLEMENTATION_BACKLOG.yaml`.

The skill package contains the fuller Ousterhout-inspired summary requested for both humans and coding agents, plus compact operational instructions, review questions, examples, and a design-review template.
