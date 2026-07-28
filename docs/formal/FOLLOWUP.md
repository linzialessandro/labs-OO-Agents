# Follow-up after the residual-contract issue

**Shipped intent:** `method_boundary_contract` /
`method_boundary_postconditions` on CodeAct `postconditions` + `InvariantError`.

## Can we automate with `gh`? (yes)

| Step | Command / rule |
|------|----------------|
| Open issue | `gh issue create --repo NVIDIA-NeMo/labs-OO-Agents ...` (done in this goal if auth allows) |
| Watch for welcome | `gh issue view N --repo ...` / `gh api` comments & labels |
| Open PR later | only after positive maintainer signal; branch + `git commit -s` + `gh pr create` |
| Agent rule | Every issue/PR title, commit message, and bot comment ends with **🤖🤖🤖** or CONTRIBUTING says it is closed without review |
| DCO | Every commit: `git commit -s` |

Do **not** open a PR immediately after issue create — wait for welcome
(comment, label, or explicit “please send a PR”).

## Decision tree

```text
Maintainer reply
├── "Looks good / send a PR"
│     → PR-APP: application.py + APPLICATION.md + test_application + example only
├── "Move next to strategy_validation"
│     → same API, different package path
├── "Docs-only"
│     → APPLICATION.md + example as pattern; no package if they prefer
├── "Expand residuals" (WAIT templates, etc.)
│     → new small factory; separate issue if large
├── "Not wanted"
│     → close; keep local pattern
└── Silence
      → one polite bump with 🤖🤖🤖; then wait
```

## PR-APP scope (when welcomed)

**Include:** `src/nooa/formal/application.py` (+ minimal `__init__` exports if needed),
`APPLICATION.md`, `tests/formal/test_application.py`, example.

**Exclude as PR subject:** long CT/MT dual-lens catalogs (can stay unmerged or separate).

## Recorded issue

**Opened:** https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41  

Details: `docs/formal/OPENED_ISSUE.md`.
