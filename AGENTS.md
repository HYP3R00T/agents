# Agent instructions

Keep user-facing responses concise and to the point.

## Skill versioning

Apply this convention to every locally maintained skill under `skills/`, including future additions. A version identifies a checkpoint; Git preserves the complete files needed to restore it. Version numbers alone do not establish that a skill works.

- Store each skill's version as a quoted string in its `SKILL.md` YAML frontmatter:

  ```yaml
  metadata:
    version: "1.0.0"
  ```

- Start unversioned skills at `1.0.0`. Preserve existing metadata and versions; do not invent versions for earlier history.
- Use independent major.minor.patch versions for each skill:
  - **Patch:** correct wording, examples, or a narrow failure without changing the intended workflow.
  - **Minor:** add compatible capabilities, preferences, or review steps.
  - **Major:** change purpose, defaults, or expected behavior enough that existing uses need adjustment.
- Bump once per completed logical update, not per file save or editing attempt. Include changes to the skill's instructions, references, scripts, assets, or agent metadata. Unrelated repository changes do not require skill bumps.
- Reset lower components when bumping a higher one: `1.2.3` becomes `1.3.0` or `2.0.0`. Do not reuse a released version for different contents.
- Validate the skill and check representative behavior appropriate to the change. Keep reusable test cases and results when they help establish a reliable checkpoint; do not invent evidence or treat frontmatter validation as behavioral proof.
- When committing is authorized, commit each version bump with its complete implementation. Record the affected skill, version, concrete changes, checks, and material limitations in the commit message as appropriate. Tags such as `humanizer/v1.1.0` are optional checkpoints, not automatic actions.
- Restore older behavior from the corresponding Git commit or tag. If publishing that restoration as a new update, assign a new version rather than relabeling it with a previously released version.

This convention does not authorize automatic commits, tags, pushes, or history rewrites. Keep versioning policy here instead of repeating it inside every skill's execution instructions. Omit optional `allowed-tools`, `compatibility`, and `license` frontmatter fields unless explicitly requested; preserve existing third-party licensing and attribution.
