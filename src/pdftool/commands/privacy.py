"""Privacy and security command implementation."""

from pathlib import Path
from typing import List, Optional
import typer
from ..privacy import (
    pdf_strip_metadata,
    jpg_strip_exif,
    pdf_encrypt,
    pdf_unlock,
    pdf_redact,
)
from ..sanitize import pdf_sanitize
from ..pii_scanner import pii_scan
from ..ui import print_error

privacy_app = typer.Typer(help="Privacy and security tools: sanitize, strip metadata, PII scanner, encrypt, decrypt, redact.")


def _register_command_aliases(app: typer.Typer, fn, names: List[str], help_text: str):
    """Registers the same function under multiple command names/aliases."""
    for i, name in enumerate(names):
        h = help_text if i == 0 else f"Alias for '{names[0]}'"
        app.command(name=name, help=h)(fn)


def sanitize_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF file to sanitize", exists=True, readable=True),
):
    """Deep clean and sanitize a PDF (strip JS, attachments, embedded actions)."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Sanitize is only supported for PDF files.")
        raise typer.Exit(code=1)
    pdf_sanitize(file_path)


def scan_pii_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF file to scan for PII", exists=True, readable=True),
):
    """Scan PDF for Personally Identifiable Information (email, phone, credit cards)."""
    if file_path.suffix.lower() != ".pdf":
        print_error("PII scan is only supported for PDF files.")
        raise typer.Exit(code=1)
    pii_scan(file_path)


def strip_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF or JPG file", exists=True, readable=True),
):
    """Strip metadata from PDF or EXIF data from JPG."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        pdf_strip_metadata(file_path)
    elif ext in [".jpg", ".jpeg"]:
        jpg_strip_exif(file_path)
    else:
        print_error(f"Strip metadata only supports PDF and JPG files, not '{ext}'.")
        raise typer.Exit(code=1)


def encrypt_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF file to encrypt", exists=True, readable=True),
):
    """Lock / encrypt a PDF with AES-256 password protection."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Encryption is only supported for PDF files.")
        raise typer.Exit(code=1)
    pdf_encrypt(file_path)


def decrypt_cmd(
    file_path: Path = typer.Argument(..., help="Path to encrypted PDF file to unlock", exists=True, readable=True),
):
    """Unlock an encrypted or restricted PDF file."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Unlock is only supported for PDF files.")
        raise typer.Exit(code=1)
    pdf_unlock(file_path)


def redact_cmd(
    file_path: Path = typer.Argument(..., help="Path to PDF file to redact", exists=True, readable=True),
):
    """Permanently redact sensitive text from a PDF."""
    if file_path.suffix.lower() != ".pdf":
        print_error("Redaction is only supported for PDF files.")
        raise typer.Exit(code=1)
    pdf_redact(file_path)


# Register commands with shorthands
_register_command_aliases(privacy_app, sanitize_cmd, ["sanitize", "san"], "Sanitize PDF (remove JS, actions, attachments)")
_register_command_aliases(privacy_app, scan_pii_cmd, ["scan-pii", "pii"], "Scan PDF for sensitive PII data")
_register_command_aliases(privacy_app, strip_cmd, ["strip", "st"], "Strip metadata / EXIF from PDF or JPG")
_register_command_aliases(privacy_app, encrypt_cmd, ["encrypt", "enc"], "Encrypt / lock PDF with AES-256")
_register_command_aliases(privacy_app, decrypt_cmd, ["decrypt", "dec"], "Decrypt / unlock PDF")
_register_command_aliases(privacy_app, redact_cmd, ["redact", "red"], "Redact sensitive text in PDF")
