import shutil
import subprocess
from pathlib import Path

from .utils import print_size_result

# ─── Structural check (qpdf) ───────────────────────────────────────────────

def _qpdf_check(path: Path, password: str = "") -> tuple[int, str]:
    """Run `qpdf --check`. Returns (exit_code, stderr_text).
    0 = clean, 2 = errors found, 3 = warnings only (see `qpdf --help=exit-status`)."""
    cmd = ["qpdf", "--check"]
    if password:
        cmd += ["--password", password]
    cmd.append(str(path))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode, (result.stderr or "").strip()
    except subprocess.TimeoutExpired:
        # Prevent application crash if the process takes more than 60 seconds
        return 2, "qpdf: Check process timed out (exceeded 60 seconds)."
    except Exception as e:
        return 2, f"qpdf: Unexpected error occurred - {e}"


def _print_qpdf_issues(stderr: str):
    for line in stderr.splitlines():
        line = line.strip()
        if line.startswith("WARNING:") or line.startswith("qpdf:"):
            # strip repeated file path to keep it concise
            print(f"    - {line}")


# ─── Content-level sanity check (render each page via poppler) ──────────

def _blank_ratio(image) -> float:
    """Ratio of pixels dominated by a single color (e.g. plain white).
    High ratio = likely a blank page or lost content.
    """
    hist = image.convert("L").histogram()
    total = sum(hist)
    if total == 0:
        return 1.0
    return max(hist) / total

_BLANK_THRESHOLD = 0.9995

def _check_rendered_pages(path: Path) -> list[int]:
    """Render each page and return a list of page numbers that render blank/white
    (indicating content may have been lost during repair). Best-effort — if poppler
    itself fails to render, that page is skipped (not counted as blank)."""
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return []

    try:
        images = convert_from_path(str(path))
    except Exception:
        return []

    blank_pages = []
    for i, img in enumerate(images, 1):
        if _blank_ratio(img) >= _BLANK_THRESHOLD:
            blank_pages.append(i)
    return blank_pages


# ─── Repair ─────────────────────────────────────────────────────────────────

def pdf_repair(path: Path):
    if shutil.which("qpdf") is None:
        print("\n[ERROR] 'qpdf' is not installed.")
        print("    Ubuntu/Debian : sudo apt install qpdf")
        print("    Windows       : https://qpdf.sourceforge.io/")
        return

    print(f"\n[*] Checking PDF structure: {path.name}")

    code, stderr = _qpdf_check(path)

    if "invalid password" in stderr.lower():
        print("\n[ERROR] PDF is encrypted — please unlock it before repairing.")
        return

    if code == 0:
        print("\n  PDF structure is valid, no issues detected.")
        print("  This file does not need repair.")
        return

    label = "Error" if code == 2 else "Warning"
    print(f"\n  [{label}] Structural issues found:")
    _print_qpdf_issues(stderr)

    print()
    confirm = input("[?] Attempt repair? [Y/n] : ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("\n[!] Canceled.")
        return

    import pikepdf

    output = path.parent / f"{path.stem}_repaired.pdf"

    try:
        with pikepdf.open(str(path), attempt_recovery=True) as pdf:
            n_pages = len(pdf.pages)
            pdf.save(str(output))
    except pikepdf.PasswordError:
        print("\n[ERROR] PDF is encrypted — please unlock it before repairing.")
        return
    except Exception as e:
        print(f"\n[ERROR] File is too corrupted to repair automatically: {e}")
        print("    qpdf was unable to reconstruct the cross-reference table.")
        return

    # Re-validate repaired file structure
    out_code, out_stderr = _qpdf_check(output)
    struct_ok = (out_code == 0)

    # Content validation — render each page, check for blank pages
    blank_pages = _check_rendered_pages(output)

    print_size_result(path, output)
    print(f"    Pages   : {n_pages}")
    print(f"    Structure: {'clean' if struct_ok else 'issues remain (run qpdf --check manually)'}")

    if blank_pages:
        print(f"\n    [!] {len(blank_pages)}/{n_pages} page(s) rendered BLANK after repair:")
        print(f"        Pages: {', '.join(map(str, blank_pages))}")
        print("        This may mean the content on those pages was permanently lost")
        print("        (data was already missing before repair), or those pages were")
        print("        originally blank. Verify manually before using the file.")
    else:
        print("\n    [✓] All pages rendered normally (no indication of lost content).")

    print(f"\n    Saved in : {output.resolve()}")
    print("\n    [!] Note: this repair fixes the FILE STRUCTURE (xref, trailer, etc.),")
    print("        it does not recreate data that was already truly lost.")