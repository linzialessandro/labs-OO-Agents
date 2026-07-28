# Paste-ready / gh issue body — residual contracts only

Automated agents: title and body must include **🤖🤖🤖** (CONTRIBUTING).

---

## Title (for `gh issue create`)

```
[Feature] Opt-in method-boundary residual contracts for CodeAct postconditions 🤖🤖🤖
```

## Body

**What problem are you trying to solve?**

NOOA already validates return types and supports
`CodeActConfig(postconditions=[...])` with `InvariantError` → model-correctable
retry (same channel as ARC WAIT-requires-submission).

Authors still re-implement residual checks by hand when the return *type*
is not enough, e.g.:

- result text must mention task-critical content (`-> str` is not enough)
- live agent state must match the declared outcome (e.g. “WAIT only if submitted”)
- structured fields like `evidence` must be non-empty even when the model type-checks

**Proposed solution**

An **opt-in** helper that compiles residual obligations onto the existing
postcondition channel (no default CodeAct change when unused):

```python
from nooa.config import CodeActConfig
from nooa.formal.application import method_boundary_contract
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

Also supports live agent state:

```python
method_boundary_contract(
    str,
    agent_fields={"ready": lambda v: v is True},
    field_messages={"ready": "set agent.ready before return_result"},
)
```

**Behavior:** residual failure → `InvariantError` with the author message →
CodeAct validation-retry. Success returns the validated value.

**Not re-exported** from top-level `import nooa`.

**How to try offline (no API key):**

```bash
uv sync --group dev
uv run pytest tests/formal/test_application.py -q
uv run python examples/formal/01_contracts_and_invariants.py
```

Author how-to: `src/nooa/formal/APPLICATION.md`  
Follow-up after reply: `docs/formal/FOLLOWUP.md`

**Non-goals**

- No change to default CodeAct/Predict when postconditions are not set
- Not a security boundary or sandbox proof
- Not a large formal-theory package as the deliverable (optional docs may exist separately)
- Not rewriting the ARC solver (motivation only)

**Alternatives considered**

1. Docs-only snippets — untested, easy to drift from the harness.
2. Only Pydantic return types — cannot express live-agent residuals.
3. Core harness change — unnecessary; the channel already exists.

**Open questions for maintainers**

1. Prefer `nooa.formal.application` vs a smaller home next to `strategy_validation`?
2. Welcome a focused PR with just this helper + tests + example?

**Checklist for a follow-up PR (if welcomed)**

- [ ] DCO: `git commit -s`
- [ ] Offline tests green
- [ ] No formal symbols on `nooa.__all__`
- [ ] 🤖🤖🤖 on PR title / agent commits / comments

🤖🤖🤖
