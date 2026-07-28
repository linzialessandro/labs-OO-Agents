# Scope of `nooa.formal` (this contribution)

## What this is

An **optional, opt-in** helper package. Import explicitly:

```python
from nooa.formal import method_boundary_contract
```

**Primary deliverable:** method-boundary residual contracts — attach residual
checks to `CodeActConfig(postconditions=...)` with `InvariantError` retry.
See [`APPLICATION.md`](APPLICATION.md).

## What this is not

- Not re-exported from top-level `nooa.__all__`
- Not a change to default CodeAct/Predict when unused
- Not a security boundary or sandbox proof
- Not a large formal-theory framework (optional local notes may exist outside this PR)

## Production attachment

| Helper | Harness |
|--------|---------|
| `method_boundary_contract(...).postconditions()` | `CodeActConfig(postconditions=...)` |
| Failure | `InvariantError` → CodeAct validation-retry |

## Related issue

https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41
