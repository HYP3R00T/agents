# Contributing

Keep additions focused, documented, and useful for real agent workflows.

## Repository layout

| Path             | Purpose                                                        |
| ---------------- | -------------------------------------------------------------- |
| `skills/<name>/` | A skill's instructions and supporting resources.               |
| `docs/`          | Usage guides and contributor documentation.                    |
| `.github/`       | Quality checks, documentation deployment, and issue templates. |
| `scripts/`       | Repository maintenance and development helpers.                |

Other agent resources can be added when needed; document their purpose and usage alongside them.

## Add or update a component

Document its purpose, setup, usage, and requirements. Keep related files together, update relevant documentation and navigation, and verify the behavior affected by your change. This applies to skills, extensions, CLI tools, and other agent resources.

### Skills

Follow the skill versioning convention in the repository root's `AGENTS.md` for every skill update. Store the version in `metadata.version` and include the bump with the corresponding implementation when committing.

1. Create or update `skills/<name>/SKILL.md` with YAML front matter containing `name` and `description`.
2. Explain invocation, scope, prerequisites, behavior, and any actions that require explicit authorization. Include concrete examples.
3. Keep supporting files in the skill folder. Add agent-specific metadata, such as `agents/openai.yaml`, when relevant.
4. Update the skill tables in `README.md` and `docs/index.md`. Link the README entry to the skill folder.
5. Add or update the usage guide under `docs/skills/` and its navigation entry in `zensical.toml`.
6. Try representative requests in a disposable repository. For skills that change Git history or files, verify scope handling and preserve unrelated work.

## Local checks

Install [uv](https://docs.astral.sh/uv/) and [prek](https://prek.j178.dev/), then run from the repository root:

```bash
prek run --all-files
uvx zensical build --strict --clean
```

The hooks check file formats, Markdown, shell scripts, and common mistakes. They may format files; review any changes. Commitizen validates commit messages when the commit-message hook is installed.

Preview the documentation:

```bash
uvx zensical serve
```

If you use mise, `mise install` installs the configured development tools and `mise run docs` starts the preview. Its project entry hook installs Commitizen and Git hooks when the required tools are available.

## CI and documentation publishing

CI runs the repository hooks and builds the documentation on pull requests and pushes to `main`. Run any additional checks appropriate to the affected component and describe the results in your pull request.

The documentation workflow builds and publishes to GitHub Pages after documentation, site configuration, or deployment workflow changes reach `main`. It can also be started manually. The repository's Pages source must be set to **GitHub Actions**.

## Issues and pull requests

Use a bug report for unexpected behavior in any component. Include the affected area, relevant environment details, reproduction steps, and expected versus actual behavior. Remove secrets and private repository content from examples.

Use a feature request for new capabilities or improvements. Describe the problem, proposed solution, and an example of the intended usage. In pull requests, explain the change and record the checks or manual scenarios you ran.
