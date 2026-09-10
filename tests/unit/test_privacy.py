from pathlib import Path
from unittest.mock import patch
import pikepdf
from pdftool import privacy


def test_pdf_strip_metadata(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_clean.pdf"
    with patch("builtins.input", return_value="y"):
        privacy.pdf_strip_metadata(sample_pdf)

    assert out.exists()
    with pikepdf.open(str(out)) as pdf:
        assert not pdf.docinfo.get("/Title")
        assert not pdf.docinfo.get("/Author")


def test_pdf_strip_metadata_cancel(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_clean.pdf"
    with patch("builtins.input", return_value="n"):
        privacy.pdf_strip_metadata(sample_pdf)

    assert not out.exists()


def test_jpg_strip_exif(sample_jpg):
    out = sample_jpg.parent / f"{sample_jpg.stem}_clean.jpg"
    with patch("builtins.input", return_value="y"):
        privacy.jpg_strip_exif(sample_jpg)

    assert out.exists()


def test_jpg_strip_exif_cancel(sample_jpg):
    out = sample_jpg.parent / f"{sample_jpg.stem}_clean.jpg"
    with patch("builtins.input", return_value="n"):
        privacy.jpg_strip_exif(sample_jpg)

    assert not out.exists()


def test_pdf_encrypt_choice1_password(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_encrypted.pdf"
    with patch("builtins.input", return_value="1"), \
         patch("getpass.getpass", side_effect=["pass123", "pass123"]):
        privacy.pdf_encrypt(sample_pdf)

    assert out.exists()
    # Verify file is password protected
    with pikepdf.open(str(out), password="pass123") as pdf:
        assert len(pdf.pages) == 3


def test_pdf_encrypt_choice2_restriction(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_encrypted.pdf"
    with patch("builtins.input", return_value="2"), \
         patch("getpass.getpass", side_effect=["owner123", "owner123"]):
        privacy.pdf_encrypt(sample_pdf)

    assert out.exists()
    with pikepdf.open(str(out)) as pdf:
        assert pdf.encryption is not None


def test_pdf_encrypt_choice3_password_and_restriction(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_encrypted.pdf"
    with patch("builtins.input", return_value="3"), \
         patch("getpass.getpass", side_effect=["user123", "owner123"]):
        privacy.pdf_encrypt(sample_pdf)

    assert out.exists()


def test_pdf_encrypt_cancel(sample_pdf):
    with patch("builtins.input", return_value="0"):
        privacy.pdf_encrypt(sample_pdf)

    out = sample_pdf.parent / f"{sample_pdf.stem}_encrypted.pdf"
    assert not out.exists()


def test_pdf_unlock_mode1_remove_password(sample_encrypted_pdf):
    out = sample_encrypted_pdf.parent / f"{sample_encrypted_pdf.stem}_unlocked.pdf"
    with patch("builtins.input", return_value="1"), \
         patch("getpass.getpass", return_value="secret123"):
        privacy.pdf_unlock(sample_encrypted_pdf)

    assert out.exists()
    # Can open without password
    with pikepdf.open(str(out)) as pdf:
        assert len(pdf.pages) == 3


def test_pdf_unlock_mode2_remove_restrictions(sample_restricted_pdf):
    out = sample_restricted_pdf.parent / f"{sample_restricted_pdf.stem}_unlocked.pdf"
    with patch("builtins.input", return_value="2"):
        privacy.pdf_unlock(sample_restricted_pdf)

    assert out.exists()


def test_pdf_unlock_mode3_remove_both(sample_encrypted_pdf):
    out = sample_encrypted_pdf.parent / f"{sample_encrypted_pdf.stem}_unlocked.pdf"
    with patch("builtins.input", return_value="3"), \
         patch("getpass.getpass", return_value="secret123"):
        privacy.pdf_unlock(sample_encrypted_pdf)

    assert out.exists()


def test_pdf_unlock_unencrypted_doc(sample_pdf, capsys):
    privacy.pdf_unlock(sample_pdf)
    out = capsys.readouterr().out
    assert "This file is not encrypted" in out


def test_pdf_redact_success(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_redacted.pdf"
    # Search for "Hello", confirm "y"
    with patch("builtins.input", side_effect=["Hello", "y"]):
        privacy.pdf_redact(sample_pdf)

    assert out.exists()


def test_pdf_redact_not_found(sample_pdf, capsys):
    with patch("builtins.input", return_value="NONEXISTENTTEXT12345"):
        privacy.pdf_redact(sample_pdf)

    out = capsys.readouterr().out
    assert "No matching text found" in out


def test_pdf_redact_cancel(sample_pdf):
    out = sample_pdf.parent / f"{sample_pdf.stem}_redacted.pdf"
    with patch("builtins.input", side_effect=["Hello", "n"]):
        privacy.pdf_redact(sample_pdf)

    assert not out.exists()
