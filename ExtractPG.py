import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
import re
import fitz  
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='pdf_search.log'
)

class PDFSearchApp:
    def __init__(self, master):
        self.master = master
        master.title("extractPG")
        master.geometry("600x400")
        
        # Processing control
        self.abort_flag = False
        self.current_process: Optional[threading.Thread] = None

        # UI Elements
        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        # Input PDF
        self.input_label = ttk.Label(self.master, text="Input PDF:")
        self.input_entry = ttk.Entry(self.master, width=50)
        self.input_button = ttk.Button(
            self.master, text="Browse", command=self.browse_input
        )

        # Search options
        self.search_label = ttk.Label(self.master, text="Search Pattern:")
        self.search_entry = ttk.Entry(self.master, width=50)
        self.case_sensitive = tk.BooleanVar(value=False)
        self.regex_mode = tk.BooleanVar(value=False)
        self.options_frame = ttk.Frame(self.master)
        self.case_check = ttk.Checkbutton(
            self.options_frame, text="Case Sensitive", variable=self.case_sensitive
        )
        self.regex_check = ttk.Checkbutton(
            self.options_frame, text="Regex Search", variable=self.regex_mode
        )

        # Progress
        self.progress = ttk.Progressbar(
            self.master, orient="horizontal", length=400, mode="determinate"
        )
        self.status_var = tk.StringVar(value="Greetings, from ASV!")
        self.status_label = ttk.Label(
            self.master, textvariable=self.status_var, anchor="w"
        )

        # Actions
        self.button_frame = ttk.Frame(self.master)
        self.process_btn = ttk.Button(
            self.button_frame, text="Process", command=self.start_processing
        )
        self.cancel_btn = ttk.Button(
            self.button_frame, text="Cancel", command=self.cancel_processing, state=tk.DISABLED
        )

    def setup_layout(self):
        self.input_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.input_button.grid(row=0, column=2, padx=5, pady=5)

        self.search_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.search_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.options_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.case_check.pack(side="left", padx=5)
        self.regex_check.pack(side="left", padx=5)

        self.progress.grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="ew")
        self.status_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        self.button_frame.grid(row=5, column=1, pady=10)
        self.process_btn.pack(side="left", padx=5)
        self.cancel_btn.pack(side="left", padx=5)

        self.master.columnconfigure(1, weight=1)

    def browse_input(self):
        filename = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filename:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)

    def start_processing(self):
        if self.current_process and self.current_process.is_alive():
            messagebox.showwarning("Warning", "A process is already running")
            return

        input_pdf = self.input_entry.get()
        search_text = self.search_entry.get().strip()
        
        if not input_pdf:
            messagebox.showerror("Error", "Please select an input PDF file")
            return
        if not search_text:
            messagebox.showerror("Error", "Please enter a search pattern")
            return

        output_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Output PDF As"
        )
        if not output_pdf:
            return

        self.abort_flag = False
        self.progress["value"] = 0
        self.update_ui_state(processing=True)
        
        self.current_process = threading.Thread(
            target=self.process_pdf,
            args=(input_pdf, output_pdf, search_text),
            daemon=True
        )
        self.current_process.start()

    def process_pdf(self, input_path: str, output_path: str, search_text: str):
        try:
            # Get total pages first for progress calculation
            with fitz.open(input_path) as doc:
                total_pages = doc.page_count

            # Find matching pages
            matching_pages = self.find_matching_pages(input_path, search_text, total_pages)
            if self.abort_flag:
                self.update_status("Processing aborted")
                return

            # Write output PDF
            self.write_output_pdf(input_path, output_path, matching_pages)
            
            msg = f"Success: {len(matching_pages)} pages saved to {output_path}"
            self.update_status(msg)
            logging.info(msg)

        except Exception as e:
            logging.error(f"Error processing PDF: {str(e)}")
            self.update_status(f"Error: {str(e)}")
        finally:
            self.update_ui_state(processing=False)

    def find_matching_pages(self, input_path: str, search_text: str, total_pages: int) -> List[int]:
        matching_pages = []
        case_sensitive = self.case_sensitive.get()
        use_regex = self.regex_mode.get()

        try:
            pattern = None
            if use_regex:
                flags = re.NOFLAG if case_sensitive else re.IGNORECASE
                pattern = re.compile(search_text, flags=flags)

            with fitz.open(input_path) as doc:
                for page_num in range(doc.page_count):
                    if self.abort_flag:
                        break

                    page = doc.load_page(page_num)
                    text = page.get_text()

                    if use_regex:
                        found = bool(pattern.search(text)) if text else False
                    else:
                        if case_sensitive:
                            found = search_text in text
                        else:
                            found = search_text.lower() in text.lower()

                    if found:
                        matching_pages.append(page_num)

                    # Update progress
                    progress = (page_num + 1) / total_pages * 100
                    self.update_progress(progress, f"Processing page {page_num + 1}/{total_pages}")

        except Exception as e:
            logging.error(f"Search error at page {page_num}: {str(e)}")
            raise

        return matching_pages

    def write_output_pdf(self, input_path: str, output_path: str, pages: List[int]):
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for i, page_num in enumerate(pages):
                if self.abort_flag:
                    break
                
                writer.add_page(reader.pages[page_num])
                # Write in chunks to save memory
                if i % 100 == 0:
                    with open(output_path, "ab") as f:
                        writer.write(f)
                    writer = PdfWriter()
                
                progress = (i + 1) / len(pages) * 100
                self.update_progress(progress, f"Writing page {i + 1}/{len(pages)}")

            # Write remaining pages
            if writer.pages and not self.abort_flag:
                with open(output_path, "ab") as f:
                    writer.write(f)

        except Exception as e:
            logging.error(f"Write error: {str(e)}")
            raise

    def cancel_processing(self):
        self.abort_flag = True
        self.update_status("Cancelling...")
        self.cancel_btn.config(state=tk.DISABLED)

    def update_ui_state(self, processing: bool):
        state = tk.DISABLED if processing else tk.NORMAL
        self.process_btn.config(state=state)
        self.cancel_btn.config(state=tk.DISABLED if not processing else tk.NORMAL)
        self.input_button.config(state=state)
        self.search_entry.config(state=state)

    def update_progress(self, value: float, message: str):
        self.master.after(0, lambda: self.progress.configure(value=value))
        self.update_status(message)

    def update_status(self, message: str):
        self.master.after(0, lambda: self.status_var.set(message))

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFSearchApp(root)
    root.mainloop()