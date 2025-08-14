"""
Command line interface for Pendragondi API Raw.

This CLI exposes a single command that analyzes the logged API calls and
writes a report to a file.  Use ``python -m pendragondi_api_raw.cli`` or
``pendragondi-api`` after installation.

Example::

    pendragondi-api --output report.md

The default format is Markdown.  Use ``--format json`` to emit JSON.
"""

from typing import Optional
import os
import re
from pathlib import Path
import typer

from .analyzer import analyze_calls
from .report import render_markdown_report, render_json_report

app = typer.Typer(help="Pendragondi API Raw – Detect redundant API calls and inefficiencies.")

REPORTS_DIR = Path("reports")

_ILLEGAL_CHARS = r'[<>:"/\\|?*\x00-\x1F]'
_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _sanitize_filename(name: str) -> str:
    """Return a filesystem‑safe filename (no directory components)."""
    base = Path(name).name.strip()
    if not base:
        base = "report.md"
    base = re.sub(_ILLEGAL_CHARS, "_", base)
    stem = Path(base).stem
    suffix = Path(base).suffix
    if stem.upper() in _RESERVED_NAMES:
        stem = f"_{stem}"
    if not suffix:
        suffix = ".md"
    return f"{stem}{suffix}"


def _resolve_output_path(output: Optional[str], fmt: str) -> Path:
    """
    Resolve the output path:
    - If an absolute path is provided, honour it (create parent dirs if needed).
    - If relative or not provided, write into ./reports/ .
    The file extension will be adjusted based on ``fmt``.
    """
    ext = ".json" if fmt == "json" else ".md"
    if output:
        out_path = Path(output)
        if out_path.is_absolute():
            final = out_path
        else:
            # If user passed directories, keep them (but sanitize final filename)
            if out_path.parent != Path("."):
                safe_name = _sanitize_filename(out_path.name)
                final = REPORTS_DIR / out_path.parent / safe_name
            else:
                safe_name = _sanitize_filename(out_path.name)
                final = REPORTS_DIR / safe_name
    else:
        final = REPORTS_DIR / f"report{ext}"

    # Ensure the suffix matches the chosen format
    final = final.with_suffix(ext)
    final.parent.mkdir(parents=True, exist_ok=True)
    return final


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    output: Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file. Relative paths are saved under ./reports/. Absolute paths are honoured.",
    ),
    fmt: str = typer.Option(
        "md",
        "--format",
        "-f",
        help="Report format: 'md' for Markdown or 'json'.",
        show_default=True,
        case_sensitive=False,
    ),
):
    """Generate an API usage report in the specified format."""
    if ctx.invoked_subcommand is None:
        _generate_report(output, fmt.lower())


@app.command(name="run")
def run(
    output: str = typer.Option(
        "report.md",
        "--output",
        "-o",
        help="Output file. Relative paths are saved under ./reports/. Absolute paths are honoured.",
    ),
    fmt: str = typer.Option(
        "md",
        "--format",
        "-f",
        help="Report format: 'md' for Markdown or 'json'.",
        show_default=True,
        case_sensitive=False,
    ),
):
    """Generate API usage report (alias for default invocation)."""
    _generate_report(output, fmt.lower())


def _generate_report(output: Optional[str], fmt: str) -> None:
    try:
        path = _resolve_output_path(output, fmt)
    except Exception as e:
        typer.secho(f"[Pendragondi.API] Invalid output path: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=2)

    stats = analyze_calls()
    if fmt == "json":
        report_content = render_json_report(stats)
    else:
        report_content = render_markdown_report(stats)

    try:
        with open(path, "w", encoding="utf-8", errors="strict") as f:
            f.write(report_content)
    except PermissionError:
        typer.secho(f"[Pendragondi.API] Permission denied: {path}", fg=typer.colors.RED)
        raise typer.Exit(code=13)
    except OSError as e:
        typer.secho(f"[Pendragondi.API] Failed to write report: {path} ({e})", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    typer.echo(f"Report saved to {path.resolve()}")


if __name__ == "__main__":
    app()