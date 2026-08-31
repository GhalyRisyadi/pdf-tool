import getpass
from pathlib import Path
from .utils import print_size_result


# ─── PDF Metadata ────────────────────────────────────────────────────────────
_PDF_DOCINFO_FIELDS = {
    "/Title":        "Title",
    "/Author":       "Author",
    "/Subject":      "Subject",
    "/Keywords":     "Keywords",
    "/Creator":      "Creator",
    "/Producer":     "Producer",
    "/CreationDate": "Created",
    "/ModDate":      "Modified",
}


def _print_pdf_meta(pdf) -> bool:
    found = False
    for key, label in _PDF_DOCINFO_FIELDS.items():
        val = pdf.docinfo.get(key)
        if val:
            print(f"  {label:<12}: {str(val)[:80]}")
            found = True
    return found


def pdf_strip_metadata(path: Path):
    import pikepdf

    print(f"\n[*] Scanning metadata: {path.name}\n")

    try:
        with pikepdf.open(str(path)) as pdf:
            has_meta = _print_pdf_meta(pdf)

            if not has_meta:
                print("  No metadata was found.")
                return

            print()
            confirm = input("[?] Strip all of the metadata above? [Y/n] : ").strip().lower()
            if confirm not in ("", "y", "yes"):
                print("\n[!] Canceled.")
                return

            for key in list(pdf.docinfo.keys()):
                del pdf.docinfo[key]

            with pdf.open_metadata() as xmp:
                for key in list(xmp.keys()):
                    del xmp[key]

            output = path.parent / f"{path.stem}_clean.pdf"
            pdf.save(str(output))

        print_size_result(path, output)
        print(f"    Saved in : {output.resolve()}")

    except Exception as e:
        print(f"\n[ERROR] Metadata strip failed: {e}")


# ─── JPG EXIF ────────────────────────────────────────────────────────────────
_SENSITIVE_EXIF_TAGS = {
    271:   "Make",               # Camera/Phone Brand
    272:   "Model",              # Camera/Phone Model
    306:   "DateTime",
    36867: "DateTimeOriginal",
    36868: "DateTimeDigitized",
    315:   "Artist",
    33432: "Copyright",
    34853: "GPSInfo",            # GPS Coordinates — highly sensitive
    40091: "XPAuthor",
    40094: "XPKeywords",
    40092: "XPComment",
}


def jpg_strip_exif(path: Path):
    from PIL import Image, ExifTags

    print(f"\n[*] Scanning EXIF: {path.name}\n")

    try:
        img  = Image.open(path)
        exif = img.getexif()

        if not exif:
            print("  No EXIF data was found.")
            img.close()
            return

        printed = False
        for tag_id, val in exif.items():
            if tag_id in _SENSITIVE_EXIF_TAGS:
                label = _SENSITIVE_EXIF_TAGS[tag_id]
                print(f"  {label:<24}: {str(val)[:70]}")
                printed = True

        if not printed:
            print(f"  {len(exif)} tag found (non-sensitive metadata)")

        print()
        confirm = input("[?] Remove all EXIF data? [Y/n] : ").strip().lower()
        if confirm not in ("", "y", "yes"):
            print("\n[!] Canceled.")
            img.close()
            return

        output = path.parent / f"{path.stem}_clean.jpg"

        clean = img.convert("RGB")
        clean.save(str(output), "JPEG", quality=95, optimize=True)
        img.close()

        check      = Image.open(output)
        exif_after = check.getexif()
        check.close()

        print_size_result(path, output)
        if exif_after:
            print(f"    [!] Warning: there are still some {len(exif_after)} remaining tags (non-critical).")
        else:
            print("    [✓] Verification: Clean EXIF data.")
        print(f"    Saved in : {output.resolve()}")

    except Exception as e:
        print(f"\n[ERROR] EXIF extraction failed: {e}")


# ─── PDF Encrypt ─────────────────────────────────────────────────────────────
def pdf_encrypt(path: Path):
    import pikepdf
 
    is_encrypted = False
    requires_password = False
    is_restriction = False
 
    try:
        from pypdf import PdfReader
        try:
            reader = PdfReader(str(path))
            is_encrypted = getattr(reader, "is_encrypted", False)
            if is_encrypted:
                try:
                    dec = reader.decrypt("")
                    if dec == 0:
                        requires_password = True
                    else:
                        is_encrypted = True
                        is_restriction = True
                except Exception:
                    requires_password = True
        except Exception:
            try:
                with pikepdf.open(str(path)):
                    is_encrypted = False
            except pikepdf.PasswordError:
                is_encrypted = True
                requires_password = True
            except Exception:
                is_encrypted = False
    except Exception:
        try:
            with pikepdf.open(str(path)):
                is_encrypted = False
        except pikepdf.PasswordError:
            is_encrypted = True
            requires_password = True
        except Exception:
            is_encrypted = False
 
    # Fallback: if pypdf raises exception but pikepdf can open → restriction-only
    if is_encrypted and not requires_password and not is_restriction:
        try:
            with pikepdf.open(str(path)) as _pdf:
                if _pdf.encryption:
                    is_restriction = True
        except Exception:
            pass
 
    print(f"\n[*] Lock PDF")
    print("    Algorithm : AES-256  (PDF Revision 6)")
    print("─" * 45)
    print(f"File : {path.name}\n")
 
    print("Security status:")
    if requires_password:
        print("  [i] This file is already password protected")
        print("    No need to encrypt")
        return
    elif is_restriction:
        print("  [i] This file is already restricted")
        print("    No need to restrict")
        return
    else:
        print("  [i] Unsecured (Ready to lock)")
 
    print("\nSelect file security")
    print("1    Password (Open requires password)")
    print("2    Restriction (Prevent copy, print, modify)")
    print("3    Password + Restriction")
    print("0    Back")
 
    choice = input("\nInput [1-3/0] : ").strip()
 
    if choice == "0":
        return
 
    if choice not in ["1", "2", "3"]:
        print("\n[!] Invalid selection.")
        return
 
    output = path.parent / f"{path.stem}_encrypted.pdf"
 
    perms = pikepdf.Permissions(
        extract=False,
        modify_annotation=False,
        modify_assembly=False,
        modify_form=False,
        modify_other=False,
        print_lowres=False,
        print_highres=False,
    )
 
    if choice == "1":
        try:
            password = getpass.getpass("Password    : ")
            if not password:
                print("\n[!] The password cannot be blank.")
                return
 
            confirm = getpass.getpass("Confirmation  : ")
            if password != confirm:
                print("\n[!]    The password does not match.")
                return
 
            print("\n[*] Encrypting PDF...")
            with pikepdf.open(str(path)) as pdf:
                pdf.save(
                    str(output),
                    encryption=pikepdf.Encryption(
                        owner=password,
                        user=password,
                        R=6,  # AES-256
                    )
                )
        except Exception as e:
            print(f"\n[ERROR] Failed to encryption: {e}")
            return
 
    elif choice == "2":
        try:
            print("\n[i] The file will open normally, but Copy, Print, and Modify will be disabled.")
            owner_pass = getpass.getpass("Owner Password (to lock) : ")
            if not owner_pass:
                print("\n[!] The owner password cannot be blank.")
                return
 
            confirm = getpass.getpass("Confirmation             : ")
            if owner_pass != confirm:
                print("\n[!] The password does not match.")
                return
 
            print("\n[*] Applying Restrictions...")
            with pikepdf.open(str(path)) as pdf:
                pdf.save(
                    str(output),
                    encryption=pikepdf.Encryption(
                        owner=owner_pass,
                        user="",  
                        allow=perms,
                        R=6
                    )
                )
        except Exception as e:
            print(f"\n[ERROR] Failed to apply restrictions: {e}")
            return
        
    elif choice == "3":
        try:
            user_pass = getpass.getpass("User Password (to open)  : ")
            if not user_pass:
                print("\n[!] User password cannot be blank.")
                return
 
            owner_pass = getpass.getpass("Owner Password (to lock) : ")
            if not owner_pass:
                print("\n[!] Owner password cannot be blank.")
                return
 
            if user_pass == owner_pass:
                print("\n[!] User and Owner passwords MUST be different to enforce restrictions.")
                return
 
            print("\n[*] Applying Password and Restrictions...")
            with pikepdf.open(str(path)) as pdf:
                pdf.save(
                    str(output),
                    encryption=pikepdf.Encryption(
                        owner=owner_pass,
                        user=user_pass,
                        allow=perms,
                        R=6
                    )
                )
        except Exception as e:
            print(f"\n[ERROR] Failed to encrypt: {e}")
            return
 
    size_kb = output.stat().st_size / 1024
    print(f"\n[✓] PDF Secured: {output.name}  ({size_kb:.0f} KB)")
    print(f"    Saved in   : {output.resolve()}")
    print("\n    [!] Keep your password safe. There is no way to recover it.")

# ─── PDF Unlock ─────────────────────────────────────────────────────────────
def pdf_unlock(path:Path):
    import pikepdf
    from pypdf import PdfReader

    try:
        reader = PdfReader(str(path))
        is_encrypted = reader.is_encrypted
        requires_password = False
        
        if is_encrypted:
            if reader.decrypt("") == 0:
                requires_password = True
    except Exception:
        requires_password = True
        is_encrypted = True

    print("\nUnlock PDF")
    print("─" * 36)
    print(f"File : {path.name}\n")

    print("Security status:")
    if requires_password:
        print("  Password             : YES")
        print("  Copy / Select        : DENIED")
        print("  Print                : DENIED")
        print("  Modify               : DENIED")
    elif is_encrypted:
        print("  Password             : NO (Owner Restricted)")
        print("  Copy / Select        : DENIED")
        print("  Print                : DENIED")
        print("  Modify               : DENIED")
    else:
        print("  Password             : NO")
        print("  Copy / Select        : ALLOWED")
        print("  Print                : ALLOWED")
        print("  Modify               : ALLOWED")
        
    if not is_encrypted:
        print("\n[i] This file is not encrypted / has no restrictions.")
        print("    There's nothing to unlock.")
        return

    print("\nWhat would you like to remove?")
    print("1   Password")
    print("2   Restrictions")
    print("3   Password + Restrictions")
    print("0   Back")

    choice = input("\nInput [1-3/0] : ").strip()

    if choice == "0":
        return
        
    if choice not in ["1", "2", "3"]:
        print("\n[!] Invalid selection")
        return

    output = path.parent / f"{path.stem}_unlocked.pdf"

    # ---------------------------------------------------------
    # MODE 1 : Remove Password
    # ---------------------------------------------------------
    if choice == "1":
        print("\nUnlock PDF — Remove Password")
        print("─" * 36)
        print(f"File : {path.name}\n")
        
        if not requires_password:
            print("[i] This file does not require a password to open.")
            print("    Please select the “Remove Restrictions” menu (Mode 2).")
            return
            
        print("This PDF is password protected.")
        print("Enter password to unlock:\n")
        password = getpass.getpass("Password : ")
        
        print("\n[*] Unlocking PDF...")
        try:
            with pikepdf.open(str(path), password=password) as pdf:
                print("[✓] Password verified.\n")
                pdf.save(str(output))
                
            print("[✓] PDF unlocked successfully\n")
            print(f"Output : {output.name}")
            size_mb = output.stat().st_size / (1024 * 1024)
            print(f"Size   : {size_mb:.2f} MB\n")
            print("The password is no longer required to open this file.")
            
        except pikepdf.PasswordError:
            print("\n[!] Incorrect password.")
            print("    PDF was not modified.")
        except Exception as e:
            print(f"\n[ERROR] Failed to unlock: {e}")

    # ---------------------------------------------------------
    # MODE 2 : Remove Restrictions
    # ---------------------------------------------------------
    elif choice == "2":
        print("\nUnlock PDF — Remove Restrictions")
        print("─" * 36)
        print(f"File : {path.name}\n")
        
        if requires_password:
            print("[!] This file is locked by a user password.")
            print("    Use Mode 1 or Mode 3 and enter the password first.")
            return
            
        print("Current restrictions:")
        print("  Copy / Select text   : DENIED")
        print("  Print                : DENIED")
        print("  Modify               : DENIED")
        print("  Annotations          : DENIED\n")
        
        print("[*] Removing PDF restrictions...")
        try:
            with pikepdf.open(str(path)) as pdf:
                pdf.save(str(output))
                
            print("[✓] Restrictions removed.\n")
            print(f"Output : {output.name}\n")
            print("Permissions:")
            print("  Copy / Select text   : ALLOWED")
            print("  Print                : ALLOWED")
            print("  Modify               : ALLOWED")
            print("  Annotations          : ALLOWED")
            
        except Exception as e:
            print(f"\n[ERROR] Failed to remove restrictions: {e}")
    
    # ---------------------------------------------------------
    # MODE 3 : Remove Password + Restrictions
    # ---------------------------------------------------------
    elif choice == "3":
        print("\nUnlock PDF — Remove Password + Restrictions")
        print("─" * 36)
        print(f"File : {path.name}\n")
        
        password = ""
        if requires_password:
            print("This PDF is password protected.")
            print("Enter password to unlock:\n")
            password = getpass.getpass("Password : ")
            
        print("\n[*] Unlocking PDF...")
        try:
            if requires_password:
                with pikepdf.open(str(path), password=password) as pdf:
                    print("    ✓ Password verified and removed")
                    pdf.save(str(output))
            else:
                with pikepdf.open(str(path)) as pdf:
                    pdf.save(str(output))
                    
            print("    ✓ Restrictions removed\n")
            print("[✓] PDF unlocked successfully\n")
            print(f"Output : {output.name}")
            size_mb = output.stat().st_size / (1024 * 1024)
            print(f"Size   : {size_mb:.2f} MB")
            
        except pikepdf.PasswordError:
            print("\n[!] Incorrect password.")
            print("    PDF was not modified.")
        except Exception as e:
            print(f"\n[ERROR] Failed to unlock: {e}")
    

# ─── PDF Redact ──────────────────────────────────────────────────────────────
def _apply_redactions(doc, findings: dict, output: Path) -> int:
    pages_touched = set()
    for matches in findings.values():
        for pi, rect in matches:
            doc[pi].add_redact_annot(rect, fill=(0, 0, 0))
            pages_touched.add(pi)
 
    for pi in pages_touched:
        doc[pi].apply_redactions()
 
    doc.save(str(output), garbage=3, deflate=True)
    return len(pages_touched)

def pdf_redact(path: Path):
    import pymupdf

    # --- UI: Header ---
    print("\nRedact PDF")
    print("─" * 36)
    print(f"\nFile : {path.name}\n")

    doc = pymupdf.open(str(path))

    # Check encryption
    if doc.needs_pass:
        print("[!] Encrypted PDF — unlock it first before redacting it.")
        doc.close()
        return

    # --- UI: Input ---
    print("Enter text to redact (Separate with commas if there is more than one):")
    raw = input("> ").strip()
    
    if not raw:
        print("\n[!] Text cannot be empty.")
        doc.close()
        return

    print("\n[*] Searching document...")

    terms = [t.strip() for t in raw.split(",") if t.strip()]
    findings = {}
    
    # Search terms on each page
    for term in terms:
        matches = [(pi, rect) for pi, page in enumerate(doc) for rect in page.search_for(term)]
        findings[term] = matches

    total_matches = sum(len(m) for m in findings.values())

    # --- UI: Not Found ---
    if total_matches == 0:
        print("\n[!] No matching text found.")
        print("    PDF was not modified.")
        print("    (If the PDF is a scanned document, the text cannot be read without OCR)")
        doc.close()
        return

    # --- UI: Found ---
    print(f"[✓] Found {total_matches} matches\n")

    page_match_counts = {}
    for matches in findings.values():
        for pi, _ in matches:
            page_match_counts[pi] = page_match_counts.get(pi, 0) + 1

    for pi in sorted(page_match_counts.keys()):
        count = page_match_counts[pi]
        word = "match" if count == 1 else "matches"
        print(f"  Page {pi + 1:<3} • {count} {word}")

    print("\n[!] WARNING")
    print("    The matched text will be permanently removed.")
    print("    This operation cannot be undone.\n")

    # Execution confirmation
    confirm = input("Apply redaction? [y/N]: ").strip().lower()
    if confirm not in ("y", "yes"):
        print("\n[i] Operation cancelled. PDF was not modified.")
        doc.close()
        return

    print("\n[*] Applying redactions...")

    output = path.parent / f"{path.stem}_redacted.pdf"
    _apply_redactions(doc, findings, output)
    doc.close()

    # --- UI: Success ---
    print(f"[✓] {total_matches} occurrences permanently redacted.\n")
    print(f"Output : {output.name}")
    size_kb = output.stat().st_size / 1024
    print(f"Size   : {size_kb:.1f} KB")