from pathlib import Path
from unittest.mock import patch
from pdftool import pii_scanner


def test_luhn_valid():
    # Valid credit card number (Luhn check)
    assert pii_scanner._luhn_valid("4532015099345677")
    # Invalid number
    assert not pii_scanner._luhn_valid("1234567812345678")


def test_nik_plausible():
    # Valid NIK structure (DD/MM within bounds)
    assert pii_scanner._nik_plausible("3171010101900001")
    # Female birthdate (DD + 40)
    assert pii_scanner._nik_plausible("3171014501900001")
    # Invalid length
    assert not pii_scanner._nik_plausible("12345")
    # Invalid month 13
    assert not pii_scanner._nik_plausible("3171010113900001")


def test_classify_digit16():
    # NIK only (month valid, but fails Luhn)
    nik = "3171010101900001"
    assert pii_scanner._classify_digit16(nik) == "nik"

    # Luhn card only (fails NIK date)
    card = "4532015099345677"
    assert pii_scanner._classify_digit16(card) == "card"

    # Ambiguous (passes both Luhn and NIK)
    ambiguous = "4532015012345671"
    assert pii_scanner._classify_digit16(ambiguous) == "digit16_ambiguous"


def test_scan_text():
    sample_text = (
        "Email: test@example.com\n"
        "Phone: 081234567890\n"
        "IP: 192.168.1.1\n"
        "NIK: 3171010101900001\n"
    )
    findings = pii_scanner._scan_text(sample_text)
    assert "test@example.com" in findings["email"]
    assert "081234567890" in findings["phone"]
    assert "192.168.1.1" in findings["ip"]
    assert "3171010101900001" in findings["nik"]


def test_pii_scan_with_redaction(sample_pii_pdf):
    out = sample_pii_pdf.parent / f"{sample_pii_pdf.stem}_pii_redacted.pdf"
    with patch("builtins.input", return_value="y"):
        pii_scanner.pii_scan(sample_pii_pdf)

    assert out.exists()
    assert out.stat().st_size > 0


def test_pii_scan_cancel_redaction(sample_pii_pdf):
    out = sample_pii_pdf.parent / f"{sample_pii_pdf.stem}_pii_redacted.pdf"
    with patch("builtins.input", return_value="n"):
        pii_scanner.pii_scan(sample_pii_pdf)

    assert not out.exists()


def test_pii_scan_no_pii_found(sample_pdf, capsys):
    pii_scanner.pii_scan(sample_pdf)
    captured = capsys.readouterr().out
    assert "No PII found" in captured


def test_pii_scan_encrypted_pdf(sample_encrypted_pdf, capsys):
    pii_scanner.pii_scan(sample_encrypted_pdf)
    captured = capsys.readouterr().out
    assert "Encrypted PDF" in captured
