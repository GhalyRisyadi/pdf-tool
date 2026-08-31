import os
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path


def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_size_result(original: Path, output: Path):
    before_kb = original.stat().st_size / 1024
    after_kb = output.stat().st_size / 1024
    print(f"\n[✓] Output  : {output.name}")
    print(f"    Before  : {before_kb:.0f} KB")
    print(f"    After   : {after_kb:.0f} KB")

def input_file(label: str, extensions: list[str]) -> Path:
    ext_display = "/".join(e.upper() for e in extensions)
    while True:
        raw = input(f"\nPath {label} file [{ext_display}] : ").strip().strip('"').strip("'")
        p = Path(raw)
        if not p.exists():
            print("[!] File not found.")
        elif p.suffix.lower() not in extensions:
            print(f"[!] File must have extension {ext_display}.")
        else:
            return p

def run_libreoffice_convert(path: Path, to: str, outdir: Path, timeout: int=120):
    with tempfile.TemporaryDirectory(prefix="pdftool_lo_profile_") as profile_dir:
        return subprocess.run(
            ["libreoffice", "--headless",
             f"-env:UserInstallation=file://{profile_dir}",
             "--convert-to", to,
             "--outdir", str(outdir), str(path)],
            capture_output=True, text=True, timeout=timeout,
        )

@contextmanager
def ensure_docx(path: Path):  
    if path.suffix.lower() == ".docx":
        yield path
        return

    print(f"\n[*] '{path.name}' is in the old .doc format — converting to .docx first (via LibreOffice)...")
    print("    (This may take longer for large or complex files; please wait.)")

    with tempfile.TemporaryDirectory(prefix="pdftool_") as tmp:
        tmp_dir = Path(tmp)
        try:
            result = run_libreoffice_convert(path, "docx", tmp_dir)
        except FileNotFoundError:
            raise RuntimeError(
                "LibreOffice is not installed.\n"
                "    Ubuntu/Debian : sudo apt install libreoffice\n"
                "    Windows       : https://www.libreoffice.org/download/download/"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Conversion .doc → .docx timed out (file too large or complex).")

        converted = tmp_dir / f"{path.stem}.docx"
        if result.returncode != 0 or not converted.exists():
            detail = (result.stderr or "").strip() or "unknown error"
            raise RuntimeError(f"Failed to convert .doc to .docx: {detail}")

        print("[✓] Conversion complete.\n")
        yield converted

def input_files(label: str, extensions: list[str], min_files: int = 2) -> list[Path]:
    ext_display = "/".join(e.upper() for e in extensions)
    paths: list[Path] = []

    print(f"\nAdd {label} files one by one — the order of input determines the merge order.")
    print("Leave the input blank and press Enter when done.")

    while True:
        raw = input(f"\nFile #{len(paths) + 1} [{ext_display}] (blank = done) : ").strip().strip('"').strip("'")

        if raw == "":
            if len(paths) < min_files:
                print(f"[!] At least {min_files} files are required to merge.")
                continue
            return paths

        p = Path(raw)
        if not p.exists():
            print("[!] File not found.")
        elif p.suffix.lower() not in extensions:
            print(f"[!] File must have extension {ext_display}.")
        elif p in paths:
            print("[!] File already added.")
        else:
            paths.append(p)
            print(f"    [+] {len(paths)}. {p.name}")

def has_javascript(reader):
    try:
        root = reader.trailer.get("/Root", {})
        names = root.get("/Names", {})
        if isinstance(names, dict) and "/JavaScript" in names:
            return True
        return False
    except Exception:
        return False

def get_attachments(reader):
    try:
        return reader.attachments
    except Exception:
        return {}

def count_images(reader):
    try:
        # Accumulate image count across all pages
        return sum(len(page.images) for page in reader.pages)
    except Exception:
        return 0

def get_fonts(reader):
    fonts = set()

    for page in reader.pages:
        resources = page.get("/Resources")

        if not resources:
            continue

        font_dict = resources.get("/Font")

        if not font_dict:
            continue

        for font in font_dict.values():
            font = font.get_object()

            base_font = font.get("/BaseFont")

            if base_font:
                fonts.add(str(base_font))

    return fonts