"""Info command implementation."""

from pathlib import Path
import typer
from ..info import pdf_analysis, jpg_analysis, doc_info
from ..utils import ensure_docx
from ..ui import print_error, print_banner

def info_cmd(
    file_path: Path = typer.Argument(..., help="Path to the document/image file", exists=True, readable=True),
):
    """Analyze and display document metadata."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        pdf_analysis(file_path)
    elif ext in [".jpg", ".jpeg"]:
        jpg_analysis(file_path)
    elif ext in [".docx", ".doc"]:
        try:
            with ensure_docx(file_path) as docx_path:
                doc_info(docx_path, origin=file_path)
        except Exception as e:
            print_error(f"Error reading document: {e}")
            raise typer.Exit(code=1)
    else:
        print_error(f"Unsupported file type '{ext}'. Supported: .pdf, .jpg, .jpeg, .docx, .doc")
        raise typer.Exit(code=1)
