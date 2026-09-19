"""Checks for Python packages and system executables used by PDFtool."""

import importlib.util
import shutil
from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyStatus:
    name: str
    installed: bool
    kind: str


def check_python_package(name: str) -> DependencyStatus:
    return DependencyStatus(name, importlib.util.find_spec(name) is not None, "python")


def check_executable(name: str) -> DependencyStatus:
    return DependencyStatus(name, shutil.which(name) is not None, "executable")


def project_dependencies() -> list[DependencyStatus]:
    return [
        check_python_package("PIL"),
        check_python_package("pypdf"),
        check_python_package("pdf2image"),
        check_python_package("pikepdf"),
        check_python_package("docx"),
        check_python_package("pdf2docx"),
        check_python_package("docxcompose"),
        check_python_package("fitz"),
        check_python_package("pymupdf4llm"),
        check_python_package("mammoth"),
        check_python_package("pdfplumber"),
        check_python_package("pytesseract"),
        check_python_package("typer"),
        check_python_package("rich"),
        check_python_package("rembg"),
        check_python_package("onnxruntime"),
    ]


def system_dependencies() -> list[DependencyStatus]:
    return [
        check_executable("pdftoppm"),
        check_executable("libreoffice"),
        check_executable("gs"),
        check_executable("qpdf"),
        check_executable("tesseract"),
    ]
