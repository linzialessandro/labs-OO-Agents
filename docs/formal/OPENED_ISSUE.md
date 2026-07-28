# Opened issue (for automated follow-up)

| Field | Value |
|-------|--------|
| Repo | `NVIDIA-NeMo/labs-OO-Agents` |
| Number | **41** |
| URL | https://github.com/NVIDIA-NeMo/labs-OO-Agents/issues/41 |
| Title | `[Feature] Opt-in method-boundary residual contracts for CodeAct postconditions 🤖🤖🤖` |
| Opened by | `gh` as `linzialessandro` |
| Agent marker | 🤖🤖🤖 on title and body |

## Later automation (when maintainer welcomes a PR)

```bash
# Inspect replies / labels
gh issue view 41 --repo NVIDIA-NeMo/labs-OO-Agents
gh api repos/NVIDIA-NeMo/labs-OO-Agents/issues/41/comments

# After welcome: branch, DCO commits, PR with 🤖🤖🤖
git checkout -b feature/method-boundary-residual-contracts
# ... add only application + tests + APPLICATION.md + example ...
git commit -s -m "feat: opt-in method-boundary residual postconditions 🤖🤖🤖"
gh pr create --repo NVIDIA-NeMo/labs-OO-Agents \
  --title "feat: opt-in method-boundary residual contracts 🤖🤖🤖" \
  --body "Closes #41 🤖🤖🤖"
```

Do **not** open a PR until there is positive maintainer signal on #41.
See `FOLLOWUP.md`.
