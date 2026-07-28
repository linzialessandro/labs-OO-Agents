# Concrete application: method-boundary residual contracts

## Problem (for a NOOA author)

Return types catch shape (`str`, `TaskResult`, Pydantic models). They do **not**
catch residual process obligations the paper and ARC already need, e.g.:

- “WAIT is only legal if a submission exists for this turn”
- “summary must mention the user’s shipping complaint”
- “`evidence` must be non-empty even if the model type-checks”

NOOA already has the channel: `CodeActConfig(postconditions=[...])` +
`InvariantError` → validation-retry. Hand-writing every checker is boilerplate.

## Solution (shipped)

```python
from nooa.config import CodeActConfig
from nooa.formal import method_boundary_contract
from nooa.strategies import CodeActStrategy
from nooa import Agent, strategy

contract = method_boundary_contract(
    str,
    result_predicate=lambda s: "shipping" in s.lower(),
    result_message="result must mention shipping for this task",
)

class FeedbackAgent(Agent, llm=llm):
    @strategy(CodeActStrategy(config=CodeActConfig(
        postconditions=contract.postconditions(),
    )))
    async def analyze(self, text: str) -> str:
        """Analyze feedback."""
        ...
```

Or shorthand:

```python
from nooa.formal import method_boundary_postconditions

cfg = CodeActConfig(postconditions=method_boundary_postconditions(
    str,
    result_predicate=...,
    agent_fields={"ready": lambda v: v is True},
    field_messages={"ready": "set agent.ready before return"},
))
```

## What you get

| Behavior | How |
|----------|-----|
| Residual fails | `InvariantError` with your message |
| CodeAct | Same-loop retry (model sees the error event) |
| Type re-check | Optional `return_type=` (aligned with method annotation) |
| Live agent state | `agent_fields={name: predicate}` (ARC-style) |
| Default runtime | Unchanged until you attach the config |

## Introspection (optional)

```python
contract.describe()  # name, enforcement path, residual flags
```

## Offline demo

```bash
uv run python examples/formal/01_contracts_and_invariants.py
uv run pytest tests/formal/test_application.py -q
```

Related: https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41
