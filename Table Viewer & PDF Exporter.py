import os
import sys
import warnings
import customtkinter as ctk
from tkinter import ttk, filedialog
import polars as pl
from fpdf import FPDF
from numbers_parser import Document

warnings.filterwarnings("ignore")

current_df = None
PDF_PATH = os.path.expanduser("~/Desktop/Table_Export.pdf")

# Load Excel, CSV, or Apple Numbers files
def load_file(file_path):
    global current_df
    ext = os.path.splitext(file_path)[1].lower()

    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, "w")
    try:
        if ext in [".xlsx", ".xls"]:
            current_df = pl.read_excel(file_path)

        elif ext == ".csv":
            with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                first_line = f.readline()
                delimiter = ";" if ";" in first_line else ","
            current_df = pl.read_csv(file_path, separator=delimiter)

        elif ext == ".numbers":
            doc = Document(file_path)
            table = doc.sheets[0].tables[0]
            data = table.rows(values_only=True)

            header = [str(col) if col is not None else f"Column_{i}" for i, col in enumerate(data[0])]
            rows = data[1:]

            table_dict = {header[i]: [r[i] for r in rows] for i in range(len(header))}
            current_df = pl.DataFrame(table_dict)

        else:
            raise ValueError("Unsupported file format.")

    except Exception as e:
        sys.stderr.close()
        sys.stderr = old_stderr
        lbl_status.configure(text=f"Error: {e}", text_color="#E06D6D")
        return
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr

    refresh_table()

# Open file selection dialog
def select_file():
    file_path = filedialog.askopenfilename(
        title="Select Spreadsheet File",
        filetypes=[
            ("All Supported Formats", "*.xlsx *.xls *.csv *.numbers"),
            ("Apple Numbers", "*.numbers"),
            ("Excel Files", "*.xlsx *.xls"),
            ("CSV Files", "*.csv")
        ]
    )
    if file_path:
        lbl_file.configure(text=f"File: {os.path.basename(file_path)}")
        load_file(file_path)

# Refresh Treeview table display
def refresh_table():
    global current_df
    if current_df is None:
        return

    for item in tree.get_children():
        tree.delete(item)

    tree["columns"] = current_df.columns
    for col in current_df.columns:
        tree.heading(col, text=str(col)[:18])
        tree.column(col, anchor="center", width=120)

    for row in current_df.iter_rows():
        clean_values = ["" if v is None else str(v) for v in row]
        tree.insert("", "end", values=clean_values)

    lbl_status.configure(text=f"Loaded rows: {len(current_df)}", text_color="#76C893")

# Export table to PDF on Desktop
def export_pdf():
    global current_df
    if current_df is None:
        lbl_status.configure(text="Please select a file first!", text_color="#E06D6D")
        return

    pdf = FPDF(orientation="landscape", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "Table Overview", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("helvetica", "B", 8)
    col_count = max(len(current_df.columns), 1)
    col_width = 270 / col_count

    for col in current_df.columns:
        pdf.cell(col_width, 8, str(col)[:14], border=1, align="C")
    pdf.ln()

    pdf.set_font("helvetica", "", 7)
    for row in current_df.iter_rows():
        for val in row:
            text = "" if val is None else str(val)[:14]
            pdf.cell(col_width, 6, text, border=1, align="C")
        pdf.ln()

    pdf.output(PDF_PATH)
    lbl_status.configure(text=f"PDF saved to Desktop:\n{PDF_PATH}", text_color="#76C893")

# GUI Configuration
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Table Viewer & PDF Exporter")

# Fullscreen mode (Press ESC to exit fullscreen)
app.attributes("-fullscreen", True)
app.bind("<Escape>", lambda event: app.attributes("-fullscreen", False))

frame_main = ctk.CTkFrame(app, corner_radius=12)
frame_main.pack(fill="both", expand=True, padx=25, pady=25)

lbl_title = ctk.CTkLabel(
    frame_main, 
    text="Table Viewer & PDF Exporter (Excel / Numbers / CSV)", 
    font=ctk.CTkFont(size=24, weight="bold")
)
lbl_title.pack(pady=(15, 5))

lbl_file = ctk.CTkLabel(
    frame_main, 
    text="No file selected yet", 
    font=ctk.CTkFont(size=14), 
    text_color="#A3C1AD"
)
lbl_file.pack(pady=(0, 10))

# Table frame
frame_table = ctk.CTkFrame(frame_main)
frame_table.pack(fill="both", expand=True, padx=20, pady=10)

style = ttk.Style()
style.theme_use("default")
style.configure(
    "Treeview", 
    background="#1B2E20", 
    foreground="#FFFFFF", 
    fieldbackground="#1B2E20", 
    rowheight=26, 
    font=("Arial", 11)
)
style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#2D4A35", foreground="#FFFFFF")

tree = ttk.Treeview(frame_table, show="headings")

scrollbar_y = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
scrollbar_x = ttk.Scrollbar(frame_table, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.pack(side="right", fill="y")
scrollbar_x.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

# Controls
frame_buttons = ctk.CTkFrame(frame_main, fg_color="transparent")
frame_buttons.pack(pady=15)

btn_select = ctk.CTkButton(
    frame_buttons,
    text="Open File (Excel / Numbers / CSV)",
    font=ctk.CTkFont(size=15, weight="bold"),
    height=45,
    width=260,
    command=select_file
)
btn_select.pack(side="left", padx=15)

btn_export = ctk.CTkButton(
    frame_buttons,
    text="Export to PDF (Desktop)",
    font=ctk.CTkFont(size=15, weight="bold"),
    height=45,
    width=220,
    command=export_pdf
)
btn_export.pack(side="left", padx=15)

lbl_status = ctk.CTkLabel(frame_main, text="", font=ctk.CTkFont(size=13))
lbl_status.pack(pady=(0, 10))

app.mainloop()