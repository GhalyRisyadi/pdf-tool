import shutil
from pathlib import Path
from unittest.mock import patch
from pypdf import PdfReader
from docx import Document
from pdftool import pages_organizer


def test_parse_ranges():
    # Empty / "all"
    assert pages_organizer._parse_ranges("", 3) == [(1, 1), (2, 2), (3, 3)]
    assert pages_organizer._parse_ranges("all", 3) == [(1, 1), (2, 2), (3, 3)]

    # Valid ranges
    assert pages_organizer._parse_ranges("1-2, 3", 3) == [(1, 2), (3, 3)]

    # Invalid range: start > end
    assert pages_organizer._parse_ranges("3-1", 3) is None
    # Invalid: out of bounds
    assert pages_organizer._parse_ranges("1-5", 3) is None
    # Invalid: non-digit
    assert pages_organizer._parse_ranges("abc", 3) is None


def test_flatten_ranges():
    assert pages_organizer._flatten_ranges([(1, 2), (2, 3), (5, 5)]) == [1, 2, 3, 5]


def test_parse_reorder():
    # Reverse
    assert pages_organizer._parse_reorder("reverse", 3) == [3, 2, 1]
    assert pages_organizer._parse_reorder("rev", 3) == [3, 2, 1]

    # Specific order with comma and dash
    assert pages_organizer._parse_reorder("2, 1, 3", 3) == [2, 1, 3]
    assert pages_organizer._parse_reorder("2-3, 1", 3) == [2, 3, 1]

    # Invalid
    assert pages_organizer._parse_reorder("", 3) is None
    assert pages_organizer._parse_reorder("4, 1", 3) is None


def test_merge_pdf(sample_pdf, tmp_path):
    p1 = tmp_path / "part1.pdf"
    p2 = tmp_path / "part2.pdf"
    shutil.copy(sample_pdf, p1)
    shutil.copy(sample_pdf, p2)

    out = tmp_path / "merged.pdf"
    pages_organizer.merge_pdf([p1, p2], output=out)

    assert out.exists()
    reader = PdfReader(str(out))
    assert len(reader.pages) == 6


def test_split_pdf(sample_pdf, tmp_path):
    out_dir = tmp_path / "split_out"
    with patch("builtins.input", return_value="1-2, 3"):
        pages_organizer.split_pdf(sample_pdf, output_dir=out_dir)

    assert out_dir.exists()
    files = sorted(out_dir.glob("*.pdf"))
    assert len(files) == 2


def test_extract_pages(sample_pdf, tmp_path):
    out = tmp_path / "extracted.pdf"
    with patch("builtins.input", return_value="1, 3"):
        pages_organizer.extract_pages(sample_pdf, output=out)

    assert out.exists()
    reader = PdfReader(str(out))
    assert len(reader.pages) == 2


def test_delete_pages(sample_pdf, tmp_path):
    out = tmp_path / "deleted.pdf"
    with patch("builtins.input", return_value="2"):
        pages_organizer.delete_pages(sample_pdf, output=out)

    assert out.exists()
    reader = PdfReader(str(out))
    assert len(reader.pages) == 2


def test_rotate_pages(sample_pdf, tmp_path):
    out = tmp_path / "rotated.pdf"
    # Rotate pages 1-2 by 90 degrees (option 1)
    with patch("builtins.input", side_effect=["1-2", "1"]):
        pages_organizer.rotate_pages(sample_pdf, output=out)

    assert out.exists()
    reader = PdfReader(str(out))
    assert reader.pages[0].rotation == 90
    assert reader.pages[1].rotation == 90
    assert reader.pages[2].rotation == 0


def test_reorder_pages(sample_pdf, tmp_path):
    out = tmp_path / "reordered.pdf"
    with patch("builtins.input", return_value="3, 1, 2"):
        pages_organizer.reorder_pages(sample_pdf, output=out)

    assert out.exists()
    reader = PdfReader(str(out))
    assert len(reader.pages) == 3


def test_merge_docx(sample_docx, tmp_path):
    d1 = tmp_path / "d1.docx"
    d2 = tmp_path / "d2.docx"
    shutil.copy(sample_docx, d1)
    shutil.copy(sample_docx, d2)

    out = tmp_path / "merged.docx"
    pages_organizer.merge_docx([d1, d2], output=out)

    assert out.exists()
    merged = Document(str(out))
    assert len(merged.paragraphs) >= 2


def test_split_docx(sample_docx, tmp_path):
    out_dir = tmp_path / "docx_split"
    pages_organizer.split_docx(sample_docx, output_dir=out_dir)

    assert out_dir.exists()
    parts = list(out_dir.glob("*.docx"))
    assert len(parts) >= 2
