# setup-github-project

Set up one GitHub Project for the current repository, with seven agreed statuses and a baseline set of labels.

[Explore the skill folder](https://github.com/HYP3R00T/agents/tree/main/skills/setup-github-project) · [Read SKILL.md](https://github.com/HYP3R00T/agents/blob/main/skills/setup-github-project/SKILL.md)

## When to use it

Invoke the skill explicitly from the target repository, including a subdirectory:

```text
$setup-github-project Set up the Project for this repository.
$setup-github-project Preview the Project configuration without changing anything.
```

The skill reads `origin` and confirms the repository through GitHub. The local folder can have a different name. It supports github.com HTTPS and SSH remotes, including SSH aliases that resolve to github.com.

## Requirements

Git, Bash, GitHub CLI (`gh`), `jq`, and authenticated GitHub access to the repository and its Projects. Resolving SSH aliases also requires `ssh`. Keep the complete skill folder together, outside the target repository.

## What it does

1. Previews the detected repository, Project, and configuration changes without writing.
2. Reuses the repository's linked Project. If none is linked, creates one named after the repository and links it when applying.
3. Enforces exactly the seven Status options below, adding missing options and removing extras. Retained options keep their IDs and metadata.
4. Adds missing baseline repository labels and preserves all extra labels.
5. Rereads GitHub to verify the statuses, labels, and one-to-one association.

| Status | Meaning |
| --- | --- |
| Backlog | Captured work; requirements are being refined. |
| Ready | Approved, sufficiently defined, and unblocked. |
| In Progress | A human or agent owns implementation. |
| In Review | A reviewable PR exists; revisions and feedback stay here. |
| Blocked | Temporarily unable to proceed; record the blocker. |
| Done | Agreed outcome delivered and verified. |
| Not Planned | Not proceeding; record the reason. |

Required labels are `bug`, `enhancement`, `documentation`, `maintenance`, `dependencies`, and `ci`. [baseline.json](https://github.com/HYP3R00T/agents/blob/main/skills/setup-github-project/scripts/baseline.json) defines their descriptions and colors.

## Boundaries

Setup requests authorize applying the previewed changes. Inspection requests only preview. `agents/openai.yaml` disables implicit invocation for agents that honor that setting.

The association must be one-to-one in both directions. Multiple linked Projects, a shared Project, or a closed Project stop the run for resolution. Missing tools, access failures, and unsupported remotes also stop the run.

Extra Status options are deleted; the skill does not choose replacement statuses for affected items. Case-only status conflicts require explicit resolution. Labels match case-insensitively.

The skill does not edit repository files, assignments, permissions, or built-in workflows. Board layout with Status columns and disabling built-in workflows remain manual checks. It adds no Priority field and does not keep issues or Project items synchronized afterward.

Creation and linking are separate operations. After a failure, inspect the partial state before retrying. The final report includes the Project URL, changes, verification, and remaining manual work.

`SKILL.md` is the source of truth for the full workflow.
