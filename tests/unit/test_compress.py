from pathlib import Path
from unittest.mock import patch, MagicMock
from pdftool import compress


def test_ask_compress_level():
    with patch("builtins.input", side_effect=["99", "", "1"]):
        assert compress.ask_compress_level() == "low"

    with patch("builtins.input", return_value="2"):
        assert compress.ask_compress_level() == "medium"

    with patch("builtins.input", return_value="3"):
        assert compress.ask_compress_level() == "high"

    with patch("builtins.input", return_value="0"):
        assert compress.ask_compress_level() is None


def test_pdf_compress_high_level(sample_pdf):
    # pikepdf stream compression
    with patch("pdftool.compress.ask_compress_level", return_value="high"):
        compress.pdf_compres(sample_pdf)

    out = sample_pdf.parent / f"{sample_pdf.stem}_compressed.pdf"
    assert out.exists()
    assert out.stat().st_size > 0


def test_pdf_compress_medium_level(sample_pdf):
    # pdf2image rasterization
    with patch("pdftool.compress.ask_compress_level", return_value="medium"):
        compress.pdf_compres(sample_pdf)

    out = sample_pdf.parent / f"{sample_pdf.stem}_compressed.pdf"
    assert out.exists()
    assert out.stat().st_size > 0


def test_pdf_compress_cancel(sample_pdf):
    with patch("pdftool.compress.ask_compress_level", return_value=None):
        compress.pdf_compres(sample_pdf)

    out = sample_pdf.parent / f"{sample_pdf.stem}_compressed.pdf"
    assert not out.exists()


def test_jpg_compress(sample_jpg):
    with patch("pdftool.compress.ask_compress_level", return_value="medium"):
        compress.jpg_compres(sample_jpg)

    out = sample_jpg.parent / f"{sample_jpg.stem}_compressed.jpg"
    assert out.exists()
    assert out.stat().st_size > 0


def test_jpg_compress_cancel(sample_jpg):
    with patch("pdftool.compress.ask_compress_level", return_value=None):
        compress.jpg_compres(sample_jpg)

    out = sample_jpg.parent / f"{sample_jpg.stem}_compressed.jpg"
    assert not out.exists()


def test_doc_compress(sample_docx):
    with patch("pdftool.compress.ask_compress_level", return_value="low"):
        compress.doc_compres(sample_docx)

    out = sample_docx.parent / f"{sample_docx.stem}_compressed.docx"
    assert out.exists()
    assert out.stat().st_size > 0


def test_doc_compress_cancel(sample_docx):
    with patch("pdftool.compress.ask_compress_level", return_value=None):
        compress.doc_compres(sample_docx)

    out = sample_docx.parent / f"{sample_docx.stem}_compressed.docx"
    assert not out.exists()


def test_print_result(tmp_path, capsys):
    f = tmp_path / "compressed.pdf"
    f.write_bytes(b"x" * 1024)
    compress._print_result(f, 2.0)
    out = capsys.readouterr().out
    assert "Compressed: compressed.pdf" in out
    assert "Saved  :" in out
