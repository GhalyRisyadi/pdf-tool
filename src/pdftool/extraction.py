import csv
import sys
from pathlib import Path


def extract_images_from_pdf(path: Path, output_dir: Path = None):
    import fitz

    if output_dir is None:
        output_dir = path.parent / f"{path.stem}_extracted_images"

    print(f"\n[*] Extracting original images (lossless) from: {path.name}")

    try:
        doc = fitz.open(str(path))
        
        if len(doc) == 0:
            print("\n[!] PDF document is empty or unreadable.")
            return

        extracted_xrefs = set()
        saved_count = 0
        output_dir_created = False

        for page_index in range(len(doc)):
            page = doc[page_index]

            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                if xref in extracted_xrefs:
                    continue 
                
                extracted_xrefs.add(xref)
                
                if not output_dir_created:
                    output_dir.mkdir(parents=True, exist_ok=True)
                    output_dir_created = True

                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"] 
                
                image_filename = f"page{page_index + 1:03d}_img{img_index + 1:02d}.{image_ext}"
                image_filepath = output_dir / image_filename
                
                with open(image_filepath, "wb") as f:
                    f.write(image_bytes)
                
                saved_count += 1
                size_kb = len(image_bytes) / 1024
                print(f"  [+] Saved: {image_filename}  ({size_kb:.1f} KB)")

        if saved_count == 0:
            print("\n[!] No bitmap/raster images found in this PDF.")
            print("    (If there appear to be images but none were extracted, they may be vector/shape graphics.)")
        else:
            print(f"\n[✓] Successfully extracted {saved_count} images.")
            print(f"    Output folder : {output_dir.resolve()}")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to extract images: {e}")

def extract_links_from_pdf(path: Path):
    import fitz
    
    print("\nExtract Links")
    print("─" * 60)

    try:
        doc = fitz.open(str(path))
        extracted_links = []

        for page_index in range(len(doc)):
            page = doc[page_index]
            links = page.get_links()
            
            for link in links:
                if link.get("kind") == fitz.LINK_URI:
                    uri = link.get("uri")
                    if uri:
                        extracted_links.append((page_index + 1, uri))

        if not extracted_links:
            print("\n[!] No external URLs or links found in this PDF.")
            return

        print(f"\nFound {len(extracted_links)} URLs\n")
        print(f"{'Page':<5} URL")
        print("─" * 60)
        
        for page_num, url in extracted_links:
            print(f"{page_num:<5} {url}")
            
        print("─" * 60)

        save_choice = input("Save result [Y/N] ? ").strip().lower()
        
        if save_choice in ['y', 'yes']:
            out_file = path.parent / f"{path.stem}_links.txt"
            
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(f"Source Document : {path.name}\n")
                f.write(f"Total URLs Found: {len(extracted_links)}\n")
                f.write("=" * 50 + "\n\n")
                for page_num, url in extracted_links:
                    f.write(f"Page {page_num:<4} : {url}\n")
            
            print(f"\n[✓] Saved as TXT: {out_file.name}")
            print(f"    Location: {out_file.resolve()}")
        else:
            print("\n[i] Result not saved.")

    except Exception as e:
        print(f"\n[ERROR] Failed to extract links: {e}")

def extract_tables_from_pdf(path: Path):
    import pdfplumber

    print("\nExtract Tables")
    print("─" * 36)

    try:
        with pdfplumber.open(str(path)) as pdf:
            total_pages = len(pdf.pages)
            
            print(f"\nFile   : {path.name}")
            print(f"Pages  : {total_pages}\n")
            print("Scanning pages...")

            extracted_tables_info = []
            table_count = 0

            for i, page in enumerate(pdf.pages):
                progress = (i + 1) / total_pages
                bar_length = 20
                block = int(round(bar_length * progress))
                text = f"\r[{'#' * block + '-' * (bar_length - block)}] {int(progress * 100)}%"
                sys.stdout.write(text)
                sys.stdout.flush()

                tables = page.extract_tables()
                
                for table in tables:
                    table_count += 1
                    rows = len(table)
                    cols = max(len(row) for row in table) if rows > 0 else 0
                    extracted_tables_info.append({
                        'table_num': table_count,
                        'page_num': i + 1,
                        'rows': rows,
                        'cols': cols,
                        'data': table
                    })

            print()

            if table_count == 0:
                print("\n[!] No tables found in this PDF.")
                return

            print(f"\nTables found: {table_count}\n")
            print(f"  {'#':<3} {'Page':<7} {'Rows':<7} {'Columns':<7}")
            
            for info in extracted_tables_info:
                print(f"  {info['table_num']:<3} {info['page_num']:<7} {info['rows']:<7} {info['cols']:<7}")

            print("\nSaving tables...")

            output_dir = path.parent / f"{path.stem}_tables"
            output_dir.mkdir(parents=True, exist_ok=True)

            for info in extracted_tables_info:
                t_num = info['table_num']
                p_num = info['page_num']
                csv_filename = f"table_{t_num:02d}_page_{p_num:02d}.csv"
                csv_path = output_dir / csv_filename
                
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for row in info['data']:
                        clean_row = [cell if cell is not None else "" for cell in row]
                        writer.writerow(clean_row)

            print(f"\n[✓] Extracted {table_count} tables")
            print(f"[✓] Output: {output_dir.name}")
            print(f"    Location: {output_dir.resolve()}")

    except Exception as e:
        print(f"\n[ERROR] Failed to extract tables: {e}")

def run_ocr(path: Path):
    import shutil
    try:
        import pytesseract
    except ImportError:
        print("\n[ERROR] pytesseract is not installed. Please install it first.")
        return

    if shutil.which("tesseract") is None:
        print("\n[ERROR] Tesseract OCR is not installed or not in PATH.")
        print("    Ubuntu/Debian : sudo apt install tesseract-ocr tesseract-ocr-ind")
        print("    macOS         : brew install tesseract")
        print("    Windows       : https://github.com/UB-Mannheim/tesseract/wiki")
        return

    print("\nFormat Output OCR")
    print("─" * 36)
    print("1\tExtract text to file .txt")
    print("2\tCreate a Searchable PDF")
    print("\n0\tBack")
    
    out_format = input("\nInput [1-2/0] : ").strip()
    if out_format == "0":
        return
    if out_format not in ("1", "2"):
        print("\n[!] Invalid selection.")
        return

    lang_choice = input("\nLanguage (eng / ind) [eng] : ").strip().lower()
    if not lang_choice:
        lang_choice = "eng"
    if lang_choice not in ("eng", "ind"):
        print("\n[!] Currently supports only 'eng' or 'ind'.")
        return

    is_pdf = path.suffix.lower() == ".pdf"
    pages = []
    
    if is_pdf:
        from pypdf import PdfReader
        from .pages_organizer import _parse_ranges, _flatten_ranges
        try:
            reader = PdfReader(str(path))
            total = len(reader.pages)
        except Exception as e:
            print(f"\n[ERROR] Unable to open PDF: {e}")
            return
            
        print(f"\n[*] OCR PDF: {path.name} ({total} pages)")
        print("    Input example : 1-3,5  (blank = process ALL pages)")
        raw_range = input("\nPage range: ").strip()
        
        if raw_range:
            ranges = _parse_ranges(raw_range, total)
            if ranges is None:
                print(f"\n[!] Invalid range (pages 1-{total}).")
                return
            pages = _flatten_ranges(ranges)
        else:
            pages = list(range(1, total + 1))
    else:
        pages = [1]
        
    print("\n[*] Processing OCR... Please wait.")
    
    try:
        if is_pdf:
            from pdf2image import convert_from_path
            images = []
            for p in pages:
                print(f"    Scanning page {p}...")
                img_list = convert_from_path(str(path), first_page=p, last_page=p, dpi=300)
                if img_list:
                    images.append(img_list[0])
        else:
            from PIL import Image
            images = [Image.open(path)]
            
        if not images:
            print("\n[!] Failed to load images.")
            return

        if out_format == "1":
            out_file = path.parent / f"{path.stem}_ocr.txt"
            with open(out_file, "w", encoding="utf-8") as f:
                for i, img in enumerate(images):
                    text = pytesseract.image_to_string(img, lang=lang_choice)
                    if is_pdf:
                        f.write(f"--- Page {pages[i]} ---\n")
                    f.write(text)
                    f.write("\n\n")
            print(f"\n[✓] Saved OCR text to: {out_file.name}")
            
        elif out_format == "2":
            out_file = path.parent / f"{path.stem}_searchable.pdf"
            if len(images) == 1:
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(images[0], extension='pdf', lang=lang_choice)
                with open(out_file, "wb") as f:
                    f.write(pdf_bytes)
            else:
                from pypdf import PdfWriter, PdfReader
                import io
                writer = PdfWriter()
                for i, img in enumerate(images):
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf', lang=lang_choice)
                    r = PdfReader(io.BytesIO(pdf_bytes))
                    writer.add_page(r.pages[0])
                with open(out_file, "wb") as f:
                    writer.write(f)
            
            size_kb = out_file.stat().st_size / 1024
            print(f"\n[✓] Searchable PDF created: {out_file.name} ({size_kb:.0f} KB)")
            
    except Exception as e:
        print(f"\n[ERROR] OCR failed: {e}")