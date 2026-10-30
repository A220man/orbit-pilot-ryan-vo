"""Validator CLI for findings and coverage ledger."""
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from pydantic import ValidationError

from app.schemas import (
    FindingCreate,
    FindingResponse,
    CoverageLedgerBase,
    CoverageLedgerResponse,
    CoverageLedgerUnit,
    CoverageLedgerAttempt,
)

app = typer.Typer(name="validate", help="Validate findings and coverage ledger data")
console = Console()


@app.command("finding")
def validate_finding(
    file_path: Path = typer.Argument(..., help="Path to JSON file with finding data"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Strict validation (fail on warnings)"),
    response: bool = typer.Option(False, "--response", "-r", help="Validate as FindingResponse (requires id, audit_run_id, timestamps)"),
):
    """Validate a finding JSON file against the schema."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)

    errors = []
    warnings = []

    # Validate as FindingCreate (for new findings) or FindingResponse
    model = FindingResponse if response else FindingCreate
    try:
        finding = model(**data)
        console.print(f"[green]✓ Valid as {model.__name__}[/green]")
    except ValidationError as e:
        errors.append(f"{model.__name__} validation failed: {e}")

    # Additional semantic checks
    if "cvss_vector" in data and data["cvss_vector"]:
        if not data["cvss_vector"].startswith("CVSS:"):
            warnings.append("CVSS vector should start with 'CVSS:'")

    if "cwe" in data and data["cwe"]:
        for cwe in data["cwe"]:
            if not cwe.startswith("CWE-"):
                warnings.append(f"CWE ID should start with 'CWE-': {cwe}")

    if "references" in data and data["references"]:
        for ref in data["references"]:
            if "url" not in ref:
                warnings.append("Reference missing 'url' field")

    if warnings:
        console.print("[yellow]Warnings:[/yellow]")
        for w in warnings:
            console.print(f"  - {w}")

    if errors:
        console.print("[red]Errors:[/red]")
        for e in errors:
            console.print(f"  - {e}")
        raise typer.Exit(1)

    if strict and warnings:
        console.print("[red]Strict mode: warnings treated as errors[/red]")
        raise typer.Exit(1)

    console.print("[green]Validation passed[/green]")


@app.command("coverage")
def validate_coverage(
    file_path: Path = typer.Argument(..., help="Path to JSON file with coverage ledger data"),
    strict: bool = typer.Option(False, "--strict", "-s", help="Strict validation (fail on warnings)"),
    response: bool = typer.Option(False, "--response", "-r", help="Validate as CoverageLedgerResponse (requires audit_run_id, timestamps)"),
):
    """Validate a coverage ledger JSON file against the schema."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)

    errors = []
    warnings = []

    model = CoverageLedgerResponse if response else CoverageLedgerBase
    try:
        coverage = model(**data)
        console.print(f"[green]✓ Valid as {model.__name__}[/green]")
    except ValidationError as e:
        errors.append(f"{model.__name__} validation failed: {e}")

    # Check for duplicate unit IDs
    unit_ids = [u.get("unit_id") for u in data.get("units", [])]
    if len(unit_ids) != len(set(unit_ids)):
        warnings.append("Duplicate unit IDs found")

    # Check for duplicate attempt IDs
    attempt_ids = [a.get("attempt_id") for a in data.get("attempts", [])]
    if len(attempt_ids) != len(set(attempt_ids)):
        warnings.append("Duplicate attempt IDs found")

    # Display summary
    console.print(f"Units: {len(data.get('units', []))}")
    console.print(f"Attempts: {len(data.get('attempts', []))}")
    console.print(f"Promoted artifacts: {len(data.get('promoted_artifacts', {}))}")

    if warnings:
        console.print("[yellow]Warnings:[/yellow]")
        for w in warnings:
            console.print(f"  - {w}")

    if errors:
        console.print("[red]Errors:[/red]")
        for e in errors:
            console.print(f"  - {e}")
        raise typer.Exit(1)

    if strict and warnings:
        console.print("[red]Strict mode: warnings treated as errors[/red]")
        raise typer.Exit(1)

    console.print("[green]Validation passed[/green]")


@app.command("coverage-display")
def display_coverage(
    file_path: Path = typer.Argument(..., help="Path to JSON file with coverage ledger data"),
    response: bool = typer.Option(False, "--response", "-r", help="Parse as CoverageLedgerResponse (requires audit_run_id, timestamps)"),
):
    """Display coverage ledger in a formatted table."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON: {e}[/red]")
        raise typer.Exit(1)
    except FileNotFoundError:
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)

    model = CoverageLedgerResponse if response else CoverageLedgerBase
    try:
        coverage = model(**data)
    except ValidationError as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)

    # Units table
    unit_table = Table(title="Coverage Units")
    unit_table.add_column("Unit ID", style="cyan")
    unit_table.add_column("Title", style="white")
    unit_table.add_column("Attack Class", style="white")
    unit_table.add_column("Status", style="white")
    unit_table.add_column("Files", style="white")
    unit_table.add_column("Assigned To", style="white")

    for unit in coverage.units:
        unit_table.add_row(
            unit.unit_id,
            unit.title,
            unit.attack_class,
            unit.status.value if hasattr(unit.status, 'value') else str(unit.status),
            ", ".join(unit.files) if unit.files else "N/A",
            unit.assigned_to or "N/A",
        )

    console.print(unit_table)

    # Attempts table
    attempt_table = Table(title="Coverage Attempts")
    attempt_table.add_column("Attempt ID", style="cyan")
    attempt_table.add_column("Phase", style="white")
    attempt_table.add_column("Units Targeted", style="white")
    attempt_table.add_column("Units Completed", style="white")
    attempt_table.add_column("Artifacts", style="white")

    for attempt in coverage.attempts:
        attempt_table.add_row(
            str(attempt.attempt_id),
            attempt.phase,
            ", ".join(attempt.units_targeted) if attempt.units_targeted else "N/A",
            ", ".join(attempt.units_completed) if attempt.units_completed else "N/A",
            str(len(attempt.artifacts)) if attempt.artifacts else "0",
        )

    console.print(attempt_table)

    # Promoted artifacts
    if coverage.promoted_artifacts:
        artifact_table = Table(title="Promoted Artifacts")
        artifact_table.add_column("Key", style="cyan")
        artifact_table.add_column("Value", style="white")
        for key, value in coverage.promoted_artifacts.items():
            artifact_table.add_row(key, json.dumps(value)[:80])
        console.print(artifact_table)


if __name__ == "__main__":
    app()
