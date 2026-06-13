import platform
import subprocess
from enum import Enum
from pathlib import Path


class LinkType(Enum):
    """Type of link to create."""

    SYMLINK = "symlink"
    COPY = "copy"


class LinkStatus(Enum):
    """Status of a link."""

    OK = "ok"
    MISSING_SOURCE = "missing_source"
    MISSING_TARGET = "missing_target"
    BROKEN = "broken"
    MISMATCH = "mismatch"
    NOT_LINKED = "not_linked"


class LinkResult:
    """Result of a link operation."""

    def __init__(
        self,
        source: Path,
        target: Path,
        status: LinkStatus,
        message: str = "",
        created: bool = False,
    ):
        self.source = source
        self.target = target
        self.status = status
        self.message = message
        self.created = created

    def __repr__(self) -> str:
        return f"LinkResult({self.source} -> {self.target}, {self.status.value})"


def is_windows() -> bool:
    """Check if running on Windows (not WSL)."""
    return platform.system() == "Windows"


def is_wsl() -> bool:
    """Check if running in WSL."""
    if platform.system() != "Linux":
        return False
    try:
        with open("/proc/version", encoding="utf-8") as f:
            return "microsoft" in f.read().lower()
    except Exception:
        return False


def create_directory_junction_windows(source: Path, target: Path) -> bool:
    """Create a directory junction on Windows using mklink /J."""
    try:
        # mklink /J requires target then source (opposite of symlink)
        cmd = ["cmd", "/c", "mklink", "/J", str(target), str(source)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode == 0
    except Exception:
        return False


def create_symlink(source: Path, target: Path, link_type: LinkType = LinkType.SYMLINK) -> LinkResult:
    """
    Create a symlink or copy from source to target.

    Args:
        source: Source path (must exist)
        target: Target path (will be created)
        link_type: Type of link to create (symlink or copy)

    Returns:
        LinkResult with status and details
    """
    # Validate source exists
    if not source.exists():
        return LinkResult(
            source=source,
            target=target,
            status=LinkStatus.MISSING_SOURCE,
            message=f"Source does not exist: {source}",
        )

    # Check if target already exists
    if target.exists() or target.is_symlink():
        # Check if it's already correctly linked
        if target.is_symlink():
            try:
                resolved = target.resolve()
                if resolved == source.resolve():
                    return LinkResult(
                        source=source,
                        target=target,
                        status=LinkStatus.OK,
                        message="Already correctly linked",
                    )
                else:
                    return LinkResult(
                        source=source,
                        target=target,
                        status=LinkStatus.MISMATCH,
                        message=f"Target points to {resolved} instead of {source}",
                    )
            except Exception as e:
                return LinkResult(
                    source=source,
                    target=target,
                    status=LinkStatus.BROKEN,
                    message=f"Broken symlink: {e}",
                )
        else:
            return LinkResult(
                source=source,
                target=target,
                status=LinkStatus.MISMATCH,
                message="Target exists but is not a symlink",
            )

    # Create parent directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)

    # Handle copy mode
    if link_type == LinkType.COPY:
        try:
            if source.is_dir():
                import shutil

                shutil.copytree(source, target, symlinks=True)
            else:
                import shutil

                shutil.copy2(source, target)
            return LinkResult(
                source=source,
                target=target,
                status=LinkStatus.OK,
                message="Copied successfully",
                created=True,
            )
        except Exception as e:
            return LinkResult(
                source=source,
                target=target,
                status=LinkStatus.BROKEN,
                message=f"Copy failed: {e}",
            )

    # Create symlink (OS-aware)
    try:
        if is_windows():
            # On Windows, use directory junction for directories
            if source.is_dir():
                success = create_directory_junction_windows(source, target)
                if success:
                    return LinkResult(
                        source=source,
                        target=target,
                        status=LinkStatus.OK,
                        message="Junction created successfully",
                        created=True,
                    )
                else:
                    return LinkResult(
                        source=source,
                        target=target,
                        status=LinkStatus.BROKEN,
                        message="Failed to create junction (may need admin rights)",
                    )
            else:
                # For files, use regular symlink
                target.symlink_to(source)
        else:
            # On Unix/Linux/WSL, use regular symlinks
            target.symlink_to(source, target_is_directory=source.is_dir())

        return LinkResult(
            source=source,
            target=target,
            status=LinkStatus.OK,
            message="Symlink created successfully",
            created=True,
        )
    except Exception as e:
        return LinkResult(
            source=source,
            target=target,
            status=LinkStatus.BROKEN,
            message=f"Failed to create symlink: {e}",
        )


def check_link_status(source: Path, target: Path) -> LinkResult:
    """Check the status of a link without modifying it."""
    if not source.exists():
        return LinkResult(
            source=source,
            target=target,
            status=LinkStatus.MISSING_SOURCE,
            message="Source does not exist",
        )

    if not target.exists() and not target.is_symlink():
        return LinkResult(
            source=source,
            target=target,
            status=LinkStatus.NOT_LINKED,
            message="Target does not exist",
        )

    if target.is_symlink():
        try:
            resolved = target.resolve()
            if resolved == source.resolve():
                return LinkResult(
                    source=source,
                    target=target,
                    status=LinkStatus.OK,
                    message="Correctly linked",
                )
            else:
                return LinkResult(
                    source=source,
                    target=target,
                    status=LinkStatus.MISMATCH,
                    message=f"Points to {resolved} instead of {source}",
                )
        except Exception as e:
            return LinkResult(
                source=source,
                target=target,
                status=LinkStatus.BROKEN,
                message=f"Broken symlink: {e}",
            )

    return LinkResult(
        source=source,
        target=target,
        status=LinkStatus.MISMATCH,
        message="Target exists but is not a symlink",
    )


def remove_link(target: Path) -> bool:
    """
    Safely remove a symlink or junction.

    Args:
        target: Path to remove

    Returns:
        True if removed successfully, False otherwise
    """
    try:
        if not target.exists() and not target.is_symlink():
            return True  # Already doesn't exist

        if target.is_symlink():
            target.unlink()
            return True
        elif is_windows() and target.is_dir():
            # On Windows, junctions need special handling
            subprocess.run(
                ["cmd", "/c", "rmdir", str(target)],
                capture_output=True,
                check=False,
            )
            return not target.exists()
        else:
            return False  # Not a link, don't remove
    except Exception:
        return False
