"""Pages organizer command implementation."""

from pathlib import Path
from typing import List, Optional
import typer
from ..pages_organizer import (
    merge_pdf,
    split_pdf,
    merge_docx,
    split_docx,
    extract_pages,
    delete_pages,
    rotate_pages,
    reorder_pages,
)
from ..ui import print_error

pages_app = typer.Typer(help="Manage and organize PDF and DOCX pages (merge, split, rotate, etc.).")


def _register_command_aliases(app: typer.Typer, fn, names: List[str], help_text: str):
    """Registers the same function under multiple command names/aliases."""
    for i, name in enumerate(names):
        h = help_text if i == 0 else f"Alias for '{names[0]}'"
        app.command(name=name, help=h)(fn)


def merge_cmd(
    files: List[Path] = typer.Argument(..., help="List of files to merge", exists=True, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output merged file path"),
):
    """Merge multiple PDF or DOCX files into one."""
    if len(files) < 2:
        print_error("You must specify at least two files to merge.")
        raise typer.Exit(code=1)

    first_ext = files[0].suffix.lower()
    if all(f.suffix.lower() == ".pdf" for f in files):
        merge_pdf(files, output=output)
    elif all(f.suffix.lower() in [".docx", ".doc"] for f in files):
        merge_docx(files, output=output)
    else:
        print_error("All files must have the same format (.pdf or .docx) to be merged.")
        raise typer.Exit(code=1)


def split_cmd(
    file_path: Path = typer.Argument(..., help="PDF or DOCX file to split", exists=True, readable=True),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory for split pages"),
):
    """Split a document into individual single-page files."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        split_pdf(file_path, output_dir=output_dir)
    elif ext in [".docx", ".doc"]:
        split_docx(file_path, output_dir=output_dir)
    else:
        print_error("Split only supports .pdf and .docx files.")
        raise typer.Exit(code=1)


def extract_cmd(
    file_path: Path = typer.Argument(..., help="Source PDF file", exists=True, readable=True),
    pages: str = typer.Option(..., "--pages", "-p", help="Pages or range to extract (e.g. '1-3, 5')"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output extracted PDF path"),
):
    """Extract specific pages into a new PDF."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Extract pages is only supported for PDF files.")
        raise typer.Exit(code=1)
    extract_pages(file_path, pages=pages, output=output)


def delete_cmd(
    file_path: Path = typer.Argument(..., help="Source PDF file", exists=True, readable=True),
    pages: str = typer.Option(..., "--pages", "-p", help="Pages or range to delete (e.g. '2, 4-5')"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output PDF path"),
):
    """Delete specific pages from a PDF."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Delete pages is only supported for PDF files.")
        raise typer.Exit(code=1)
    delete_pages(file_path, pages=pages, output=output)


def rotate_cmd(
    file_path: Path = typer.Argument(..., help="Source PDF file", exists=True, readable=True),
    angle: int = typer.Option(90, "--angle", "-a", help="Rotation angle clockwise: 90, 180, or 270"),
    pages: Optional[str] = typer.Option(None, "--pages", "-p", help="Specific pages to rotate (default: all)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output PDF path"),
):
    """Rotate PDF pages."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Rotate pages is only supported for PDF files.")
        raise typer.Exit(code=1)
    rotate_pages(file_path, angle=angle, pages=pages, output=output)


def reorder_cmd(
    file_path: Path = typer.Argument(..., help="Source PDF file", exists=True, readable=True),
    order: str = typer.Option(..., "--order", "-r", help="New page order, comma-separated (e.g. '3,1,2')"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output PDF path"),
):
    """Reorder pages of a PDF document."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Reorder pages is only supported for PDF files.")
        raise typer.Exit(code=1)
    reorder_pages(file_path, order_input=order, output=output)


# Register commands with aliases
_register_command_aliases(pages_app, merge_cmd, ["merge", "mg"], "Merge multiple documents into one")
_register_command_aliases(pages_app, split_cmd, ["split", "sp"], "Split document into single pages")
_register_command_aliases(pages_app, extract_cmd, ["extract", "ext"], "Extract specific pages from a PDF")
_register_command_aliases(pages_app, delete_cmd, ["delete", "del", "rm"], "Delete specific pages from a PDF")
_register_command_aliases(pages_app, rotate_cmd, ["rotate", "rot"], "Rotate pages in a PDF")
_register_command_aliases(pages_app, reorder_cmd, ["reorder", "re"], "Reorder pages in a PDF")
