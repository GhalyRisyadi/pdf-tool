from unittest.mock import patch
import pikepdf
from pdftool.privacy import pdf_encrypt, pdf_unlock


def test_encrypt_then_unlock_flow(sample_pdf):
    # Step 1: Encrypt the sample PDF
    with patch("builtins.input", return_value="1"), \
         patch("getpass.getpass", side_effect=["mypassword123", "mypassword123"]):
        pdf_encrypt(sample_pdf)

    encrypted_pdf = sample_pdf.parent / f"{sample_pdf.stem}_encrypted.pdf"
    assert encrypted_pdf.exists()

    # Verify that pikepdf cannot open it without password
    try:
        with pikepdf.open(str(encrypted_pdf)):
            can_open = True
    except pikepdf.PasswordError:
        can_open = False
    assert can_open is False

    # Step 2: Unlock the encrypted PDF
    with patch("builtins.input", return_value="1"), \
         patch("getpass.getpass", return_value="mypassword123"):
        pdf_unlock(encrypted_pdf)

    unlocked_pdf = encrypted_pdf.parent / f"{encrypted_pdf.stem}_unlocked.pdf"
    assert unlocked_pdf.exists()

    # Step 3: Verify the unlocked PDF opens cleanly without any password
    with pikepdf.open(str(unlocked_pdf)) as pdf:
        assert len(pdf.pages) == 3
