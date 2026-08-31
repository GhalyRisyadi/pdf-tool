import io
import zipfile
from pathlib import Path

from .utils import clear


_PDF_PRESET = {
    "low":    {"dpi": 72,  "jpg_quality": 40},
    "medium": {"dpi": 120, "jpg_quality": 65},
}

_IMG_QUALITY = {
    "low":    35,
    "medium": 60,
    "high":   80,
}


def ask_compress_level() -> str | None:
    while True:
        clear()
        print("\nCompression level\n")
        print("1\tLow    → smallest file size, noticeable quality drop")
        print("2\tMedium → balanced [recommended]")
        print("3\tHigh   → best quality, smaller file size reduction")
        print("\n0\tBack")

        choice = input("\nInput [1-3/0] : ").strip()

        if choice == "0":
            return None

        mapping = {"1": "low", "2": "medium", "3": "high"}
        if choice not in mapping:
            print("\n[!] Invalid selection.")
            input("\nEnter to continue")
            continue

        return mapping[choice]


def pdf_compres(path: Path):
    level = ask_compress_level()
    if level is None:
        return

    output      = path.parent / f"{path.stem}_compressed.pdf"
    original_kb = path.stat().st_size / 1024

    print(f"\n[*] Compressing {path.name} — level: {level}")

    try:
        if level == "high":
            import pikepdf
            with pikepdf.open(str(path)) as pdf:
                pdf.save(
                    str(output),
                    compress_streams=True,
                    stream_decode_level=pikepdf.StreamDecodeLevel.generalized,
                    recompress_flate=True,
                )
        else:
            from pdf2image import convert_from_path
            preset = _PDF_PRESET[level]
            images = convert_from_path(str(path), dpi=preset["dpi"])
            rgb    = [img.convert("RGB") for img in images]

            save_kwargs = dict(
                format="PDF",
                resolution=preset["dpi"],
                quality=preset["jpg_quality"],
                optimize=True,
            )
            if len(rgb) == 1:
                rgb[0].save(str(output), **save_kwargs)
            else:
                rgb[0].save(str(output), save_all=True,
                            append_images=rgb[1:], **save_kwargs)

        _print_result(output, original_kb)
        if level != "high":
            print("    [!] Text in this PDF can no longer be selected (rasterized).")

    except Exception as e:
        print(f"\n[ERROR] Failed to compress: {e}")


def jpg_compres(path: Path):
    level = ask_compress_level()
    if level is None:
        return

    from PIL import Image

    output      = path.parent / f"{path.stem}_compressed.jpg"
    original_kb = path.stat().st_size / 1024
    quality     = _IMG_QUALITY[level]

    print(f"\n[*] Compressing {path.name} — level: {level}")

    try:
        img = Image.open(path).convert("RGB")
        img.save(str(output), "JPEG", quality=quality, optimize=True)
        img.close()
        _print_result(output, original_kb)

    except Exception as e:
        print(f"\n[ERROR] Failed to compress: {e}")


def doc_compres(path: Path, origin: Path | None = None): 
    level = ask_compress_level()
    if level is None:
        return

    origin      = origin or path
    output      = path.parent / f"{path.stem}_compressed.docx"
    original_kb = path.stat().st_size / 1024
    quality     = _IMG_QUALITY[level]

    print(f"\n[*] Compressing {origin.name} — level: {level}")

    try:
        from PIL import Image

        with zipfile.ZipFile(str(path), "r") as zin:
            with zipfile.ZipFile(str(output), "w", zipfile.ZIP_DEFLATED) as zout:
                for item in zin.namelist():
                    data     = zin.read(item)
                    is_image = (
                        item.startswith("word/media/")
                        and item.lower().endswith((".jpg", ".jpeg"))
                    )
                    if is_image:
                        try:
                            img = Image.open(io.BytesIO(data)).convert("RGB")
                            buf = io.BytesIO()
                            img.save(buf, "JPEG", quality=quality, optimize=True)
                            data = buf.getvalue()
                        except Exception:
                            pass  
                    zout.writestr(item, data)

        _print_result(output, original_kb)

    except Exception as e:
        print(f"\n[ERROR] Failed to compress: {e}")


def _print_result(output: Path, original_kb: float):
    new_kb    = output.stat().st_size / 1024
    reduction = (original_kb - new_kb) / original_kb * 100 if original_kb else 0
    print(f"\n[✓] Compressed: {output.name}")
    print(f"    Before : {original_kb:.0f} KB")
    print(f"    After  : {new_kb:.0f} KB")
    print(f"    Saved  : {reduction:.0f}%")