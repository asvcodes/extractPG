
![image](https://github.com/user-attachments/assets/25dd98f5-7bba-4ffd-97f1-0c25069cd991)

# extractPG - PDF Page Extraction Tool
A Python-based GUI application to search and extract pages from PDF files based on text patterns. Perfect for quickly isolating relevant content from large PDF documents.

## Features

- **Search Patterns**: Find pages using plain text or regex patterns
- **Case Sensitivity**: Option to enable/disable case-sensitive search
- **Regex Support**: Use regular expressions for advanced pattern matching
- **Progress Tracking**: Visual progress bar and status updates
- **Cancellation Support**: Stop long-running operations mid-process
- **Multi-threaded Processing**: Maintain responsive UI during operations
- **PDF/A Support**: Handles most PDF formats including PDF/A

## Installation

### Requirements
- Python 3.8+
- Tkinter (usually included with Python)
- [PyMuPDF](https://pypi.org/project/PyMuPDF/) (Fitz)
- [PyPDF2](https://pypi.org/project/PyPDF2/)

### Setup
```bash
# Install required packages
pip install PyMuPDF PyPDF2

# Clone repository (optional)
git clone https://github.com/asvcodes/extractPG.git
cd extractPG
```

## Usage

1. **Launch the application**
   ```bash
   python extractPG.py
   ```
2. Select input PDF using the "Browse" button
3. Enter your search pattern (text or regex)
4. Choose search options:
   - ☑️ Case Sensitive: Match exact casing
   - ☑️ Regex Search: Enable regular expression mode
5. Click "Process" and choose output file location
6. Monitor progress via the status bar and progress indicator
7. Click "Cancel" anytime to abort processing

## How It Works

1. **Text Extraction**: Uses PyMuPDF (Fitz) for fast text extraction from PDF pages
2. **Pattern Matching**:
   - Plain text search with optional case sensitivity
   - Regular expression support for complex patterns
3. **Page Selection**: Creates list of pages containing matches
4. **PDF Assembly**: Uses PyPDF2 to create new PDF with only matching pages
5. **Memory Management**: Processes files in chunks to handle large documents

## License

This project is [MIT licensed](LICENSE).

## Acknowledgments

- Powered by:
  - [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for PDF text extraction
  - [PyPDF2](https://github.com/py-pdf/PyPDF2) for PDF writing operations
  - Tkinter for the GUI framework

---

**Disclaimer**: This tool works with most PDFs but may not handle scanned documents or images. Always verify results with critical documents.
