"""Root Typer CLI application for PDFtool."""

import importlib.metadata

import typer
from .info import info_cmd
from .convert import convert_cmd
from .optimize import optimize_cmd
from .pages import pages_app
from .extract import extract_app
from .privacy import privacy_app
from .doctor import doctor_cmd

app = typer.Typer(
    help="PDFtool: Privacy-focused, 100% offline document manipulation tool.",
    no_args_is_help=False,
    rich_markup_mode="rich",
)

# Direct commands (with aliases)
app.command(name="doctor", help="Check installed dependencies")(doctor_cmd)

app.command(name="info", help="Check file info and metadata")(info_cmd)
app.command(name="in", help="Alias for 'info'")(info_cmd)

app.command(name="convert", help="Convert documents between PDF, JPG, DOCX, etc.")(convert_cmd)
app.command(name="cv", help="Alias for 'convert'")(convert_cmd)

app.command(name="optimize", help="Compress or repair PDF/JPG files")(optimize_cmd)
app.command(name="opti", help="Alias for 'optimize'")(optimize_cmd)
app.command(name="opt", help="Alias for 'optimize'")(optimize_cmd)

# Sub-command groups (with aliases)
app.add_typer(pages_app, name="pages", help="Organize pages: merge, split, reorder, rotate, delete")
app.add_typer(pages_app, name="pg", help="Alias for 'pages'")

app.add_typer(extract_app, name="extract", help="Extract content: OCR, images, tables, links")
app.add_typer(extract_app, name="ex", help="Alias for 'extract'")

app.add_typer(privacy_app, name="privacy", help="Privacy tools: sanitize, PII scan, encrypt, strip")
app.add_typer(privacy_app, name="priv", help="Alias for 'privacy'")


def _get_version() -> str:
    try:
        return importlib.metadata.version("pdftool")
    except importlib.metadata.PackageNotFoundError:
        return "1.3.0"


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"PDFtool version {_get_version()}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def default_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show PDFtool version.",
        is_eager=True,
        callback=_version_callback,
    ),
) -> None:
    """Entry callback: if no subcommand is passed, start the interactive wizard."""
    if ctx.invoked_subcommand is None and not version:
        from ..cli import interactive_menu
        interactive_menu()
