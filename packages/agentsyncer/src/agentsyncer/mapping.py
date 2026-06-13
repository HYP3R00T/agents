from pathlib import Path
from typing import TypedDict


class AgentMapping(TypedDict):
    """Mapping of source categories to target paths."""

    targets: list[str]
    description: str


# Source directory (canonical store)
AGENTS_SOURCE = Path.home() / ".agents"

# Agent ecosystem structure mapping
# Maps .agents subdirectories to their target locations across different AI tools
AGENT_STRUCTURE: dict[str, AgentMapping] = {
    "skills": {
        "targets": [
            "~/.cursor/skills",
            "~/.claude/skills",
            "~/.copilot/skills",
            "~/.windsurf/skills",
            ".github/copilot/skills",
        ],
        "description": "Agent skills and prompts",
    },
    "agents": {
        "targets": [
            "~/.claude/agents",
            "~/.cursor/agents",
            ".github/copilot/agents",
        ],
        "description": "Agent definitions and configurations",
    },
    "hooks": {
        "targets": [
            "~/.cursor/hooks",
            "~/.claude/hooks",
        ],
        "description": "Lifecycle hooks and event handlers",
    },
    "mcp": {
        "targets": [
            "~/.claude/mcp",
            "~/.cursor/mcp",
        ],
        "description": "Model Context Protocol configurations",
    },
}


def expand_path(path_str: str) -> Path:
    """Expand ~ and resolve path to absolute."""
    path = Path(path_str).expanduser()
    # If path is relative and doesn't start with ~, make it relative to cwd
    if not path.is_absolute():
        path = Path.cwd() / path
    return path


def get_source_path(category: str) -> Path:
    """Get the source path for a given category."""
    return AGENTS_SOURCE / category


def get_target_paths(category: str) -> list[Path]:
    """Get all target paths for a given category."""
    if category not in AGENT_STRUCTURE:
        return []
    return [expand_path(target) for target in AGENT_STRUCTURE[category]["targets"]]


def get_all_mappings() -> list[tuple[Path, Path]]:
    """Get all source -> target mappings as a flat list."""
    mappings = []
    for category in AGENT_STRUCTURE:
        source = get_source_path(category)
        mappings.extend((source, target) for target in get_target_paths(category))
    return mappings
