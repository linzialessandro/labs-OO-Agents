# Follow-up after the residual-contract issue

**Shipped intent:** `method_boundary_contract` /
`method_boundary_postconditions` on CodeAct `postconditions` + `InvariantError`.

**Public API only:** those three names via `nooa.formal` /
`nooa.formal.application`. `model_theory` is private support.

## Process rules

| Step | Rule |
|------|------|
| Issue | #41 already open — **do not bump** until maintainers reply |
| Watch | `gh issue view 41 --repo NVIDIA-NeMo/labs-OO-Agents` (passive) |
| PR | Only after positive maintainer signal; `git commit -s` + `🤖🤖🤖` if agent-authored |
| DCO | Every commit: `git commit -s` |

Do **not** open a PR until welcome (comment, label, or explicit “please send a PR”).

## Decision tree

```text
Maintainer reply
├── "Looks good / send a PR"
│     → PR-APP: application-first public API + private model_theory support
│       + APPLICATION.md + SCOPE.md + test_application + example
├── "Move next to strategy_validation"
│     → same API, different package path
├── "Docs-only"
│     → APPLICATION.md + example as pattern; no package if they prefer
├── "Expand residuals" (WAIT templates, etc.)
│     → new small factory; separate issue if large
├── "Not wanted"
│     → close; keep local pattern
└── Silence (after private ~14–21 day reassess)
      → archive & stop; no polite bump; no PR-as-bump
```

## PR-APP scope (when welcomed)

**Include:**

- `src/nooa/formal/application.py`
- `src/nooa/formal/model_theory.py` (**private support**, not public re-exports)
- thin `src/nooa/formal/__init__.py` (application API only)
- `APPLICATION.md`, `SCOPE.md`
- `tests/formal/test_application.py`
- `examples/formal/`

**Exclude:** CT/MT dual-lens catalogs, LEARNING/perspectives stacks, article,
any untracked formal experiments.

## Recorded issue

**Opened:** https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41

Details: `docs/formal/OPENED_ISSUE.md`.
