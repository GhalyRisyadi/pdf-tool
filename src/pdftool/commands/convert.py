"""Convert command implementation."""

from pathlib import Path
from typing import Optional
import typer
from ..convert import (
    markdown_to_pdf,
    pdf_to_jpg,
    pdf_to_doc,
    pdf_to_text,
    pdf_to_markdown,
    pdf_to_html,
    jpg_to_pdf,
    jpg_to_png,
    png_to_jpg,
    doc_to_pdf,
    pdf_to_pdfa,
)
from ..ui import print_error

def convert_cmd(
    file_path: Path = typer.Argument(..., help="Source file path to convert", exists=True, readable=True),
    to: str = typer.Option(..., "--to", "-t", help="Target format (e.g. pdf, jpg, docx, txt, md, html, png, pdfa)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Custom output path"),
):
    """Convert a file to another format."""
    ext = file_path.suffix.lower()
    target = to.lower().strip().lstrip(".")

    try:
        if ext == ".pdf":
            if target in ["jpg", "jpeg"]:
                pdf_to_jpg(file_path, output_dir=output)
            elif target in ["doc", "docx"]:
                pdf_to_doc(file_path, output_path=output)
            elif target in ["txt", "text"]:
                pdf_to_text(file_path, output_path=output)
            elif target in ["md", "markdown"]:
                pdf_to_markdown(file_path, output_path=output)
            elif target == "html":
                pdf_to_html(file_path, output_path=output)
            elif target == "pdfa":
                pdf_to_pdfa(file_path, output_path=output)
            else:
                print_error(f"Cannot convert PDF to '{target}'. Supported: jpg, docx, txt, md, html, pdfa")
                raise typer.Exit(code=1)

        elif ext in [".jpg", ".jpeg"]:
            if target == "pdf":
                jpg_to_pdf(file_path, output_path=output)
            elif target == "png":
                jpg_to_png(file_path, output_path=output)
            else:
                print_error(f"Cannot convert JPG to '{target}'. Supported: pdf, png")
                raise typer.Exit(code=1)

        elif ext == ".png":
            if target in ["jpg", "jpeg"]:
                png_to_jpg(file_path, output_path=output)
            else:
                print_error(f"Cannot convert PNG to '{target}'. Supported: jpg")
                raise typer.Exit(code=1)

        elif ext in [".doc", ".docx"]:
            if target == "pdf":
                doc_to_pdf(file_path, output_dir=output)
            else:
                print_error(f"Cannot convert DOC/DOCX to '{target}'. Supported: pdf")
                raise typer.Exit(code=1)

        elif ext in [".md", ".markdown"]:
            if target == "pdf":
                markdown_to_pdf(file_path, output_dir=output)
            else:
                print_error(f"Cannot convert Markdown to '{target}'. Supported: pdf")
                raise typer.Exit(code=1)

        else:
            print_error(f"Unsupported source format '{ext}'.")
            raise typer.Exit(code=1)

    except Exception as e:
        print_error(f"Conversion failed: {e}")
        raise typer.Exit(code=1)
