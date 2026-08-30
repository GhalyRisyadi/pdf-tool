import re

from pathlib import Path
from .privacy import _apply_redactions


_PATTERNS = {
    "email":  re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone":  re.compile(r"(?:\+62|62|0)[\s-]?8[1-9][0-9\-\s]{6,13}[0-9]"),
    "digit16": re.compile(r"\b\d{16}\b"),
    "ip": re.compile(
        r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
    ),
}

_LABELS = {
    "email" : "Email",
    "phone" : "Nomor Telepon",
    "nik" : "NIK (Nomor Induk Kependudukan)",
    "card" : "Kartu Kredit",
    "digit16_ambiguous": "Angka 16-digit (NIK atau Kartu Kredit — nggak bisa dipastikan)",
    "ip":     "IP Address",
}

def _luhn_valid(number: str) -> bool:
    digits = [int(d) for d in number if d.isdigit()]
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0

def _nik_plausible(nik: str) -> bool:
    if not (len(nik) == 16 and nik.isdigit()):
        return False
    dd, mm = int(nik[6:8]), int(nik[8:10])
    if dd > 40:
        dd -= 40
    return 1 <= dd <= 31 and 1 <= mm <= 12

def _classify_digit16(number: str) -> str:
    is_nik = _nik_plausible(number)
    is_card = _luhn_valid(number)
 
    if is_card and not is_nik:
        return "card"
    if is_nik and not is_card:
        return "nik"
    return "digit16_ambiguous"

def _scan_text(text: str) -> dict:
    found = {key: set() for key in _LABELS}
 
    for m in _PATTERNS["email"].finditer(text):
        found["email"].add(m.group())
 
    for m in _PATTERNS["phone"].finditer(text):
        found["phone"].add(m.group())
 
    for m in _PATTERNS["digit16"].finditer(text):
        num = m.group()
        found[_classify_digit16(num)].add(num)
 
    for m in _PATTERNS["ip"].finditer(text):
        found["ip"].add(m.group())
 
    return found

def pii_scan(path: Path):
    import pymupdf
 
    print(f"\n[*] Scanning PII: {path.name}")
 
    doc = pymupdf.open(str(path))
 
    if doc.needs_pass:
        print("\n[ERROR] Encrypted PDF — unlock it first before scanning PII.")
        doc.close()
        return
 
    # findings: kategori -> {string -> [(page_index, rect), ...]}
    findings = {key: {} for key in _LABELS}
 
    for pi, page in enumerate(doc):
        text = page.get_text()
        per_page = _scan_text(text)
 
        for category, values in per_page.items():
            for val in values:
                rects = page.search_for(val)
                if rects:
                    findings[category].setdefault(val, []).extend((pi, r) for r in rects)
 
    total = sum(len(v) for v in findings.values())
 
    if total == 0:
        print("\n  No PII found.")
        print("  (If this is the scan result, the text is not in the text layer — OCR first.)")
        doc.close()
        return
 
    print(f"\n  Found {total} potential PII:\n")
    for category, label in _LABELS.items():
        values = findings[category]
        if not values:
            continue
        pages = sorted({pi + 1 for matches in values.values() for pi, _ in matches})
        print(f"  [{label}] ({len(values)})")
        for val in list(values)[:5]:
            print(f"    - {val}")
        if len(values) > 5:
            print(f"    ... and {len(values) - 5} more ")
        print(f"    pages: {', '.join(map(str, pages))}\n")
 
    print("  [!] Category 'ambiguous' needs manual verification — regex can't be sure")
    print("      whether it's a NIK or credit card number based on the numeric pattern alone.\n")
 
    confirm = input("[?] Redact ALL of the above? [y/N] : ").strip().lower()
    if confirm not in ("y", "yes"):
        print("\n[i] Canceled. The PDF wasn't modified.")
        doc.close()
        return
 
    combined = {}
    for category, values in findings.items():
        for val, matches in values.items():
            combined[val] = matches
 
    output = path.parent / f"{path.stem}_pii_redacted.pdf"
    pages_touched = _apply_redactions(doc, combined, output)
    doc.close()
 
    print(f"\n[✓] {total} PII is permanently redacted on {pages_touched} pages.")
    print(f"    Saved in : {output.resolve()}")