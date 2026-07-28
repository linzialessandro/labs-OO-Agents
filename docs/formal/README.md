# Formal contribution pack

## Concrete application (lead with this)

**Method-boundary residual contracts** → existing CodeAct postcondition /
`InvariantError` retry channel.

- How-to: [`APPLICATION.md`](../../src/nooa/formal/APPLICATION.md)
- **Public API:** `from nooa.formal import method_boundary_contract`
- Demo: `examples/formal/01_contracts_and_invariants.py`
- Tests: `tests/formal/test_application.py`
- Scope: [`SCOPE.md`](../../src/nooa/formal/SCOPE.md)

`model_theory.py` is **private support** for residual compilation — not package
public API.

Personal theory notes / article (if present under `article/`) stay **out of the
PR** and are not required reading for maintainers.

## Issue / follow-up

| Doc | Purpose |
|-----|---------|
| **[#41](https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41)** | Opened feature issue (residual contracts) |
| [OPENED_ISSUE.md](OPENED_ISSUE.md) | URL + later `gh pr` recipe |
| [ISSUE_DRAFT.md](ISSUE_DRAFT.md) | Body used for create |
| [FOLLOWUP.md](FOLLOWUP.md) | Hard silence until welcome → PR-APP scope |

```bash
uv run pytest tests/formal/test_application.py -q
uv run python examples/formal/01_contracts_and_invariants.py
```
