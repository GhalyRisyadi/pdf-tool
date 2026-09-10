from pathlib import Path
from unittest.mock import patch, MagicMock
from pdftool import extraction


def test_extract_images_success(sample_with_images_pdf, tmp_path):
    out_dir = tmp_path / "extracted_images"
    extraction.extract_images_from_pdf(sample_with_images_pdf, output_dir=out_dir)

    assert out_dir.exists()
    extracted_files = list(out_dir.glob("*.*"))
    assert len(extracted_files) >= 1


def test_extract_images_no_images(sample_pdf, tmp_path, capsys):
    out_dir = tmp_path / "extracted_images"
    extraction.extract_images_from_pdf(sample_pdf, output_dir=out_dir)

    captured = capsys.readouterr().out
    assert "No bitmap/raster images found" in captured
    assert not out_dir.exists()


def test_extract_images_empty_pdf(sample_pdf, capsys):
    mock_doc = MagicMock()
    mock_doc.__len__.return_value = 0

    with patch("fitz.open", return_value=mock_doc):
        extraction.extract_images_from_pdf(sample_pdf)

    captured = capsys.readouterr().out
    assert "PDF document is empty or unreadable" in captured


def test_extract_links_with_links_and_save(sample_with_links_pdf, capsys):
    with patch("builtins.input", return_value="y"):
        extraction.extract_links_from_pdf(sample_with_links_pdf)

    out_file = sample_with_links_pdf.parent / f"{sample_with_links_pdf.stem}_links.txt"
    assert out_file.exists()
    content = out_file.read_text()
    assert "https://example.com/pdftool" in content


def test_extract_links_with_links_no_save(sample_with_links_pdf, capsys):
    with patch("builtins.input", return_value="n"):
        extraction.extract_links_from_pdf(sample_with_links_pdf)

    out_file = sample_with_links_pdf.parent / f"{sample_with_links_pdf.stem}_links.txt"
    assert not out_file.exists()
    captured = capsys.readouterr().out
    assert "Result not saved" in captured


def test_extract_links_no_links(sample_pdf, capsys):
    extraction.extract_links_from_pdf(sample_pdf)
    captured = capsys.readouterr().out
    assert "No external URLs or links found" in captured


def test_extract_tables_with_mock_pdfplumber(sample_pdf):
    # Mock pdfplumber extracting tables
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [[["Col1", "Col2"], ["Val1", "Val2"]]]
    mock_pdf.pages = [mock_page]

    with patch("pdfplumber.open") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_pdf
        extraction.extract_tables_from_pdf(sample_pdf)

    tables_dir = sample_pdf.parent / f"{sample_pdf.stem}_tables"
    assert tables_dir.exists()
    csv_files = list(tables_dir.glob("*.csv"))
    assert len(csv_files) == 1
    content = csv_files[0].read_text()
    assert "Col1,Col2" in content
    assert "Val1,Val2" in content


def test_extract_tables_none_found(sample_pdf, capsys):
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_tables.return_value = []
    mock_pdf.pages = [mock_page]

    with patch("pdfplumber.open") as mock_open:
        mock_open.return_value.__enter__.return_value = mock_pdf
        extraction.extract_tables_from_pdf(sample_pdf)

    captured = capsys.readouterr().out
    assert "No tables found in this PDF" in captured


def test_run_ocr_missing_tesseract_binary(sample_pdf, capsys):
    with patch("shutil.which", return_value=None):
        extraction.run_ocr(sample_pdf)
        captured = capsys.readouterr().out
        assert "Tesseract OCR is not installed" in captured


def test_run_ocr_cancel_option(sample_pdf):
    with patch("shutil.which", return_value="/usr/bin/tesseract"):
        with patch("builtins.input", return_value="0"):
            extraction.run_ocr(sample_pdf)


def test_run_ocr_format1_txt(sample_pdf):
    # Inputs: format 1 (txt), lang "eng", page range "" (all)
    inputs = ["1", "eng", ""]

    mock_img = MagicMock()
    with patch("shutil.which", return_value="/usr/bin/tesseract"), \
         patch("builtins.input", side_effect=inputs), \
         patch("pdf2image.convert_from_path", return_value=[mock_img]), \
         patch("pytesseract.image_to_string", return_value="Extracted text line"):
        extraction.run_ocr(sample_pdf)

    out_file = sample_pdf.parent / f"{sample_pdf.stem}_ocr.txt"
    assert out_file.exists()
    assert "Extracted text line" in out_file.read_text()


def test_run_ocr_format2_searchable_pdf(sample_pdf):
    # Inputs: format 2 (searchable pdf), lang "eng", page range "1"
    inputs = ["2", "eng", "1"]

    mock_img = MagicMock()
    dummy_pdf_bytes = b"%PDF-1.4 mock searchable pdf"
    with patch("shutil.which", return_value="/usr/bin/tesseract"), \
         patch("builtins.input", side_effect=inputs), \
         patch("pdf2image.convert_from_path", return_value=[mock_img]), \
         patch("pytesseract.image_to_pdf_or_hocr", return_value=dummy_pdf_bytes):
        extraction.run_ocr(sample_pdf)

    out_file = sample_pdf.parent / f"{sample_pdf.stem}_searchable.pdf"
    assert out_file.exists()
    assert out_file.read_bytes() == dummy_pdf_bytes
