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
