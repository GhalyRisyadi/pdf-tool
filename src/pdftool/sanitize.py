from pathlib import Path
from .utils import print_size_result


_ACTION_LABELS = {
    "/JavaScript": "JavaScript",
    "/Launch":     "Launch (run external program)",
    "/SubmitForm": "Submit Form (send data to external URL)",
    "/ImportData": "Import Data",
    "/GoToR":      "GoTo Remote (open external file)",
    "/GoToE":      "GoTo Embedded (open embedded file)",
    "/URI":        "URI (open external link)",
    "/Sound":      "Sound",
    "/Movie":      "Movie",
    "/RichMedia":  "Rich Media",
}

_AA_TRIGGER_LABELS = {
    "/O":  "Open",
    "/C":  "Close / Calculate",
    "/WC": "Will Close",
    "/WS": "Will Save",
    "/DS": "Did Save",
    "/WP": "Will Print",
    "/DP": "Did Print",
    "/E":  "Enter",
    "/X":  "Exit",
    "/D":  "Mouse Down",
    "/U":  "Mouse Up",
    "/Fo": "Focus",
    "/Bl": "Blur",
    "/PO": "Page Open",
    "/PC": "Page Close",
    "/PV": "Page Visible",
    "/PI": "Page Invisible",
    "/K":  "Keystroke",
    "/F":  "Format",
    "/V":  "Validate",
}

_CATEGORY_LABELS = {
    "open_action":    "OpenAction (runs automatically on open)",
    "doc_aa":         "Document Additional Actions",
    "javascript":     "Embedded JavaScript",
    "embedded_files": "Embedded Files",
    "page_actions":   "Page Additional Actions",
    "annot_actions":  "Annotation / Form Field Actions",
    "xfa":            "XFA Dynamic Form",
}


# ─── Scan helpers ──────────────────────────────────────────────────────────

def _action_label(action) -> str | None:
    try:
        s = str(action["/S"])
    except (KeyError, TypeError):
        return None
    return _ACTION_LABELS.get(s, s.lstrip("/") or "Unknown")


def _walk_name_tree(node):
    """Yield (name, value) pairs from a PDF name tree, including branches via /Kids."""
    if node is None:
        return
    if "/Names" in node:
        names = node["/Names"]
        for i in range(0, len(names), 2):
            yield str(names[i]), names[i + 1]
    if "/Kids" in node:
        for kid in node["/Kids"]:
            yield from _walk_name_tree(kid)


def _scan(pdf) -> dict:
    findings = {key: [] for key in _CATEGORY_LABELS}
    root = pdf.Root

    if "/OpenAction" in root:
        label = _action_label(root["/OpenAction"])
        findings["open_action"].append(label or "Destination (non-action, aman)")

    if "/AA" in root:
        for key in root["/AA"].keys():
            findings["doc_aa"].append(_AA_TRIGGER_LABELS.get(str(key), str(key)))

    if "/Names" in root:
        names = root["/Names"]
        if "/JavaScript" in names:
            for name, _ in _walk_name_tree(names["/JavaScript"]):
                findings["javascript"].append(name)
        if "/EmbeddedFiles" in names:
            for name, _ in _walk_name_tree(names["/EmbeddedFiles"]):
                findings["embedded_files"].append(name)

    if "/AcroForm" in root and "/XFA" in root["/AcroForm"]:
        findings["xfa"].append("XFA form detected (dynamic form logic)")

    for pi, page in enumerate(pdf.pages, 1):
        if "/AA" in page:
            for key in page["/AA"].keys():
                findings["page_actions"].append(
                    f"Page {pi}: {_AA_TRIGGER_LABELS.get(str(key), str(key))}"
                )

        if "/Annots" not in page:
            continue

        for annot in page["/Annots"]:
            subtype = str(annot.get("/Subtype", ""))

            if "/A" in annot:
                findings["annot_actions"].append(
                    f"Page {pi} [{subtype.lstrip('/')}]: {_action_label(annot['/A'])}"
                )
            if "/AA" in annot:
                for key in annot["/AA"].keys():
                    trig = _AA_TRIGGER_LABELS.get(str(key), str(key))
                    findings["annot_actions"].append(
                        f"Page {pi} [{subtype.lstrip('/')}]: {trig} (trigger)"
                    )
            if subtype == "/FileAttachment" and "/FS" in annot:
                fname = str(annot["/FS"].get("/F", "unnamed"))
                findings["embedded_files"].append(f"{fname} (file attachment annotation)")

    return findings


def _print_findings(findings: dict) -> bool:
    found_any = False
    for key, label in _CATEGORY_LABELS.items():
        items = findings[key]
        if not items:
            continue
        found_any = True
        print(f"\n  [{label}] ({len(items)})")
        for item in items[:10]:
            print(f"    - {item}")
        if len(items) > 10:
            print(f"    ... and {len(items) - 10} more")
    return found_any


# ─── Sanitize ─────────────────────────────────────────────────────────────

def pdf_sanitize(path: Path):
    import pikepdf

    print(f"\n[*] Scanning attack surface: {path.name}")

    try:
        with pikepdf.open(str(path)) as pdf:
            findings = _scan(pdf)

            if not _print_findings(findings):
                print("\n  No active content found. This PDF is clean.")
                return

            print()
            confirm = input("[?] Strip all elements listed above? [Y/n] : ").strip().lower()
            if confirm not in ("", "y", "yes"):
                print("\n[!] Canceled.")
                return

            root = pdf.Root

            if "/OpenAction" in root:
                del root["/OpenAction"]

            if "/AA" in root:
                del root["/AA"]

            if "/Names" in root:
                names = root["/Names"]
                if "/JavaScript" in names:
                    del names["/JavaScript"]
                if "/EmbeddedFiles" in names:
                    del names["/EmbeddedFiles"]

            if "/AcroForm" in root and "/XFA" in root["/AcroForm"]:
                del root["/AcroForm"]["/XFA"]

            for page in pdf.pages:
                if "/AA" in page:
                    del page["/AA"]

                if "/Annots" not in page:
                    continue

                kept = []
                for annot in page["/Annots"]:
                    subtype = str(annot.get("/Subtype", ""))

                    if subtype == "/FileAttachment" and "/FS" in annot:
                        continue

                    if "/A" in annot:
                        del annot["/A"]
                    if "/AA" in annot:
                        del annot["/AA"]

                    kept.append(annot)

                page["/Annots"] = kept

            output = path.parent / f"{path.stem}_sanitized.pdf"
            pdf.save(str(output))

        print_size_result(path, output)
        print(f"    Saved in : {output.resolve()}")

    except Exception as e:
        if "password" in str(e).lower() or type(e).__name__ == "PasswordError":
            print("\n[ERROR] PDF is encrypted — please unlock it before sanitizing.")
        else:
            print(f"\n[ERROR] Failed to sanitize: {e}")
