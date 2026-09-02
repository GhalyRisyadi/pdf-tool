from pathlib import Path

from .utils import clear, input_file, input_files, ensure_docx
from .info import pdf_analysis, jpg_analysis, doc_info
from .convert import markdown_to_pdf, pdf_to_jpg, pdf_to_doc, pdf_to_text, pdf_to_markdown, pdf_to_html, jpg_to_pdf, jpg_to_png, png_to_jpg, doc_to_pdf, pdf_to_pdfa
from .compress import pdf_compres, jpg_compres, doc_compres
from .pages_organizer import merge_pdf, split_pdf, merge_docx, split_docx, extract_pages, delete_pages, rotate_pages, reorder_pages
from .privacy import pdf_strip_metadata, jpg_strip_exif, pdf_encrypt, pdf_unlock, pdf_redact
from .sanitize import pdf_sanitize
from .pii_scanner import pii_scan
from .repair import pdf_repair
from .extraction import extract_images_from_pdf, extract_links_from_pdf, extract_tables_from_pdf, run_ocr


def welcome():
    clear()
    print("\n" + "=" * 40)
    print("\t  I Hate PDF file")
    print("=" * 40)
    print("1\t→\tInfo File")
    print("2\t→\tConvert File")
    print("3\t→\tOptimize File")
    print("4\t→\tPages Organizer")
    print("5\t→\tContent Extraction")
    print("6\t→\tPrivacy")
    print("\nQ → Quit")

def flow_info_file():
    while True:
        try:
            clear()
            print("\nSelect a file type")
            print("─" * 36)
            print("1\tPDF")
            print("2\tJPG")
            print("3\tDOC/DOCX")
            print("\n0\tBack")

            choice = input("\nInput [1-3/0] : ").strip()

            if choice == "0":
                return

            ext_map = {"1": [".pdf"], "2": [".jpg", ".jpeg"], "3": [".doc", ".docx"]}
            label_map = {"1": "PDF", "2": "JPG", "3": "DOC/DOCX"}

            if choice not in ext_map:
                print("\n[!] Invalid selection.")
                input("\nEnter to continue")
                continue

            path = input_file(label_map[choice], ext_map[choice])
            clear()

            if   choice == "1": pdf_analysis(path)
            elif choice == "2": jpg_analysis(path)
            elif choice == "3":
                try:
                    with ensure_docx(path) as docx_path:
                        doc_info(docx_path, origin=path)
                except Exception as e:
                    print(f"\n[ERROR] {e}")

            input("\nEnter to continue")
        except (KeyboardInterrupt, EOFError):
            print("\n\n[!] Operation cancelled. Returning to main menu...")
            return

def flow_convert_file():
    while True:
        try:
            clear()
            print("\nConvert to what format?")
            print("─" * 36)
            print("1\tPDF  → JPG")
            print("2\tPDF  → DOCX")
            print("3\tPDF  → Text")
            print("4\tPDF  → Markdown")
            print("5\tPDF  → HTML")
            print("6\tJPG  → PDF")
            print("7\tJPG  → PNG")
            print("8\tPNG  → JPG")
            print("9\tDOCX → PDF")
            print("10\tMarkdown → PDF")
            print("\n0\tBack")

            choice = input("\nInput [1-10/0] : ").strip()

            if choice == "0":
                return

            config = {
                "1": ("PDF",      [".pdf"],          pdf_to_jpg),
                "2": ("PDF",      [".pdf"],          pdf_to_doc),
                "3": ("PDF",      [".pdf"],          pdf_to_text),
                "4": ("PDF",      [".pdf"],          pdf_to_markdown),
                "5": ("PDF",      [".pdf"],          pdf_to_html),
                "6": ("JPG",      [".jpg", ".jpeg"], jpg_to_pdf),
                "7": ("JPG",      [".jpg", ".jpeg"], jpg_to_png),
                "8": ("PNG",      [".png"],          png_to_jpg),
                "9": ("DOC/DOCX", [".doc", ".docx"], doc_to_pdf),
                "10": ("Markdown", [".md"],          markdown_to_pdf),  
            }

            if choice not in config:
                print("\n[!] Invalid selection.")
                input("\nEnter to continue")
                continue

            label, exts, func = config[choice]
            path = input_file(label, exts)
            clear()
            func(path)
            input("\nEnter to continue")
        except (KeyboardInterrupt, EOFError):
            print("\n\n[!] Operation cancelled. Returning to main menu...")
            return

def flow_optimize_file():
    while True:
        try:
            clear()
            print("\nOptimize file")
            print("─" * 36)
            print("1\tCompress PDF")
            print("2\tCompress JPG")
            print("3\tCompress DOC/DOCX")
            print("4\tRepair PDF")
            print("5\tConvert PDF to PDF/A (Archive)")
            print("\n0\tBack")

            choice = input("\nInput [1-5/0] : ").strip()

            if choice == "0":
                return

            config = {
                "1": ("PDF",      [".pdf"],          pdf_compres),
                "2": ("JPG",      [".jpg", ".jpeg"], jpg_compres),
                "3": ("DOC/DOCX", [".doc", ".docx"], doc_compres),
                "4": ("PDF",      [".pdf"],          pdf_repair),
                "5": ("PDF",      [".pdf"],          pdf_to_pdfa),
            }

            if choice not in config:
                print("\n[!] Invalid selection.")
                input("\nEnter to continue")
                continue

            label, exts, func = config[choice]
            path = input_file(label, exts)
            clear()

            if choice == "3":
                try:
                    with ensure_docx(path) as docx_path:
                        func(docx_path, origin=path)
                except Exception as e:
                    print(f"\n[ERROR] {e}")
            else:
                func(path)
            input("\nEnter to continue")
        except (KeyboardInterrupt, EOFError):
            print("\n\n[!] Operation cancelled. Returning to main menu...")
            return

def flow_pages_organizer():
    while True:
        try:
            clear()
            print("\nPages Organizer")
            print("─" * 36)
            print("1\tMerge PDF")
            print("2\tSplit PDF")
            print("3\tMerge DOCX")
            print("4\tSplit DOCX")
            print("5\tExtract Pages")
            print("6\tDelete Pages")
            print("7\tRotate Pages")
            print("8\tReorder Pages")
            print("\n0\tBack")

            choice = input("\nInput [1-8/0] : ").strip()

            if choice == "0":
                return

            config = {
                "1": ("PDF",  [".pdf"],          True,  merge_pdf),
                "2": ("PDF",  [".pdf"],          False, split_pdf),
                "3": ("DOCX", [".docx"],         True,  merge_docx),
                "4": ("DOCX", [".docx"],         False, split_docx),
                "5": ("PDF",  [".pdf"],          False, extract_pages),
                "6": ("PDF",  [".pdf"],          False, delete_pages),
                "7": ("PDF",  [".pdf"],          False, rotate_pages),
                "8": ("PDF",  [".pdf"],          False, reorder_pages),
            }

            if choice not in config:
                print("\n[!] Invalid selection.")
                input("\nEnter to continue")
                continue
            
            label, exts, is_merge, func = config[choice]    

            if is_merge:
                paths = input_files(label, exts)
                clear()
                func(paths)
            else:
                path = input_file(label, exts)
                clear()
                func(path)
                
            input("\nEnter to continue")    
        except (KeyboardInterrupt, EOFError):
            print("\n\n[!] Operation cancelled. Returning to main menu...")
            return

def flow_content_extraction():
    while True:
        try:
            clear()
            print("\nContent Extraction")
            print("─" * 36)
            print("1\tExtract Images from PDF file")
            print("2\tExtract Tables to CSV from PDF file")
            print("3\tExtract Links from PDF file")
            print("4\tOCR")
            print("\n0\tBack")

            choice = input("\nInput [1-4/0] : ").strip()

            if choice == "0":
                return

            config = {
                "1": ("PDF",  [".pdf"],     extract_images_from_pdf),
                "2": ("PDF",  [".pdf"],     extract_tables_from_pdf),
                "3": ("PDF",  [".pdf"],     extract_links_from_pdf),
                "4": ("PDF/Image", [".pdf", ".jpg", ".jpeg", ".png"], run_ocr),
            }

            if choice not in config:
                print("\n[!] Invalid selection.")
                input("\nEnter to continue")
                continue

            label, exts, func = config[choice]
            path = input_file(label, exts)
            clear()
            func(path)
            input("\nEnter to continue")
        except (KeyboardInterrupt, EOFError):
            print("\n\n[!] Operation cancelled. Returning to main menu...")
            return

def flow_privacy():
    while True:
        try:
            clear()
            print("\nPrivacy")
            print("─" * 36)
            print("1\tStrip Metadata  PDF")
            print("2\tStrip EXIF      JPG")
            print("3\tEncrypt PDF    (lock PDF)")
            print("4\tDecrypt PDF    (unlock PDF)")
            print("5\tSanitize PDF   (strip JS/actions/embedded files)")
            print("6\tRedaction PDF")
            print("7\tPII Scanner")
            print("\n0\tBack")

            choice = input("\nInput [1-7/0] : ").strip()

            if choice == "0":
                return

            config = {
                "1": ("PDF", [".pdf"],          pdf_strip_metadata),
                "2": ("JPG", [".jpg", ".jpeg"], jpg_strip_exif),
                "3": ("PDF", [".pdf"],          pdf_encrypt),
                "4": ("PDF", [".pdf"],          pdf_unlock),
                "5": ("PDF", [".pdf"],          pdf_sanitize),
                "6": ("PDF", [".pdf"],          pdf_redact),
                "7": ("PDF", [".pdf"],          pii_scan),
            }

            if choice not in config:
                print("\n[!] Invalid selection.")
                input("\nEnter to continue")
                continue

            label, exts, func = config[choice]
            path = input_file(label, exts)
            clear()
            func(path)
            input("\nEnter to continue")
        except (KeyboardInterrupt, EOFError):
            print("\n\n[!] Operation cancelled. Returning to main menu...")
            return

def main():
    try:
        while True:
            welcome()
            try:
                opsi = input("\nInput [1-6/Q] : ").strip().upper()
            except (KeyboardInterrupt, EOFError):
                print("\n\n[!] Exiting pdftool. Goodbye!\n")
                break

            if   opsi == "Q": print("\nQuit"); break
            elif opsi == "1": flow_info_file()
            elif opsi == "2": flow_convert_file()
            elif opsi == "3": flow_optimize_file()
            elif opsi == "4": flow_pages_organizer()
            elif opsi == "5": flow_content_extraction()
            elif opsi == "6": flow_privacy()
            else:
                print("\n[!] Invalid selection.")
                try:
                    input("\nEnter to continue")
                except (KeyboardInterrupt, EOFError):
                    print("\n\n[!] Exiting pdftool. Goodbye!\n")
                    break
    except (KeyboardInterrupt, EOFError):
        print("\n\n[!] Exiting pdftool. Goodbye!\n")
