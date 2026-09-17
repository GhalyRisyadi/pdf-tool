# PDFtool

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)
[![codecov](https://codecov.io/github/GhalyRisyadi/pdf-tool/graph/badge.svg?token=7UNQEW7VV1)](https://codecov.io/github/GhalyRisyadi/pdf-tool)

CLI tool for converting and compressing PDF, JPG, and DOC/DOCX files directly from the terminal.

## Why use this?

Online services like iLovePDF, SmallPDF, etc., require you to **upload documents to a third-party server** for processing. For sensitive documents (ID cards, driver’s licenses, diplomas, certificates, etc.), this poses a privacy risk. You don’t know where the data is stored, how long it will be kept, or who can access it. There is a risk that your personal data could be misused.

PDFtool processes all files **100% on your own computer**. No uploads, no servers, and no internet connection are required when processing files. Your documents never leave your device.

## Features

- **Info file** — Check the metadata for PDF, JPG, and DOCX files.
- **Convert file** — Supports PDF, DOC, JPG, PNG, TXT, Markdown, and HTML.
- **Optimize file** — Compress PDF, JPG, and DOCX files at 3 levels. Repair PDF and PDF/A. 
- **Pages Organizer** — Merge and Split PDF, DOCX. Extract pages, Delete pages, and Rotate pages.
- **Content Extraction** — Extract images, tables, and links from PDF files.
- **Privacy file** — Strip metadata (PDF, JPG), Encrypt, Decrypt, Sanitize, Redact. 

## Prerequisites Before Installation

In addition to Python, these system dependencies are required:

| Dependency | Function | Linux | Windows |
|---|---|---|---|
| poppler | convert PDF→JPG | `sudo apt install poppler-utils` | [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) |
| libreoffice | convert DOC→PDF | `sudo apt install libreoffice` | [libreoffice.org](https://www.libreoffice.org/download/) |
| gs(Ghostscript) | convert PDF→PDF/A | `sudo apt install ghostscript` | [Ghostscript](https://www.ghostscript.com/releases/) |
| qpdf | repair PDF | `sudo apt install qpdf` | [qpdf](https://github.com/qpdf/qpdf/releases/latest)|
| tesseract | OCR | `sudo apt install tesseract-ocr` (add `tesseract-ocr-ind` for Indonesian) | [tesseract](https://github.com/UB-Mannheim/tesseract/wiki) |

## Installation

```bash
pipx install git+https://github.com/GhalyRisyadi/pdf-tool.git
```

or use regular pip:
```bash
pip install git+https://github.com/GhalyRisyadi/pdf-tool.git
```

## How to Use

PDFtool supports **Dual-Mode**: run it interactively like a wizard, or run direct commands for fast scripting and automation.

### 1. Interactive Wizard Mode
Launch the interactive terminal menu:
```bash
pdftool
```

### 2. Direct CLI Mode (Fast with Shorthand Aliases)
Execute operations directly from the terminal without prompts. Both full names and short aliases are supported:

| Category | Command | Shorthand | Example Usage | Description |
|---|---|---|---|---|
| **Info** | `info` | `in` | `pdftool in file.pdf` | Inspect document metadata & structure |
| **Convert** | `convert` | `cv` | `pdftool cv doc.docx --to pdf` | Convert between PDF, DOCX, JPG, PNG, MD, TXT, HTML |
| | | | `pdftool cv report.pdf --to md -o out.md` | Convert with custom output path |
| **Optimize** | `optimize` | `opti` / `opt` | `pdftool opti doc.pdf -l high` | Compress file (levels: 1=Low, 2=Medium, 3=High) |
| | | | `pdftool opti broken.pdf --repair` | Repair corrupted PDF structure |
| | | | `pdftool opti doc.pdf --pdfa` | Convert to standardized PDF/A archive format |
| **Pages** | `pages merge` | `pg mg` | `pdftool pg mg a.pdf b.pdf -o out.pdf` | Merge multiple PDF or DOCX files |
| | `pages split` | `pg sp` | `pdftool pg sp doc.pdf` | Split document into single pages |
| | `pages reorder` | `pg re` | `pdftool pg re doc.pdf --order "3,1,2"` | Reorder pages of a PDF |
| | `pages rotate` | `pg rot` | `pdftool pg rot doc.pdf -a 90 -p "1-2"` | Rotate pages clockwise (90°, 180°, 270°) |
| | `pages delete` | `pg del` / `rm` | `pdftool pg del doc.pdf -p "2, 4-5"` | Delete specific pages from a PDF |
| | `pages extract` | `pg ext` | `pdftool pg ext doc.pdf -p "1-3"` | Extract specific pages into a new PDF |
| **Extract** | `extract ocr` | `ex ocr` | `pdftool ex ocr scan.pdf --lang ind` | OCR to text or searchable PDF (`--to pdf`) |
| | `extract images` | `ex img` | `pdftool ex img doc.pdf -o ./output/` | Extract embedded images (lossless) |
| | `extract tables` | `ex tbl` | `pdftool ex tbl doc.pdf` | Extract tables into CSV format |
| | `extract links` | `ex url` | `pdftool ex url doc.pdf` | Extract all external URLs and links |
| **Privacy** | `privacy sanitize` | `priv san` | `pdftool priv san secret.pdf` | Deep clean: strip JS, actions, attachments |
| | `privacy scan-pii` | `priv pii` | `pdftool priv pii form.pdf` | Scan for emails, phones, credit cards |
| | `privacy strip` | `priv st` | `pdftool priv st doc.pdf` | Remove metadata (PDF) or EXIF (JPG) |
| | `privacy encrypt` | `priv enc` | `pdftool priv enc doc.pdf` | Lock with AES-256 password protection |
| | `privacy decrypt` | `priv dec` | `pdftool priv dec doc.pdf` | Unlock password or remove restrictions |
| | `privacy redact` | `priv red` | `pdftool priv red doc.pdf` | Permanently redact sensitive text |

To view detailed help and all flags for any command:
```bash
pdftool --help
pdftool cv --help
pdftool pg --help
```

## Developer

**Ghaly Risyadi**
- GitHub: @GhalyRisyadi
- Email: vrenty882@hotmail.com
- Instagram : @ghalyrisydi

## License

MIT