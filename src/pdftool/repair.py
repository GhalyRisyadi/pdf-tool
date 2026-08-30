import shutil
import subprocess
from pathlib import Path

from .utils import print_size_result

# ─── Structural check (qpdf) ───────────────────────────────────────────────

def _qpdf_check(path: Path, password: str = "") -> tuple[int, str]:
    """Jalankan `qpdf --check`. Return (exit_code, stderr_text).
    0 = bersih, 2 = ada error, 3 = ada warning (lihat `qpdf --help=exit-status`)."""
    cmd = ["qpdf", "--check"]
    if password:
        cmd += ["--password", password]
    cmd.append(str(path))

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode, (result.stderr or "").strip()
    except subprocess.TimeoutExpired:
        # Menghindari crash aplikasi jika proses memakan waktu lebih dari 60 detik
        return 2, "qpdf: Proses pengecekan timeout (lebih dari 60 detik)."
    except Exception as e:
        return 2, f"qpdf: Terjadi kesalahan tak terduga - {e}"


def _print_qpdf_issues(stderr: str):
    for line in stderr.splitlines():
        line = line.strip()
        if line.startswith("WARNING:") or line.startswith("qpdf:"):
            # buang path file yang diulang-ulang, biar ringkas
            print(f"    - {line}")


# ─── Content-level sanity check (render tiap halaman via poppler) ──────────

def _blank_ratio(image) -> float:
    """Proporsi pixel yang didominasi satu warna (mis. putih polos).
    Rasio tinggi = kemungkinan halaman kosong/konten hilang.
    """
    hist = image.convert("L").histogram()
    total = sum(hist)
    if total == 0:
        return 1.0
    return max(hist) / total

_BLANK_THRESHOLD = 0.9995

def _check_rendered_pages(path: Path) -> list[int]:
    """Render tiap halaman, return list nomor halaman yang ke-render kosong/putih
    (indikasi konten mungkin hilang pas proses repair). Best-effort — kalau poppler
    sendiri gagal render, dianggap skip (bukan dihitung blank)."""
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
        print("\n[ERROR] 'qpdf' belum terinstall di sistem.")
        print("    Ubuntu/Debian : sudo apt install qpdf")
        print("    Windows       : https://qpdf.sourceforge.io/")
        return

    print(f"\n[*] Checking struktur PDF: {path.name}")

    code, stderr = _qpdf_check(path)

    if "invalid password" in stderr.lower():
        print("\n[ERROR] PDF terenkripsi — decrypt dulu sebelum repair.")
        return

    if code == 0:
        print("\n  Struktur PDF valid, nggak ada masalah terdeteksi.")
        print("  File ini nggak butuh repair.")
        return

    label = "Error" if code == 2 else "Warning"
    print(f"\n  [{label}] Masalah struktur ditemukan:")
    _print_qpdf_issues(stderr)

    print()
    confirm = input("[?] Coba perbaiki? [Y/n] : ").strip().lower()
    if confirm not in ("", "y", "yes"):
        print("\n[!] Dibatalkan.")
        return

    import pikepdf

    output = path.parent / f"{path.stem}_repaired.pdf"

    try:
        with pikepdf.open(str(path), attempt_recovery=True) as pdf:
            n_pages = len(pdf.pages)
            pdf.save(str(output))
    except pikepdf.PasswordError:
        print("\n[ERROR] PDF terenkripsi — decrypt dulu sebelum repair.")
        return
    except Exception as e:
        print(f"\n[ERROR] File terlalu rusak buat direpair otomatis: {e}")
        print("    qpdf nggak berhasil merekonstruksi cross-reference table-nya.")
        return

    # Validasi ulang struktur hasil repair
    out_code, out_stderr = _qpdf_check(output)
    struct_ok = (out_code == 0)

    # Validasi konten — render tiap halaman, cek yang jadi blank
    blank_pages = _check_rendered_pages(output)

    print_size_result(path, output)
    print(f"    Halaman : {n_pages}")
    print(f"    Struktur: {'bersih' if struct_ok else 'masih ada isu (lihat qpdf --check manual)'}")

    if blank_pages:
        print(f"\n    [!] {len(blank_pages)}/{n_pages} halaman ke-render KOSONG setelah repair:")
        print(f"        Halaman {', '.join(map(str, blank_pages))}")
        print("        Ini bisa berarti konten di halaman itu emang hilang permanen")
        print("        (data-nya udah nggak ada di file sebelum di-repair), atau")
        print("        memang halaman itu kosong dari awal. Cek manual sebelum dipakai.")
    else:
        print("\n    [✓] Semua halaman ke-render normal (nggak ada indikasi konten hilang).")

    print(f"\n    Saved in : {output.resolve()}")
    print("\n    [!] Catatan: repair ini benerin STRUKTUR file (xref, trailer, dll),")
    print("        bukan menciptakan data yang emang udah bener-bener hilang.")