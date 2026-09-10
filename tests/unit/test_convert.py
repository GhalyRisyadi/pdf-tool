from pathlib import Path
from unittest.mock import patch, MagicMock
from pdftool import convert


def test_pdf_to_jpg(sample_pdf, tmp_path):
    convert.pdf_to_jpg(sample_pdf, output_dir=tmp_path)
    jpgs = list(tmp_path.glob("*.jpg"))
    assert len(jpgs) >= 1


def test_pdf_to_doc(sample_pdf, tmp_path):
    out = tmp_path / "out.docx"
    with patch("pdf2docx.Converter") as mock_conv:
        mock_instance = mock_conv.return_value
        mock_instance.convert.side_effect = lambda path: Path(path).touch()
        convert.pdf_to_doc(sample_pdf, output_path=out)
        mock_instance.convert.assert_called_once()
        mock_instance.close.assert_called_once()
    assert out.exists()


def test_pdf_to_text(sample_pdf, tmp_path):
    out = tmp_path / "out.txt"
    convert.pdf_to_text(sample_pdf, output_path=out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "Hello world from pdftool" in content


def test_pdf_to_markdown(sample_pdf, tmp_path):
    out = tmp_path / "out.md"
    convert.pdf_to_markdown(sample_pdf, output_path=out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert len(content) > 0


def test_pdf_to_html(sample_pdf, tmp_path):
    out = tmp_path / "out.html"
    with patch("pdf2docx.Converter") as mock_conv, \
         patch("mammoth.convert_to_html") as mock_mammoth:
        mock_instance = mock_conv.return_value
        mock_instance.convert.side_effect = lambda p: Path(p).write_bytes(b"PK mock docx")
        mock_mammoth_res = MagicMock()
        mock_mammoth_res.value = "<p>Converted paragraph</p>"
        mock_mammoth_res.messages = []
        mock_mammoth.return_value = mock_mammoth_res

        convert.pdf_to_html(sample_pdf, output_path=out)

    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
    assert "<p>Converted paragraph</p>" in content


def test_ask_pdfa_level():
    with patch("builtins.input", side_effect=["99", "", "2"]):
        assert convert._ask_pdfa_level() == "2"

    with patch("builtins.input", return_value="0"):
        assert convert._ask_pdfa_level() is None


def test_pdf_to_pdfa_missing_ghostscript(sample_pdf, capsys):
    with patch("shutil.which", return_value=None):
        convert.pdf_to_pdfa(sample_pdf)
        captured = capsys.readouterr().out
        assert "Ghostscript is not installed" in captured


def test_pdf_to_pdfa_success(sample_pdf, tmp_path):
    out = tmp_path / "out_pdfa.pdf"

    def mock_gs_run(cmd, capture_output, text, timeout):
        # Create output file
        out.touch()
        res = MagicMock()
        res.returncode = 0
        return res

    with patch("shutil.which", return_value="/usr/bin/gs"), \
         patch("pdftool.convert._ask_pdfa_level", return_value="2"), \
         patch("subprocess.run", side_effect=mock_gs_run):
        convert.pdf_to_pdfa(sample_pdf, output_path=out)

    assert out.exists()


def test_jpg_to_pdf(sample_jpg, tmp_path):
    out = tmp_path / "out.pdf"
    convert.jpg_to_pdf(sample_jpg, output_path=out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_jpg_to_png(sample_jpg, tmp_path):
    out = tmp_path / "out.png"
    convert.jpg_to_png(sample_jpg, output_path=out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_png_to_jpg(sample_png, tmp_path):
    out = tmp_path / "out.jpg"
    convert.png_to_jpg(sample_png, output_path=out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_doc_to_pdf(sample_docx, tmp_path):
    def mock_lo(path, to, outdir, timeout=120):
        (outdir / f"{path.stem}.pdf").touch()
        res = MagicMock()
        res.returncode = 0
        return res

    with patch("pdftool.convert.run_libreoffice_convert", side_effect=mock_lo):
        convert.doc_to_pdf(sample_docx, output_dir=tmp_path)

    out = tmp_path / f"{sample_docx.stem}.pdf"
    assert out.exists()


def test_markdown_to_pdf(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test markdown")

    def mock_lo(path, to, outdir, timeout=120):
        (outdir / f"{path.stem}.pdf").touch()
        res = MagicMock()
        res.returncode = 0
        return res

    with patch("pdftool.convert.run_libreoffice_convert", side_effect=mock_lo):
        convert.markdown_to_pdf(md_file, output_dir=tmp_path)

    out = tmp_path / f"{md_file.stem}.pdf"
    assert out.exists()
