# PDFtool

![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

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

In addition to Python, these two system dependencies are required:

| Dependency | Function | Linux | Windows |
|---|---|---|---|
| poppler | convert PDF→JPG | `sudo apt install poppler-utils` | [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases) |
| libreoffice | convert DOC→PDF | `sudo apt install libreoffice` | [libreoffice.org](https://www.libreoffice.org/download/download/) |

## Instalasi

```bash
pipx install git+https://github.com/GhalyRisyadi/pdf-tool.git
```

or use a regular pipe:
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