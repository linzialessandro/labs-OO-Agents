# Opened issue + fork branch (for automated follow-up)

| Field | Value |
|-------|--------|
| Upstream issue | **#41** — https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41 |
| Title | `[Feature] Opt-in method-boundary residual contracts for CodeAct postconditions 🤖🤖🤖` |
| Public fork | https://github.com/linzialessandro/labs-OO-Agents |
| Feature branch | `feature/issue-41-method-boundary-residual-contracts` |
| Branch URL | https://github.com/linzialessandro/labs-OO-Agents/tree/feature/issue-41-method-boundary-residual-contracts |
| Remotes | `origin` → fork, `upstream` → `NVIDIA-NeMo/labs-OO-Agents` |
| Commit | DCO `Signed-off-by` + 🤖🤖🤖; residual-contract slice only |

## What is on the branch (PR-APP scope)

- `src/nooa/formal/application.py` + thin `__init__.py` (**public API only**)
- `src/nooa/formal/model_theory.py` (**private support**, not re-exported)
- `APPLICATION.md`, `SCOPE.md`
- `tests/formal/test_application.py`
- `examples/formal/`
- `docs/formal/` (issue / follow-up notes)

Theory-heavy local files (LEARNING, perspectives, article, …) stay **untracked**
and are **not** part of the PR unless maintainers ask later.

## Later: open PR only after welcome on #41

```bash
gh issue view 41 --repo NVIDIA-NeMo/labs-OO-Agents

gh pr create --repo NVIDIA-NeMo/labs-OO-Agents \
  --head linzialessandro:feature/issue-41-method-boundary-residual-contracts \
  --base main \
  --title "feat: opt-in method-boundary residual contracts 🤖🤖🤖" \
  --body "Closes #41

Opt-in residual contracts for CodeAct postconditions (InvariantError retry).
Docs: src/nooa/formal/APPLICATION.md. No default runtime change when unused.

🤖🤖🤖"
```

Do **not** open a PR until there is positive maintainer signal on #41.
See `FOLLOWUP.md`.
