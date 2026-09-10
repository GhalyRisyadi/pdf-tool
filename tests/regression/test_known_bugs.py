from pathlib import Path
from unittest.mock import patch
import fitz
from pdftool.pages_organizer import delete_pages, reorder_pages
from pdftool.extraction import run_ocr


def test_cannot_delete_all_pages_bug_prevention(sample_pdf, capsys):
    """Ensure deleting all pages is rejected and does not produce an empty corrupt PDF."""
    out = sample_pdf.parent / f"{sample_pdf.stem}_deleted.pdf"
    # sample_pdf has 3 pages, try to delete pages 1-3
    with patch("builtins.input", return_value="1-3"):
        delete_pages(sample_pdf, output=out)

    assert not out.exists()
    captured = capsys.readouterr().out
    assert "You can't delete ALL pages" in captured


def test_reorder_single_page_pdf(tmp_path, capsys):
    """Ensure reorder on a 1-page PDF notifies user and does not raise exception."""
    doc = fitz.open()
    doc.new_page(width=595, height=842)
    one_page_pdf = tmp_path / "single_page.pdf"
    doc.save(str(one_page_pdf))
    doc.close()

    reorder_pages(one_page_pdf)
    captured = capsys.readouterr().out
    assert "reordering is not needed" in captured


def test_ocr_invalid_page_range_handled_gracefully(sample_pdf, capsys):
    """Ensure entering an out-of-bounds page range in OCR doesn't crash the application."""
    # Format: 1 (txt), Lang: eng, Page range: 99 (invalid since total is 3)
    inputs = ["1", "eng", "99"]
    with patch("shutil.which", return_value="/usr/bin/tesseract"), \
         patch("builtins.input", side_effect=inputs):
        run_ocr(sample_pdf)

    captured = capsys.readouterr().out
    assert "Invalid range" in captured
