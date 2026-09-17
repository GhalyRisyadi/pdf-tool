"""Extraction command implementation (OCR, images, tables, links)."""

from pathlib import Path
from typing import List, Optional
import typer
from ..extraction import (
    extract_images_from_pdf,
    extract_links_from_pdf,
    extract_tables_from_pdf,
    run_ocr,
)
from ..ui import print_error

extract_app = typer.Typer(help="Extract content (images, tables, links, OCR) from documents.")


def _register_command_aliases(app: typer.Typer, fn, names: List[str], help_text: str):
    """Registers the same function under multiple command names/aliases."""
    for i, name in enumerate(names):
        h = help_text if i == 0 else f"Alias for '{names[0]}'"
        app.command(name=name, help=h)(fn)


def ocr_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF or image file", exists=True, readable=True),
    lang: str = typer.Option("eng", "--lang", "-l", help="Language code (eng or ind)"),
    to: str = typer.Option("txt", "--to", "-t", help="Output format: txt or pdf"),
    pages: Optional[str] = typer.Option(None, "--pages", "-p", help="Page range for PDF (e.g. '1-3, 5')"),
):
    """Perform OCR on a PDF or image file."""
    format_code = "2" if to.lower() == "pdf" else "1"
    run_ocr(file_path, output_format=format_code, lang=lang, pages_range=pages)


def images_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF file", exists=True, readable=True),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Directory to save extracted images"),
):
    """Extract embedded images from a PDF file."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Image extraction is only supported for PDF files.")
        raise typer.Exit(code=1)
    extract_images_from_pdf(file_path, output_dir=output_dir)


def tables_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF file", exists=True, readable=True),
):
    """Extract tables from a PDF file into CSV files."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Table extraction is only supported for PDF files.")
        raise typer.Exit(code=1)
    extract_tables_from_pdf(file_path)


def links_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF file", exists=True, readable=True),
):
    """Extract external URLs and links from a PDF file."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Link extraction is only supported for PDF files.")
        raise typer.Exit(code=1)
    extract_links_from_pdf(file_path)


# Register commands with shorthands
_register_command_aliases(extract_app, ocr_cmd, ["ocr"], "Extract text via OCR (Optical Character Recognition)")
_register_command_aliases(extract_app, images_cmd, ["images", "img"], "Extract images from PDF")
_register_command_aliases(extract_app, tables_cmd, ["tables", "tbl"], "Extract tables from PDF into CSV")
_register_command_aliases(extract_app, links_cmd, ["links", "url"], "Extract URLs and links from PDF")
