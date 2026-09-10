from pathlib import Path
from unittest.mock import patch
from PIL import Image
from pdftool.convert import pdf_to_jpg
from pdftool.compress import jpg_compres


def test_pdf_to_jpg_then_compress(sample_pdf, tmp_path):
    # Step 1: Convert PDF to JPG
    pdf_to_jpg(sample_pdf, dpi=72, quality=80, output_dir=tmp_path)
    jpg_files = list(tmp_path.glob("*.jpg"))
    assert len(jpg_files) >= 1

    first_jpg = jpg_files[0]
    initial_size = first_jpg.stat().st_size

    # Step 2: Compress the generated JPG
    with patch("pdftool.compress.ask_compress_level", return_value="low"):
        jpg_compres(first_jpg)

    compressed_jpg = first_jpg.parent / f"{first_jpg.stem}_compressed.jpg"
    assert compressed_jpg.exists()
    # Verify the compressed image is readable and valid
    with Image.open(compressed_jpg) as img:
        assert img.format == "JPEG"
        assert img.width > 0 and img.height > 0
