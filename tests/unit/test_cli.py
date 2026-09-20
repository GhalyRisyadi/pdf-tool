from unittest.mock import patch
from pdftool import cli


def test_welcome(capsys):
    with patch("pdftool.cli.clear"):
        cli.welcome()
    out = capsys.readouterr().out
    assert "I Hate PDF file" in out
    assert "Info File" in out
    assert "Privacy" in out


def test_flows_exit_on_zero():
    with patch("pdftool.cli.clear"), patch("builtins.input", return_value="0"):
        cli.flow_info_file()
        cli.flow_convert_file()
        cli.flow_optimize_file()
        cli.flow_pages_organizer()
        cli.flow_content_extraction()
        cli.flow_privacy()


def test_main_quit():
    with patch("pdftool.cli.welcome"), patch("builtins.input", return_value="Q"):
        cli.main()


def test_main_navigation_and_quit():
    # User selects 1 (Info), exits flow with 0, then selects Q to quit
    with patch("pdftool.cli.welcome"), \
         patch("pdftool.cli.clear"), \
         patch("builtins.input", side_effect=["1", "0", "Q"]):
        cli.main()


def test_main_keyboard_interrupt():
    with patch("pdftool.cli.welcome"), patch("builtins.input", side_effect=KeyboardInterrupt):
        cli.main()


def test_typer_help():
    from typer.testing import CliRunner
    from pdftool.commands import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "PDFtool" in result.output
    assert "convert" in result.output
    assert "cv" in result.output
    assert "doctor" in result.output


def test_typer_subcommands_help():
    from typer.testing import CliRunner
    from pdftool.commands import app

    runner = CliRunner()
    for alias in ["cv", "convert", "opti", "optimize", "pg", "pages", "ex", "extract", "priv", "privacy"]:
        res = runner.invoke(app, [alias, "--help"])
        assert res.exit_code == 0


def test_typer_doctor():
    from typer.testing import CliRunner
    from pdftool.commands import app

    result = CliRunner().invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Python packages:" in result.output
    assert "System tools:" in result.output


def test_doctor_cmd_reports_package_and_system_statuses(capsys):
    from pdftool.commands.doctor import doctor_cmd
    from pdftool.dependencies import DependencyStatus

    packages = [
        DependencyStatus("pypdf", True, "python"),
        DependencyStatus("rembg", False, "python"),
    ]
    executables = [
        DependencyStatus("qpdf", True, "executable"),
        DependencyStatus("gs", False, "executable"),
    ]

    with patch("pdftool.commands.doctor.project_dependencies", return_value=packages), \
         patch("pdftool.commands.doctor.system_dependencies", return_value=executables):
        doctor_cmd()

    output = capsys.readouterr().out
    assert "Python packages:" in output
    assert "  ✓ pypdf" in output
    assert "  ✗ rembg" in output
    assert "System tools:" in output
    assert "  ✓ qpdf" in output
    assert "  ✗ gs" in output


def test_typer_info_and_alias(sample_pdf):
    from typer.testing import CliRunner
    from pdftool.commands import app

    runner = CliRunner()
    # Test canonical
    res1 = runner.invoke(app, ["info", str(sample_pdf)])
    assert res1.exit_code == 0

    # Test shorthand alias 'in'
    res2 = runner.invoke(app, ["in", str(sample_pdf)])
    assert res2.exit_code == 0


def test_typer_convert_shorthand(sample_docx, tmp_path):
    from typer.testing import CliRunner
    from pdftool.commands import app

    runner = CliRunner()
    out_pdf = tmp_path / "converted.pdf"
    res = runner.invoke(app, ["cv", str(sample_docx), "--to", "pdf", "-o", str(out_pdf)])
    assert res.exit_code == 0
    assert out_pdf.exists()


def test_typer_convert_doc_failure_returns_nonzero(sample_pdf):
    from typer.testing import CliRunner
    from pdftool.commands import app
    from pdftool.errors import ConversionError

    with patch(
        "pdftool.commands.convert.pdf_to_doc",
        side_effect=ConversionError("conversion failed"),
    ):
        result = CliRunner().invoke(
            app, ["convert", str(sample_pdf), "--to", "docx"]
        )

    assert result.exit_code == 1
    assert "conversion failed" in result.output


def test_typer_convert_jpg_failure_returns_nonzero(sample_pdf):
    from typer.testing import CliRunner
    from pdftool.commands import app
    from pdftool.errors import DependencyError

    with patch(
        "pdftool.commands.convert.pdf_to_jpg",
        side_effect=DependencyError("Poppler is not installed"),
    ):
        result = CliRunner().invoke(
            app, ["convert", str(sample_pdf), "--to", "jpg"]
        )

    assert result.exit_code == 1
    assert "Poppler is not installed" in result.output


def test_typer_pages_reorder_shorthand(sample_pdf, tmp_path):
    from typer.testing import CliRunner
    from pdftool.commands import app

    runner = CliRunner()
    out_pdf = tmp_path / "reordered.pdf"
    res = runner.invoke(app, ["pg", "re", str(sample_pdf), "--order", "3,2,1", "-o", str(out_pdf)])
    assert res.exit_code == 0
    assert out_pdf.exists()


def test_typer_privacy_sanitize_shorthand(sample_pdf):
    from typer.testing import CliRunner
    from pdftool.commands import app

    runner = CliRunner()
    res = runner.invoke(app, ["priv", "san", str(sample_pdf)])
    assert res.exit_code == 0


def test_main_cli_routing_with_args():
    from unittest.mock import patch

    with patch("sys.argv", ["pdftool", "in", "--help"]), patch("pdftool.commands.app") as mock_app:
        cli.main()
        mock_app.assert_called_once()


def test_main_routes_doctor_to_typer_app():
    with patch("sys.argv", ["pdftool", "doctor"]), \
         patch("pdftool.commands.app") as mock_app, \
         patch("pdftool.cli.interactive_menu") as mock_menu:
        cli.main()

    mock_app.assert_called_once()
    mock_menu.assert_not_called()
