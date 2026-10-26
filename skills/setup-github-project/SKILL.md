---
name: setup-github-project
description: Detect the current GitHub repository, reuse or create its one-to-one Project, enforce seven statuses, and ensure baseline labels.
metadata:
  version: "1.1.0"
---

# Set up a GitHub Project

Run inside the target repository, including a subdirectory. Resolve the script relative to this skill:

```bash
bash <skill-directory>/scripts/setup.sh
```

This previews without writes. When the user requests setup, inspect the preview, then run the same command with `--apply`. Inspection or discussion alone does not authorize changes.

The script reads Git's `origin`, reuses the repository's single linked Project, or creates and links one named after the repository. Both sides must have exactly one association. Multiple Projects, a shared Project, or a closed Project stop the run without changing existing associations.

[scripts/baseline.json](scripts/baseline.json) defines the seven statuses and required repository labels. Status must contain exactly those seven names: add missing options and delete every extra option. Preserve IDs and metadata for retained options. Preview lists additions and removals. Do not assign replacement statuses to items using removed options. Status names differing only by case require resolution. Labels are additive: ensure required names exist, match case-insensitively, and preserve all extra labels. No Priority field is added. Feedback stays In Review; Ready means approved and unblocked.

Requires Git, Bash, `gh`, `jq`, and GitHub access. Supports github.com HTTPS and SSH remotes, including SSH aliases resolved through `ssh -G` (requires `ssh`). Repository identity comes from `origin` and is confirmed through GitHub; the local folder name does not matter. Report missing tools, authentication problems, or unsupported remotes; do not install tools or change credentials. Use authorized host execution if only the sandbox blocks access.

Keep this tooling outside the target repository. Do not change issues, assignments, permissions, repository files, or built-in workflows. Board layout with Status columns and disabling built-in workflows remain manual checks.

Creation and linking are separate operations. After a failure or uncertain outcome, inspect GitHub before retrying; never blindly create another Project. Avoid concurrent configuration edits.

Report the repository, Project URL when available, additions or no-op result, verification, and manual work. Exit `0` means preview or verification succeeded; `2` means invalid input, prerequisites, or a conflict. Other nonzero exits may leave partial changes.

For script changes, run `bash -n` and `shellcheck`, then check representative behavior without modifying live GitHub data.
