---
name: commit-now
description: When explicitly invoked, create Git commits within the user's requested scope, group related whole files, and write Conventional Commit messages compatible with the repository's Commitizen rules.
metadata:
  version: "1.0.0"
---

# Commit Now

Turn the authorized changes into a clear, traceable commit history. A request to commit authorizes creating local commits; pushing or rewriting existing history needs its own authorization.

## Invocation and scope

- Run only when the user explicitly invokes `commit-now` by name or as `$commit-now`. File saves, edits, completed tasks, and generic requests to save work do not trigger this skill. Do not install file watchers, scheduled jobs, or automatic commit hooks.
- With no inclusion or exclusion instructions, commit all pending repository changes: staged, unstaged, and untracked files, including additions, modifications, and deletions. Include both staged and unstaged changes in partially staged files. Apply coherent grouping and Conventional Commit messages without asking the user to select paths. Do not force-add ignored files.
- Follow the user's current inclusion and exclusion instructions for files and folders. A specific inclusion limits the eligible set; exclusions remove paths from that set and take priority over grouping preferences. Never include an excluded path merely because it is related, already staged, or needed by another change. Leave excluded and unrequested changes uncommitted.
- With only exclusions, commit everything else. With inclusions, commit only the specified scope minus any exclusions. If exclusions prevent a coherent commit, explain the dependency and ask only if a decision is necessary; do not silently expand the scope.
- Before committing, ensure the index contains only the current authorized group. If excluded or unrelated files are already staged, unstage those paths without changing their working contents, and restore their original staged state after the authorized commits. Preserve partially staged content exactly when doing so; if that cannot be done safely, ask before altering it.

## Inspect and group

1. Read applicable repository instructions and commit conventions, including Commitizen configuration. Inspect status, staged and unstaged diffs, and relevant untracked files before deciding what belongs together. Include additions and deletions within the user's requested scope.
2. Group files by shared purpose or behavior, not simply by directory, extension, or file count. Keep an implementation with its relevant tests, documentation, configuration, and lockfile changes when they serve the same change.
3. Use one commit for a small, coherent change. For substantial changes with distinct purposes, make several focused commits. Do not force one commit per file or split a single coherent change merely because its diff is large.
4. Assign each file to exactly one commit. Stage whole files only; do not split hunks, temporarily edit files, or reconstruct intermediate file versions. If a file connects otherwise separate groups, combine those groups into the smallest coherent commit and describe the combined purpose honestly.
5. Order dependent groups so prerequisites come first and later commits build on them. Prefer commits that remain understandable and valid on their own. Briefly state the grouping when multiple commits are needed, then proceed without routine confirmation. Honor an explicit request for a single commit or a particular grouping.

Existing staging does not limit the default all-changes scope. If the user explicitly requests staged changes only and a partially staged file conflicts with whole-file grouping, ask before including its unstaged changes. Never discard working changes to simplify grouping.

## Write messages

Follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/): `type(scope): summary`, with optional scope and `!` immediately before the colon for breaking changes. Separate any body and footers with blank lines. A scope identifies a codebase area.

Choose the type by intent:

| Type       | Use for                                         |
| ---------- | ----------------------------------------------- |
| `feat`     | New functionality                               |
| `fix`      | Bug corrections                                 |
| `refactor` | Restructuring without behavior changes          |
| `perf`     | Performance improvements                        |
| `docs`     | Documentation changes                           |
| `test`     | Tests and test maintenance                      |
| `build`    | Build tooling or dependencies                   |
| `ci`       | CI workflows and configuration                  |
| `style`    | Formatting without semantic changes             |
| `chore`    | Other maintenance                               |
| `revert`   | Reversing an earlier commit; reference its hash |

The specification defines `feat` and `fix`; the other types are common conventions, not a mandated list. Follow repository and Commitizen constraints on types, scopes, and lengths. Use concise imperative subjects as a writing preference, not a specification requirement.

Describe concrete changes; avoid vague subjects. Include bodies only for useful context and footers only for known facts. Never invent issue references or test results. Any type can introduce a breaking change. The specification accepts `!` or an uppercase `BREAKING CHANGE:` footer; prefer both to explain impact and migration clearly.

## Commit and verify

- Stage explicit paths for one group at a time, including deletions. Inspect the staged diff before each commit to confirm that only that group is included. Avoid blanket staging unless every pending file belongs to the same authorized group.
- Run relevant checks and let installed hooks, including Commitizen, run normally. Do not bypass hooks or change their configuration to get a commit through.
- If hooks format files, review those edits and restage only affected files in the current group before retrying. Fix message validation errors directly. If a failure requires substantive unrelated changes or remains unresolved, stop and report it while preserving uncommitted work.
- After each commit, verify its result before starting the next group. At the end, inspect status to ensure every intended change was committed and identify anything remaining.
- Report commit hashes and subjects concisely, along with any remaining changes or failed checks. If there are no changes, say so without creating an empty commit.
