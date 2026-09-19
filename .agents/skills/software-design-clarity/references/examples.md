# Examples

## Deep versus shallow module

### Shallow

```python
class AgentService:
    def start(
        self,
        provider,
        worktree,
        checkpoint_store,
        transcript_store,
        timeout,
        permissions,
        retry_policy,
    ):
        ...
```

The caller must understand most runtime details.

### Deeper

```python
class AgentRuntime:
    def start(self, spec: AgentSpec) -> AgentRunId:
        ...
```

Runtime policy and provider details remain behind the module boundary.

---

## Pass-through layering

### Weak

```text
Controller
  → Service
    → Manager
      → Repository
```

If every layer exposes `get_rule(id)`, little complexity is hidden.

### Better

```text
Web/UI
  → application operation
    → domain model
      → persistence adapter
```

Each boundary changes the level of abstraction.

---

## Configuration leakage

### Weak

```python
Worker(
    poll_interval=2,
    heartbeat_interval=5,
    stale_timeout=30,
    kill_timeout=10,
    flush_interval=1,
)
```

### Better

```python
Worker()
```

or, where real policies exist:

```python
Worker(policy=INTERACTIVE_LOCAL_WORKER)
```

---

## Normal outcome versus exception

### Weak

```python
try:
    detector.evaluate(code)
except RuleNotApplicable:
    ...
```

### Better

```python
result = detector.evaluate(code)

if result.applicability == "not_applicable":
    ...
```

---

## Useful comment

### Weak

```python
# Increment retry count.
retry_count += 1
```

### Useful

```python
# Retries create a new attempt rather than mutating the old one so
# experiment provenance remains immutable.
```

---

## Strategic versus tactical change

### Tactical

Add a boolean flag to bypass an architectural constraint for one caller.

### Strategic

Clarify the underlying boundary so the caller's legitimate use case is represented directly without a bypass.
