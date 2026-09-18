"""Optimize command implementation (compression & repair)."""

from pathlib import Path
from typing import Optional
import typer
from ..compress import pdf_compres, jpg_compres
from ..repair import pdf_repair
from ..convert import pdf_to_pdfa
from ..ui import print_error

def optimize_cmd(
    file_path: Path = typer.Argument(..., help="Path to file to optimize/repair", exists=True, readable=True),
    level: int = typer.Option(2, "--level", "-l", help="Compression level: 1 (Low), 2 (Medium), 3 (High)"),
    repair: bool = typer.Option(False, "--repair", "-r", help="Repair corrupted PDF structure"),
    pdfa: bool = typer.Option(False, "--pdfa", help="Convert PDF to standardized PDF/A archive format"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Custom output path"),
):
    """Compress or repair a document."""
    ext = file_path.suffix.lower()

    if repair:
        if ext != ".pdf":
            print_error("Repair is only supported for PDF files.")
            raise typer.Exit(code=1)
        pdf_repair(file_path, output=output)
        return

    if pdfa:
        if ext != ".pdf":
            print_error("PDF/A conversion is only supported for PDF files.")
            raise typer.Exit(code=1)
        pdf_to_pdfa(file_path, output=output)
        return

    if level not in [1, 2, 3]:
        print_error("Compression level must be 1 (Low), 2 (Medium), or 3 (High).")
        raise typer.Exit(code=1)

    try:
        if ext == ".pdf":
            pdf_compres(file_path, level=level, output=output)
        elif ext in [".jpg", ".jpeg"]:
            jpg_compres(file_path, level=level, output=output)
        else:
            print_error(f"Compression is not supported for '{ext}'. Supported: .pdf, .jpg")
            raise typer.Exit(code=1)
    except Exception as e:
        print_error(f"Optimization failed: {e}")
        raise typer.Exit(code=1)
