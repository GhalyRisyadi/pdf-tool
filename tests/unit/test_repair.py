from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
from pdftool import repair


def test_blank_ratio():
    # Pure white image has ratio 1.0
    img_white = Image.new("RGB", (10, 10), color=(255, 255, 255))
    assert repair._blank_ratio(img_white) == 1.0

    # Image with half black, half white
    img_mixed = Image.new("L", (2, 2))
    img_mixed.putpixel((0, 0), 255)
    img_mixed.putpixel((0, 1), 255)
    img_mixed.putpixel((1, 0), 0)
    img_mixed.putpixel((1, 1), 0)
    assert repair._blank_ratio(img_mixed) == 0.5


def test_qpdf_check_clean(sample_pdf):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        code, stderr = repair._qpdf_check(sample_pdf)
        assert code == 0
        assert stderr == ""


def test_print_qpdf_issues(capsys):
    err_text = "WARNING: something is wrong\nqpdf: corrupted xref\nignorable line"
    repair._print_qpdf_issues(err_text)
    out = capsys.readouterr().out
    assert "WARNING: something is wrong" in out
    assert "qpdf: corrupted xref" in out
    assert "ignorable line" not in out


def test_pdf_repair_missing_qpdf(sample_pdf, capsys):
    with patch("shutil.which", return_value=None):
        repair.pdf_repair(sample_pdf)
    out = capsys.readouterr().out
    assert "'qpdf' is not installed" in out


def test_pdf_repair_already_clean(sample_pdf, capsys):
    with patch("shutil.which", return_value="/usr/bin/qpdf"), \
         patch("pdftool.repair._qpdf_check", return_value=(0, "")):
        repair.pdf_repair(sample_pdf)

    out = capsys.readouterr().out
    assert "PDF structure is valid" in out


def test_pdf_repair_with_issues_and_repaired(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_repaired.pdf"

    with patch("shutil.which", return_value="/usr/bin/qpdf"), \
         patch("pdftool.repair._qpdf_check", side_effect=[(3, "WARNING: bad xref"), (0, "")]), \
         patch("builtins.input", return_value="y"), \
         patch("pdftool.repair._check_rendered_pages", return_value=[]):
        repair.pdf_repair(sample_pdf)

    assert out.exists()


def test_pdf_repair_cancel(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_repaired.pdf"

    with patch("shutil.which", return_value="/usr/bin/qpdf"), \
         patch("pdftool.repair._qpdf_check", return_value=(2, "ERROR: damaged file")), \
         patch("builtins.input", return_value="n"):
        repair.pdf_repair(sample_pdf)

    assert not out.exists()


def test_check_rendered_pages(sample_pdf):
    # Tests rendered page checking helper
    mock_img = Image.new("RGB", (10, 10), color=(255, 255, 255))
    with patch("pdf2image.convert_from_path", return_value=[mock_img]):
        blank_pages = repair._check_rendered_pages(sample_pdf)
        assert blank_pages == [1]
