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

```bash
pdftool
```

## Developer

**Ghaly Risyadi**
- GitHub: @GhalyRisyadi
- Email: vrenty882@hotmail.com
- Instagram : @ghalyrisydi

## License

MIT