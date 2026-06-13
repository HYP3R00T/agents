"""CLI interface for agentsyncer."""

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .linker import LinkStatus, LinkType, check_link_status, create_symlink, remove_link
from .mapping import AGENT_STRUCTURE, AGENTS_SOURCE, get_all_mappings, get_source_path

app = typer.Typer(
    name="agentsyncer",
    help="Sync agent configurations across AI tools using a single source of truth",
    no_args_is_help=True,
)
console = Console()


@app.command()
def sync(
    copy: Annotated[
        bool,
        typer.Option(
            "--copy",
            "-c",
            help="Copy files instead of creating symlinks",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Remove existing mismatched links before creating new ones",
        ),
    ] = False,
) -> None:
    """
    Sync all agent configurations from .agents to target locations.

    Creates symlinks (or copies with --copy) from ~/.agents/* to all configured
    AI tool locations. Idempotent - safe to run multiple times.
    """
    console.print(f"\n[bold cyan]Syncing from:[/bold cyan] {AGENTS_SOURCE}")
    console.print(f"[bold cyan]Link type:[/bold cyan] {'copy' if copy else 'symlink'}\n")

    if not AGENTS_SOURCE.exists():
        console.print(
            f"[bold red]Error:[/bold red] Source directory does not exist: {AGENTS_SOURCE}",
            style="red",
        )
        console.print(
            f"\n[yellow]Tip:[/yellow] Create {AGENTS_SOURCE} and add your agent configurations there.",
        )
        raise typer.Exit(1)

    link_type = LinkType.COPY if copy else LinkType.SYMLINK
    mappings = get_all_mappings()

    if not mappings:
        console.print("[yellow]No mappings configured.[/yellow]")
        raise typer.Exit(0)

    results = []
    for source, target in mappings:
        # Check if source exists
        if not source.exists():
            console.print(f"[dim]Skipping {source.name} (source doesn't exist)[/dim]")
            continue

        # Handle force flag
        if force and (target.exists() or target.is_symlink()):
            status = check_link_status(source, target)
            if status.status in (LinkStatus.MISMATCH, LinkStatus.BROKEN):
                console.print(f"[yellow]Removing mismatched link:[/yellow] {target}")
                remove_link(target)

        result = create_symlink(source, target, link_type)
        results.append(result)

        # Print result
        if result.created:
            console.print(f"[green]✓[/green] Created: {target}")
        elif result.status == LinkStatus.OK:
            console.print(f"[dim]✓ Already linked: {target}[/dim]")
        elif result.status == LinkStatus.MISMATCH:
            console.print(f"[yellow]⚠[/yellow] Mismatch: {target}")
            console.print(f"  [dim]{result.message}[/dim]")
        else:
            console.print(f"[red]✗[/red] Failed: {target}")
            console.print(f"  [dim]{result.message}[/dim]")

    # Summary
    created = sum(1 for r in results if r.created)
    ok = sum(1 for r in results if r.status == LinkStatus.OK and not r.created)
    failed = sum(1 for r in results if r.status not in (LinkStatus.OK,))

    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Created: {created}")
    console.print(f"  Already OK: {ok}")
    if failed > 0:
        console.print(f"  Failed: {failed}", style="red")


@app.command()
def status() -> None:
    """
    Show the status of all agent configuration links.

    Displays which links exist, which are broken, and which are missing.
    """
    console.print("\n[bold cyan]Agent Configuration Status[/bold cyan]")
    console.print(f"[dim]Source: {AGENTS_SOURCE}[/dim]\n")

    if not AGENTS_SOURCE.exists():
        console.print(
            f"[bold red]Error:[/bold red] Source directory does not exist: {AGENTS_SOURCE}",
            style="red",
        )
        raise typer.Exit(1)

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Category", style="cyan")
    table.add_column("Source", style="dim")
    table.add_column("Target", style="white")
    table.add_column("Status", style="white")

    mappings = get_all_mappings()
    stats = {
        "ok": 0,
        "missing_source": 0,
        "not_linked": 0,
        "broken": 0,
        "mismatch": 0,
    }

    for source, target in mappings:
        # Determine category
        category = source.name

        # Check status
        result = check_link_status(source, target)

        # Update stats
        if result.status == LinkStatus.OK:
            stats["ok"] += 1
            status_text = "[green]✓ OK[/green]"
        elif result.status == LinkStatus.MISSING_SOURCE:
            stats["missing_source"] += 1
            status_text = "[dim]- No source[/dim]"
        elif result.status == LinkStatus.NOT_LINKED:
            stats["not_linked"] += 1
            status_text = "[yellow]⚠ Not linked[/yellow]"
        elif result.status == LinkStatus.BROKEN:
            stats["broken"] += 1
            status_text = "[red]✗ Broken[/red]"
        elif result.status == LinkStatus.MISMATCH:
            stats["mismatch"] += 1
            status_text = "[yellow]⚠ Mismatch[/yellow]"
        else:
            status_text = "[dim]?[/dim]"

        # Add row
        source_exists = "✓" if source.exists() else "✗"
        table.add_row(
            category,
            f"{source_exists} {source.name}",
            str(target),
            status_text,
        )

    console.print(table)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  OK: {stats['ok']}")
    if stats["not_linked"] > 0:
        console.print(f"  Not linked: {stats['not_linked']}", style="yellow")
    if stats["mismatch"] > 0:
        console.print(f"  Mismatched: {stats['mismatch']}", style="yellow")
    if stats["broken"] > 0:
        console.print(f"  Broken: {stats['broken']}", style="red")
    if stats["missing_source"] > 0:
        console.print(f"  Missing source: {stats['missing_source']}", style="dim")

    if stats["not_linked"] > 0 or stats["broken"] > 0 or stats["mismatch"] > 0:
        console.print("\n[yellow]Tip:[/yellow] Run [cyan]agentsyncer sync[/cyan] to fix issues.")


@app.command()
def doctor(
    fix: Annotated[
        bool,
        typer.Option(
            "--fix",
            "-f",
            help="Automatically fix broken and missing links",
        ),
    ] = False,
) -> None:
    """
    Check for issues and optionally fix them.

    Identifies broken links, missing sources, and mismatches.
    Use --fix to automatically repair issues.
    """
    console.print("\n[bold cyan]Running diagnostics...[/bold cyan]\n")

    if not AGENTS_SOURCE.exists():
        console.print(
            f"[bold red]✗ Source directory missing:[/bold red] {AGENTS_SOURCE}",
        )
        console.print(
            f"\n[yellow]Fix:[/yellow] Create the directory:\n  mkdir -p {AGENTS_SOURCE}",
        )
        raise typer.Exit(1)
    else:
        console.print(f"[green]✓[/green] Source directory exists: {AGENTS_SOURCE}")

    # Check each category
    issues = []
    for category in AGENT_STRUCTURE:
        source = get_source_path(category)
        if not source.exists():
            issues.append(f"Missing source category: {category}")
            console.print(f"[yellow]⚠[/yellow] Category '{category}' not found in source")
        else:
            console.print(f"[green]✓[/green] Category '{category}' exists")

    # Check all links
    mappings = get_all_mappings()
    broken_links = []
    missing_links = []
    mismatched_links = []

    for source, target in mappings:
        if not source.exists():
            continue

        result = check_link_status(source, target)

        if result.status == LinkStatus.BROKEN:
            broken_links.append((source, target))
            console.print(f"[red]✗[/red] Broken link: {target}")
        elif result.status == LinkStatus.NOT_LINKED:
            missing_links.append((source, target))
            console.print(f"[yellow]⚠[/yellow] Missing link: {target}")
        elif result.status == LinkStatus.MISMATCH:
            mismatched_links.append((source, target))
            console.print(f"[yellow]⚠[/yellow] Mismatched link: {target}")

    # Summary
    total_issues = len(broken_links) + len(missing_links) + len(mismatched_links)

    console.print(f"\n[bold]Issues found:[/bold] {total_issues}")
    if broken_links:
        console.print(f"  Broken links: {len(broken_links)}", style="red")
    if missing_links:
        console.print(f"  Missing links: {len(missing_links)}", style="yellow")
    if mismatched_links:
        console.print(f"  Mismatched links: {len(mismatched_links)}", style="yellow")

    # Fix if requested
    if fix and total_issues > 0:
        console.print("\n[bold cyan]Fixing issues...[/bold cyan]\n")

        fixed = 0
        for source, target in broken_links + mismatched_links:
            console.print(f"Removing broken/mismatched link: {target}")
            if remove_link(target):
                result = create_symlink(source, target)
                if result.status == LinkStatus.OK:
                    console.print(f"[green]✓[/green] Fixed: {target}")
                    fixed += 1
                else:
                    console.print(f"[red]✗[/red] Failed to fix: {target}")

        for source, target in missing_links:
            result = create_symlink(source, target)
            if result.status == LinkStatus.OK:
                console.print(f"[green]✓[/green] Created: {target}")
                fixed += 1
            else:
                console.print(f"[red]✗[/red] Failed to create: {target}")

        console.print(f"\n[bold]Fixed:[/bold] {fixed}/{total_issues}")
    elif total_issues > 0:
        console.print("\n[yellow]Tip:[/yellow] Run [cyan]agentsyncer doctor --fix[/cyan] to repair issues.")
    else:
        console.print("\n[green]✓ All checks passed![/green]")


def main() -> None:
    app()
