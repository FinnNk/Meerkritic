# Review Questions

Use a subset relevant to the change.

## Complexity

- Did this change make the system conceptually simpler or more complex?
- What new concepts must a future developer understand?
- Were any old concepts eliminated?

## Module depth

- Does each new module hide substantial complexity?
- Is its public interface smaller and simpler than its implementation?
- Could the caller remain unchanged if the hidden implementation changes?

## Dependencies

- Did callers gain knowledge of implementation details?
- Does one design decision now appear in multiple modules?
- Are dependencies enforced by the right boundary?

## Layers

- Does each layer provide a genuinely different abstraction?
- Are there pass-through methods?
- Would deleting a layer materially worsen the abstraction?

## State and errors

- Can invalid states be made impossible?
- Are normal outcomes represented explicitly rather than with exceptions?
- Are state transitions understandable and constrained?

## Configuration

- Does every new configuration option represent a real caller choice?
- Could a sensible internal policy remove configuration?

## Strategic quality

- Is this a durable simplification or a tactical fix?
- Did the change create a special case?
- Is new complexity justified by meaningful capability?

## Vocabulary

- Are existing concepts reused consistently?
- Did the change introduce synonyms for an existing idea?
- Does the shared glossary need updating?

## Comments

- Do comments explain rationale/invariants rather than restate code?
- Are non-obvious constraints discoverable where callers need them?

## Agent-generated changes

- Did the agent optimise only for passing tests?
- Did it introduce unnecessary wrappers, flags, helpers, or configuration?
- Is there a simpler design with fewer concepts?
