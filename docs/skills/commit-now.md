# commit-now

Create local Git commits from pending changes, grouped by purpose and described with Conventional Commit messages.

[Explore the skill folder](https://github.com/HYP3R00T/agents/tree/main/skills/commit-now) · [Read SKILL.md](https://github.com/HYP3R00T/agents/blob/main/skills/commit-now/SKILL.md)

## When to use it

Invoke `commit-now` explicitly when your changes are ready to commit. With no file restrictions, it includes all pending staged, unstaged, and untracked changes, including deletions. It does not force-add ignored files.

Example requests:

```text
$commit-now
$commit-now Commit only the changes in docs/.
$commit-now Commit everything except skills/experimental/.
```

Your agent must support skill discovery and invocation. The `$commit-now` syntax is an invocation example for agents that support it.

## What it does

- Reads repository instructions and commit conventions, including Commitizen configuration.
- Respects file inclusions and exclusions; exclusions take priority.
- Groups related whole files by purpose and orders dependent commits.
- Runs relevant checks and installed hooks, then verifies each commit.
- Reports commit hashes, subjects, and any remaining changes or failed checks.

## Boundaries

The skill runs only when explicitly invoked by name. It does not automatically commit after edits or file saves. Pushing and rewriting existing history require separate authorization.

Files are committed whole. If a staged-only request conflicts with a partially staged file, the skill asks before including unstaged changes. Excluded or unrelated staged content is preserved and restored after the authorized commits.

`SKILL.md` is the source of truth for the full workflow. The accompanying `agents/openai.yaml` provides its display metadata and disables implicit invocation for agents that honor that setting.
