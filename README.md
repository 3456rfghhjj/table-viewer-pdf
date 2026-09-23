# Table Viewer & PDF Exporter

A clean, full-screen desktop application built with Python and CustomTkinter to open, view, and export spreadsheets into clean PDF documents.

## Features
- **Multi-Format Support:** Opens Excel (`.xlsx`, `.xls`), Apple Numbers (`.numbers`), and CSV (`.csv`) files.
- **Smart CSV Parsing:** Automatically detects comma and semicolon delimiters.
- **Modern Dark GUI:** Full-screen table overview built on CustomTkinter with smooth scrolling.
- **One-Click PDF Export:** Exports the loaded table into a landscape A4 PDF saved directly to the Desktop.

## Requirements
To install required dependencies, run:
```bash
pip install customtkinter polars fastexcel fpdf2 numbers-parser
```
## How to Run
Run the script using Python:
```bash
python table_viewer_pdf.py
```
