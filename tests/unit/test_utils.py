from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from pypdf import PdfReader
from pdftool import utils


def test_clear():
    with patch("os.system") as mock_sys:
        utils.clear()
        mock_sys.assert_called_once()


def test_print_size_result(tmp_path, capsys):
    f1 = tmp_path / "orig.txt"
    f2 = tmp_path / "out.txt"
    f1.write_bytes(b"A" * 2048)
    f2.write_bytes(b"B" * 1024)

    utils.print_size_result(f1, f2)
    captured = capsys.readouterr().out
    assert "Output  : out.txt" in captured
    assert "Before  : 2 KB" in captured
    assert "After   : 1 KB" in captured


def test_input_file_valid(tmp_path):
    f = tmp_path / "doc.pdf"
    f.touch()
    with patch("builtins.input", return_value=str(f)):
        res = utils.input_file("PDF", [".pdf"])
        assert res == f


def test_input_file_reprompts(tmp_path):
    non_existent = tmp_path / "does_not_exist.pdf"
    wrong_ext = tmp_path / "file.txt"
    wrong_ext.touch()
    valid = tmp_path / "file.pdf"
    valid.touch()

    # Sequence of inputs: non-existent -> wrong ext -> valid
    with patch("builtins.input", side_effect=[str(non_existent), str(wrong_ext), str(valid)]):
        res = utils.input_file("PDF", [".pdf"])
        assert res == valid


def test_input_files(tmp_path):
    f1 = tmp_path / "1.pdf"
    f2 = tmp_path / "2.pdf"
    f1.touch()
    f2.touch()

    # Inputs: blank first (fails min_files) -> f1 -> f1 again (duplicate) -> f2 -> blank (done)
    with patch("builtins.input", side_effect=["", str(f1), str(f1), str(f2), ""]):
        res = utils.input_files("PDF", [".pdf"], min_files=2)
        assert res == [f1, f2]


def test_ensure_docx_with_docx(sample_docx):
    with utils.ensure_docx(sample_docx) as path:
        assert path == sample_docx


def test_ensure_docx_with_doc_successful(tmp_path):
    doc_path = tmp_path / "test.doc"
    doc_path.touch()

    def mock_lo_convert(p, to, outdir, timeout=120):
        # Create converted file in outdir
        (outdir / "test.docx").touch()
        mock_res = MagicMock()
        mock_res.returncode = 0
        return mock_res

    with patch("pdftool.utils.run_libreoffice_convert", side_effect=mock_lo_convert):
        with utils.ensure_docx(doc_path) as converted:
            assert converted.name == "test.docx"
            assert converted.exists()


def test_ensure_docx_missing_libreoffice(tmp_path):
    doc_path = tmp_path / "test.doc"
    doc_path.touch()

    with patch("pdftool.utils.run_libreoffice_convert", side_effect=FileNotFoundError):
        with pytest.raises(RuntimeError, match="LibreOffice is not installed"):
            with utils.ensure_docx(doc_path):
                pass


def test_has_javascript(sample_pdf, sample_active_pdf):
    reader_clean = PdfReader(str(sample_pdf))
    assert not utils.has_javascript(reader_clean)

    reader_active = PdfReader(str(sample_active_pdf))
    assert utils.has_javascript(reader_active)


def test_get_attachments(sample_pdf):
    from collections.abc import Mapping
    reader = PdfReader(str(sample_pdf))
    attachments = utils.get_attachments(reader)
    assert isinstance(attachments, Mapping)


def test_count_images(sample_pdf, sample_with_images_pdf):
    reader_no_img = PdfReader(str(sample_pdf))
    assert utils.count_images(reader_no_img) == 0

    reader_img = PdfReader(str(sample_with_images_pdf))
    assert utils.count_images(reader_img) >= 1


def test_get_fonts(sample_pdf):
    reader = PdfReader(str(sample_pdf))
    fonts = utils.get_fonts(reader)
    assert isinstance(fonts, set)


def test_run_libreoffice_convert(tmp_path):
    input_file = tmp_path / "doc.txt"
    input_file.touch()
    outdir = tmp_path / "out"
    outdir.mkdir()

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        res = utils.run_libreoffice_convert(input_file, "pdf", outdir)
        mock_run.assert_called_once()
        assert res.returncode == 0
