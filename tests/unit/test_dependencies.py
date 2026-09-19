from unittest.mock import patch

from pdftool.dependencies import DependencyStatus, project_dependencies


def test_project_dependencies_checks_all_runtime_packages():
    expected_packages = [
        "PIL",
        "pypdf",
        "pdf2image",
        "pikepdf",
        "docx",
        "pdf2docx",
        "docxcompose",
        "fitz",
        "pymupdf4llm",
        "mammoth",
        "pdfplumber",
        "pytesseract",
        "typer",
        "rich",
        "rembg",
        "onnxruntime",
    ]

    with patch(
        "pdftool.dependencies.check_python_package",
        side_effect=lambda name: DependencyStatus(name, True, "python"),
    ) as check_package:
        statuses = project_dependencies()

    assert [status.name for status in statuses] == expected_packages
    assert [call.args[0] for call in check_package.call_args_list] == expected_packages
