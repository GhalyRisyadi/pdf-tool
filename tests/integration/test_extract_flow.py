from unittest.mock import patch
from PIL import Image
from pdftool.extraction import extract_links_from_pdf, extract_images_from_pdf


def test_extract_flow(sample_with_links_pdf, sample_with_images_pdf, tmp_path):
    # Step 1: Extract links
    with patch("builtins.input", return_value="y"):
        extract_links_from_pdf(sample_with_links_pdf)

    links_file = sample_with_links_pdf.parent / f"{sample_with_links_pdf.stem}_links.txt"
    assert links_file.exists()
    assert "https://example.com/pdftool" in links_file.read_text()

    # Step 2: Extract images
    img_out_dir = tmp_path / "extracted_images"
    extract_images_from_pdf(sample_with_images_pdf, output_dir=img_out_dir)

    assert img_out_dir.exists()
    images = list(img_out_dir.glob("*.*"))
    assert len(images) >= 1
    with Image.open(images[0]) as img:
        assert img.width > 0 and img.height > 0
