from pathlib import Path
from unittest.mock import patch
import pikepdf
from pdftool import sanitize


def test_action_label():
    assert sanitize._action_label({"/S": "/JavaScript"}) == "JavaScript"
    assert sanitize._action_label({"/S": "/URI"}) == "URI (open external link)"
    assert sanitize._action_label({}) is None


def test_walk_name_tree():
    # Construct a simple name tree dictionary
    tree = {"/Names": ["Item1", "Val1", "Item2", "Val2"]}
    items = list(sanitize._walk_name_tree(tree))
    assert len(items) == 2
    assert items[0] == ("Item1", "Val1")
    assert items[1] == ("Item2", "Val2")


def test_scan_and_print_findings(sample_active_pdf):
    with pikepdf.open(str(sample_active_pdf)) as pdf:
        findings = sanitize._scan(pdf)
        assert len(findings["open_action"]) > 0 or len(findings["javascript"]) > 0
        has_active = sanitize._print_findings(findings)
        assert has_active is True


def test_scan_annot_actions(tmp_path):
    # Create PDF with annotation action
    pdf = pikepdf.new()
    page = pdf.add_blank_page()
    annot = pikepdf.Dictionary(
        Subtype=pikepdf.Name.Link,
        Rect=pikepdf.Array([0, 0, 100, 100]),
        A=pikepdf.Dictionary(S=pikepdf.Name.URI, URI=pikepdf.String("http://example.com")),
        AA=pikepdf.Dictionary(D=pikepdf.Dictionary(S=pikepdf.Name.JavaScript, JS=pikepdf.String("x=1;")))
    )
    page.Annots = pikepdf.Array([annot])
    test_pdf = tmp_path / "annot_test.pdf"
    pdf.save(str(test_pdf))

    with pikepdf.open(str(test_pdf)) as p:
        findings = sanitize._scan(p)
        assert len(findings["annot_actions"]) >= 1

    # Also test sanitize on it
    with patch("builtins.input", return_value="y"):
        sanitize.pdf_sanitize(test_pdf)

    sanitized_pdf = tmp_path / "annot_test_sanitized.pdf"
    assert sanitized_pdf.exists()


def test_pdf_sanitize_success(sample_active_pdf):
    out = sample_active_pdf.parent / f"{sample_active_pdf.stem}_sanitized.pdf"
    with patch("builtins.input", return_value="y"):
        sanitize.pdf_sanitize(sample_active_pdf)

    assert out.exists()
    # Verify active content is gone
    with pikepdf.open(str(out)) as pdf:
        findings = sanitize._scan(pdf)
        assert len(findings["open_action"]) == 0
        assert len(findings["javascript"]) == 0


def test_pdf_sanitize_cancel(sample_active_pdf):
    out = sample_active_pdf.parent / f"{sample_active_pdf.stem}_sanitized.pdf"
    with patch("builtins.input", return_value="n"):
        sanitize.pdf_sanitize(sample_active_pdf)

    assert not out.exists()


def test_pdf_sanitize_already_clean(sample_pdf, capsys):
    sanitize.pdf_sanitize(sample_pdf)
    out = capsys.readouterr().out
    assert "No active content found" in out
