---
name: setup-github-project
description: Detect the current GitHub repository from its Git origin remote, reuse its linked Project or create one, and ensure the agreed statuses and labels with a readable Bash script. Use for one-to-one repository/Project setup or verification.
metadata:
  version: "3.0.0"
---

# Set up a GitHub Project

Run from the repository being configured, including a subdirectory. Keep this tooling in the user-level skill directory; do not add scripts or development documentation to the target repository.

## Check, then apply

Resolve the script relative to this SKILL.md:

```bash
bash <skill-directory>/scripts/setup.sh
```

This previews without writes. If the user requested setup/configuration, inspect the preview, then run:

```bash
bash <skill-directory>/scripts/setup.sh --apply
```

No repository, Project number, owner, or title arguments are needed. An inspection or discussion request alone does not authorize applying changes.

## Exact workflow

1. Check Git, gh, jq, authentication, and the baseline data.
2. Read `git remote get-url origin` from the active repository. Accept GitHub HTTPS, SCP-style SSH, and `ssh://git@github.com/` remotes. Resolve the canonical repository through GitHub.
3. Read that repository's linked Projects. Reuse its single linked Project. If none is linked, create a new Project under the repository owner, using the repository name as its title, and link it. Do not search unrelated Projects by name or ask the user to repeat discoverable details.
4. Check the reverse association too: the selected Project must link exclusively to this repository. Multiple linked Projects, a shared Project, or a closed linked Project is a conflict: report it without unlinking, replacing, or modifying existing associations.
5. Ensure missing statuses and labels, then reread GitHub to verify both configuration and the one-to-one link. Matching configuration requires no writes or recreation.

The current repository is selected through `origin`. Missing/unsupported remotes, missing tools, authentication failures, and access failures stop with a clear report; do not guess, install tools, or change credentials. Use authorized host execution if a sandbox alone blocks CLI access.

## Baseline and boundaries

[scripts/baseline.json](scripts/baseline.json) contains the seven statuses and six labels. Assignees and Labels are built-in fields; no Priority field is added. Feedback stays In Review. Ready means approved and unblocked.

Add only missing values. Preserve existing status IDs, metadata, labels, issue values, and unrelated fields. Extra statuses, including factory options, are not removed or reordered. Case-only status conflicts require explicit resolution; label names match case-insensitively.

Do not change issue states or membership, assignments, repository files, commits, pushes, permissions, or built-in workflows. The script has no background monitoring or event triggers. Board layout and disabling built-in workflows remain a UI checklist, not a verified script outcome.

Project creation and linking are separate API calls. If one fails or its outcome is unknown, report partial state and inspect it before retrying; do not create another Project blindly. Avoid concurrent setup/configuration edits. A new Project with the same title as an unrelated, unlinked Project is permitted: association, not title matching, selects the target.

Exit `0` means preview or verification completed; `2` means a prerequisite/input/conflict failure. Other nonzero exits indicate errors and may leave partial changes. Report the detected repository, Project URL, changes or no-op result, verification, and remaining UI work. Never print credentials.

## Validate changes to this skill

```bash
bash -n <skill-directory>/scripts/setup.sh
shellcheck <skill-directory>/scripts/setup.sh
python3 -B -m unittest discover -s <skill-directory>/tests
```

Tests use real Git, Bash and jq with a fake gh; no network calls. Python and ShellCheck are development-only.
