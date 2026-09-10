from pathlib import Path
from unittest.mock import patch, MagicMock
from pdftool import info


def test_jpg_analysis_with_exif(sample_jpg, capsys):
    info.jpg_analysis(sample_jpg)
    out = capsys.readouterr().out
    assert "JPG Analysis" in out
    assert "Camera" in out
    assert "GPS:" in out


def test_jpg_analysis_no_exif(tmp_path, capsys):
    from PIL import Image
    no_exif_jpg = tmp_path / "plain.jpg"
    img = Image.new("RGB", (50, 50), color=(120, 120, 120))
    img.save(str(no_exif_jpg), "JPEG")

    info.jpg_analysis(no_exif_jpg)
    out = capsys.readouterr().out
    assert "JPG Analysis" in out
    assert "None" in out


def test_doc_info(sample_docx, capsys):
    info.doc_info(sample_docx)
    out = capsys.readouterr().out
    assert "File       :" in out
    assert "Paragraphs :" in out
    assert "Sample DOCX Title" in out
    assert "Antigravity" in out


def test_pdf_analysis_unencrypted(sample_pdf, capsys):
    info.pdf_analysis(sample_pdf)
    out = capsys.readouterr().out
    assert "PDF Analysis" in out
    assert "Pages       : 3" in out
    assert "Sample Document Title" in out
    assert "Antigravity Tester" in out
    assert "Encrypted   : No" in out


def test_pdf_analysis_encrypted_with_password(sample_encrypted_pdf, capsys):
    info.pdf_analysis(sample_encrypted_pdf)
    out = capsys.readouterr().out
    assert "PDF Analysis" in out
    assert "need password to read" in out
    assert "Encrypted   : Yes" in out


def test_pdf_analysis_restricted(sample_restricted_pdf, capsys):
    info.pdf_analysis(sample_restricted_pdf)
    out = capsys.readouterr().out
    assert "PDF Analysis" in out
    assert "Encrypted   : Yes" in out
