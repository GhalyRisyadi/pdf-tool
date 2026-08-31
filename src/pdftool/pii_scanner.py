import re
import sys
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
    "phone" : "Phone Number",
    "nik":    "National ID (NIK, most likely)",
    "card":   "Credit Card (most likely)",
    "digit16_ambiguous": "16-digit number (National ID or credit card — unclear)",
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

    total_pages = len(doc)
    findings = {key: {} for key in _LABELS}
    bar_length = 20
 
    for pi, page in enumerate(doc):
        progress = (pi + 1) / total_pages
        block = int(round(bar_length * progress))
        bar = f"\r[{'#' * block + '-' * (bar_length - block)}] {int(progress * 100)}%"
        sys.stdout.write(bar)
        sys.stdout.flush()

        text = page.get_text()
        per_page = _scan_text(text)
 
        for category, values in per_page.items():
            for val in values:
                rects = page.search_for(val)
                if rects:
                    findings[category].setdefault(val, []).extend((pi, r) for r in rects)
 
    print()


    total = sum(len(v) for v in findings.values())
    categories_found = sum(1 for v in findings.values() if v)
 
    if total == 0:
        print("\n  No PII found.")
        print("  (If this is the scan result, the text is not in the text layer — OCR first.)")
        doc.close()
        return

    print("\n[✓] Scan completed")
    print(f"    Pages scanned : {total_pages}")
    print(f"    Findings      : {total}")
    print(f"    Categories    : {categories_found}")

    print("\n" + "─" * 40)

    for category, label in _LABELS.items():
        values = findings[category]
        if not values:
            continue
        n = len(values)
        word = "finding" if n == 1 else "findings"
        print(f"\n{label:<20}{n} {word}")
        for val in list(values):
            pages = sorted({pi + 1 for pi, _ in values[val]})
            page_word = "page" if len(pages) == 1 else "pages"
            page_list = ", ".join(map(str, pages))
            print(f"  • {val:<30} {page_word} {page_list}")
 
    print("\n" + "─" * 40)

    if findings["nik"] or findings["card"]:
        print("  [!] Category 'ambiguous' needs manual verification — regex can't be sure")
        print("      whether it's a NIK or credit card number based on the numeric pattern alone.\n")

    ambiguous_count = len(findings.get("digit16_ambiguous", {}))
    if ambiguous_count:
        word = "finding requires" if ambiguous_count == 1 else "findings require"
        print(f"\n[!] {ambiguous_count} ambiguous {word} manual review.")
        print("    Regex can't determine whether it's a National ID number or a credit card number based solely on the number pattern.")

    pages_affected = len({pi for values in findings.values() for matches in values.values() for pi, _ in matches})

    print("\nRedaction")
    print(f"  Findings to redact : {total}")
    print(f"  Pages affected     : {pages_affected}")
    print("\n[!] Redaction permanently removes the detected data.")
    print("    This operation cannot be undone.\n")
 
    confirm = input("[?] Redact ALL of the above? [y/N] : ").strip().lower()
    if confirm not in ("y", "yes"):
        print("\n[i] Canceled. The PDF wasn't modified.")
        doc.close()
        return

    print("\n[*] Applying redactions...")
 
    combined = {}
    for category, values in findings.items():
        for val, matches in values.items():
            combined[val] = matches
 
    output = path.parent / f"{path.stem}_pii_redacted.pdf"
    pages_touched = _apply_redactions(doc, combined, output)
    doc.close()
 
    print("\n[✓] Redaction completed")
    print(f"    Findings redacted : {total}")
    print(f"    Pages affected    : {pages_touched}")
    print("\nOutput:")
    print(f"    {output.resolve()}")