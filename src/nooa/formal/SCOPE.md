# Scope of `nooa.formal` (this contribution)

## What this is

An **optional, opt-in** helper package. Import explicitly:

```python
from nooa.formal import method_boundary_contract
# or: from nooa.formal.application import method_boundary_contract
```

**Primary deliverable:** method-boundary residual contracts — attach residual
checks to `CodeActConfig(postconditions=...)` with `InvariantError` retry.
See [`APPLICATION.md`](APPLICATION.md).

**Public surface:** `MethodBoundaryContract`, `method_boundary_contract`,
`method_boundary_postconditions` (via `nooa.formal` / `nooa.formal.application`).

**Private support:** `model_theory.py` compiles residuals into postcondition
callables. Not a stable public API; do not re-export from package `__init__`.

## What this is not

- Not re-exported from top-level `nooa.__all__`
- Not a change to default CodeAct/Predict when unused
- Not a security boundary or sandbox proof
- Not a large formal-theory framework (CT/MT catalogs, articles stay out of this PR)

## Production attachment

| Helper | Harness |
|--------|---------|
| `method_boundary_contract(...).postconditions()` | `CodeActConfig(postconditions=...)` |
| Failure | `InvariantError` → CodeAct validation-retry |

## Related issue

https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41
