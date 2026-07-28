# Residual-contract example

**Opt-in helper:** `method_boundary_contract` on CodeAct postconditions
(`InvariantError` → retry). Offline FakeLLM.

```bash
uv run python examples/formal/01_contracts_and_invariants.py
uv run pytest tests/formal/test_application.py -q
```

- How-to: [`APPLICATION.md`](../../src/nooa/formal/APPLICATION.md)
- Issue: https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41
