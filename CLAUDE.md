# CLAUDE.md - Hospital PDF Manager Codebase Guide

This document provides comprehensive information about the Hospital PDF Manager codebase for developers and AI assistants working on this project.

## Project Overview

**Hospital PDF Manager** is a PySide6 desktop application that adds hospital numbers to medical assessment PDFs. It allows users to:
- Enter a patient's hospital number
- Select a medical center (CMC, Manipal, Ludhiana)
- Select multiple PDFs to process
- Add hospital number overlay to all selected PDFs
- Download individual or merged PDFs
- Print PDFs directly from the application

**Key Technology Stack:**
- Python 3.13
- PySide6 6.10.1 (Qt for Python)
- PyPDF 6.6.0 (PDF manipulation)
- reportlab 4.2.0 (PDF text overlay)
- matplotlib 3.10.8 (visualization support)

## Architecture Overview

### High-Level Data Flow

```
User Input
    ↓
Hospital Number + Center Selection + PDF Selection
    ↓
PDF Processing (Add Hospital Number Overlay)
    ↓
[Optional] Merge PDFs
    ↓
Download to Disk / Print (Open in Viewer)
```

### Component Architecture

```
┌─────────────────────────────────────────────────┐
│         PySide6 GUI Layer                       │
│  (ui/main_window.py - User Interface)          │
└──────────────────┬──────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────┐
│    PDF Processing Layer                         │
│  ┌──────────────────┐  ┌────────────────────┐   │
│  │ PDFProcessor     │  │ OverlayCreator    │   │
│  │ (processor.py)   │  │ (overlay.py)      │   │
│  └──────────────────┘  └────────────────────┘   │
└──────────────────┬───────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────┐
│    Utility Layer                                 │
│  ┌──────────────────────────────────────────┐   │
│  │ Input Validators (validators.py)         │   │
│  └──────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

## Key Files and Their Responsibilities

### Entry Point
- **`main.py`**
  - Initializes QApplication
  - Creates and displays MainWindow
  - Sets application metadata (name, version)
  - Entry point: `python main.py` or `uv run python main.py`

### User Interface Layer
- **`ui/main_window.py`** (438 lines)
  - `MainWindow` class: Main application window
  - Layout: Hospital number input, center dropdown, PDF list with checkboxes, merge checkbox, download/print buttons
  - Button handlers: `on_download_clicked()`, `on_print_clicked()`
  - Validation: `validate_inputs()`, `update_button_states()`
  - PDF selection: `get_selected_pdfs()`
  - Window size: Fixed 550x650px
  - Status bar for operation feedback

### PDF Processing Layer
- **`pdf/processor.py`** (142 lines)
  - `PDFProcessor` class: Main PDF processing engine
  - Methods:
    - `add_hospital_number()`: Adds overlay to single PDF, returns BytesIO
    - `process_multiple()`: Processes multiple PDFs, returns dict with results
    - `merge_pdfs()`: Merges multiple PDF buffers into single PDF
  - Uses PyPDF's PdfReader/PdfWriter for PDF manipulation
  - Handles encrypted PDFs by raising ValueError
  - Error handling: Gracefully handles corrupted/missing PDFs

- **`pdf/overlay.py`** (44 lines)
  - `OverlayCreator` class: Text overlay generation
  - Method:
    - `create_text_overlay()`: Creates single-page PDF with text at top-right
  - Uses reportlab's Canvas to draw text
  - Position: 20pt from right, 20pt from top
  - Font: Helvetica, 10pt, black color

### Utilities Layer
- **`utils/validators.py`** (26 lines)
  - `validate_hospital_number()`: Validates hospital number input
  - Rules:
    - Non-empty required
    - Max 20 characters
    - Alphanumeric + hyphens only
    - Strips whitespace
  - Returns tuple: (is_valid, error_message)

### Configuration Files
- **`pyproject.toml`**
  - Project metadata (name: homerpdf, version: 0.1.0)
  - Python requirement: >=3.13
  - Dependencies: matplotlib, pypdf, pyside6, reportlab

- **`README.md`**
  - User-facing documentation
  - Installation, usage, features, troubleshooting

- **`.gitignore`**
  - Standard Python ignores (__pycache__, .venv, build/, dist/, etc.)

## Data Flow Details

### Download Workflow (Individual PDFs)

```
User clicks "Download Selected"
    ↓
QFileDialog.getExistingDirectory() [Get save location]
    ↓
FOR each selected PDF:
    - PDFProcessor.add_hospital_number(filename, hospital_num, center_code)
      └─ OverlayCreator.create_text_overlay() [Creates overlay PDF]
      └─ PdfReader reads original PDF
      └─ For each page: merge overlay onto page
      └─ Return modified PDF as BytesIO
    - Write BytesIO to file: {hospital_number}_{pdf_name}.pdf
    ↓
Show success/error message
```

### Download Workflow (Merged)

```
User clicks "Download Selected" + "Merge" checkbox enabled
    ↓
[Same as above, but store all BytesIO objects]
    ↓
PDFProcessor.merge_pdfs([list of BytesIO])
    ↓
PdfWriter combines all pages from all PDFs
    ↓
Save merged PDF: {hospital_number}_merged.pdf
    ↓
Show success message
```

### Print Workflow

```
User clicks "Print Selected"
    ↓
Create temp directory: %TEMP%/homerpdf_print/
    ↓
FOR each selected PDF:
    [Same processing as download]
    ↓
    IF merge enabled:
        Save to temp as {hospital_number}_merged.pdf
    ELSE:
        Save to temp as {hospital_number}_{name}.pdf
    ↓
    QDesktopServices.openUrl() [Open in system viewer]
    ↓
User prints from their familiar PDF viewer
```

## Key Classes and Methods

### MainWindow (ui/main_window.py)

```python
class MainWindow(QMainWindow):
    # UI Setup
    def __init__()
    def setup_ui()
    def center_window()

    # Validation
    def validate_inputs() -> bool
    def set_input_invalid(is_invalid: bool)
    def update_button_states()

    # User Input Handlers
    def on_input_changed()
    def on_selection_changed()
    def get_selected_pdfs() -> list

    # Download/Print Handlers
    def on_download_clicked()
    def on_print_clicked()

    # Data
    CENTERS = [("CMC", "CMC Vellore"), ("MNP", "Manipal Hospital"), ("LDH", "Ludhiana Hospital")]
```

### PDFProcessor (pdf/processor.py)

```python
class PDFProcessor:
    def __init__(pdf_dir: Path)
    def add_hospital_number(pdf_filename: str, hospital_number: str, center_code: str) -> BytesIO
    def process_multiple(pdf_filenames: list, hospital_number: str, center_code: str) -> dict
    def merge_pdfs(pdf_buffers: list) -> BytesIO
```

### OverlayCreator (pdf/overlay.py)

```python
class OverlayCreator:
    FONT_NAME = "Helvetica"
    FONT_SIZE = 10
    MARGIN_TOP = 20
    MARGIN_RIGHT = 20

    @staticmethod
    def create_text_overlay(text: str, page_width: float, page_height: float) -> BytesIO
```

## Important Implementation Details

### PDF Overlay Mechanism

1. **reportlab** creates an in-memory PDF with text positioned at top-right
2. PyPDF **merges** this overlay onto each page of the original PDF
3. Text format: `"{CENTER_CODE}-{HOSPITAL_NUMBER}"` (e.g., "CMC-12345")
4. Position: Calculated from page dimensions with fixed margins
5. No compression or quality loss - original PDF quality preserved

### Error Handling Strategy

- **File not found**: Show error, skip file, continue with others
- **Encrypted PDF**: Raise ValueError, show error to user
- **Corrupted PDF**: Catch exception, skip, show warning
- **Permission denied**: Catch during write, show specific error
- **No PDFs selected**: Disable buttons, show tooltip
- **Invalid hospital number**: Red border on input, buttons disabled

### Input Validation

Hospital number validation happens in two places:
1. Real-time: As user types (red border feedback)
2. On submit: Full validation before processing

Allowed characters: `[a-zA-Z0-9\-]` (letters, numbers, hyphens)

### UI State Management

Buttons are enabled/disabled based on:
- Hospital number must be valid (non-empty, proper format)
- At least one PDF must be selected
- Center is always valid (dropdown ensures this)

Status bar shows:
- "Ready" when idle
- "Processing..." during operations
- "Downloaded X PDF(s)" after success
- Error messages for failures

## Common Workflows for Development

### Adding a New Feature

1. **UI Changes**: Modify `ui/main_window.py`
   - Add new widget in `setup_ui()`
   - Connect signals/slots
   - Add handler method
   - Update validation if needed

2. **PDF Processing Changes**: Modify `pdf/processor.py`
   - Add new method to PDFProcessor
   - Test with test script
   - Update MainWindow to use new method

3. **Validation Changes**: Modify `utils/validators.py`
   - Add new validation function
   - Return (is_valid, error_message) tuple
   - Update MainWindow to call validator

### Testing Changes

Create test script (e.g., `test_feature.py`):
```python
from pdf.processor import PDFProcessor

def test_feature():
    processor = PDFProcessor(Path(__file__).parent / "files")
    # Test code
    print("[OK] Feature works!")

if __name__ == "__main__":
    test_feature()
```

Run with: `uv run python test_feature.py`

### Debugging Tips

1. **PDF Processing Issues**:
   - Check page dimensions with `page.mediabox.width/height`
   - Verify overlay text positioning with test output
   - Check for encrypted PDFs

2. **UI Issues**:
   - Check widget sizing with `setFixedSize(550, 650)`
   - Verify signal/slot connections
   - Test validation logic with edge cases

3. **File I/O Issues**:
   - Verify file paths are absolute
   - Check file permissions
   - Ensure temp directory is accessible

## Testing Strategy

### Manual Testing Checklist

- [ ] Enter valid hospital number (e.g., "12345")
- [ ] Select different centers
- [ ] Select single PDF → download works
- [ ] Select multiple PDFs → download works
- [ ] Check merge checkbox + select multiple → merged PDF created
- [ ] Print single PDF → opens in viewer
- [ ] Print multiple PDFs → opens all in viewer
- [ ] Print with merge → opens merged PDF
- [ ] Try invalid hospital number → error feedback
- [ ] Leave hospital number empty → buttons disabled
- [ ] Uncheck all PDFs → buttons disabled

### Automated Testing

Run validation tests:
```bash
cd E:\homer\homerpdf
uv run python -c "from utils.validators import validate_hospital_number; assert validate_hospital_number('12345')[0]"
```

Test PDF processing:
```bash
from pdf.processor import PDFProcessor
from pathlib import Path

processor = PDFProcessor(Path("files"))
result = processor.add_hospital_number("arat.pdf", "12345", "CMC")
assert len(result.getvalue()) > 0
```

## Extending the Application

### Adding More Centers

In `ui/main_window.py`, update CENTERS:
```python
CENTERS = [
    ("CMC", "CMC Vellore"),
    ("MNP", "Manipal Hospital"),
    ("LDH", "Ludhiana Hospital"),
    ("NEW", "New Center"),  # Add here
]
```

### Customizing Text Format

In `pdf/processor.py`, update the overlay_text format:
```python
# Current format
overlay_text = f"{center_code}-{hospital_number}"

# Could be changed to
overlay_text = f"Hospital: {hospital_number} ({center_code})"
```

### Adding More PDF Files

Simply place PDF files in the `files/` folder. They're automatically discovered and listed.

### Changing Text Position

In `pdf/overlay.py`, adjust these constants:
```python
MARGIN_TOP = 20      # Distance from top (in points)
MARGIN_RIGHT = 20    # Distance from right (in points)
FONT_SIZE = 10       # Font size in points
```

### Adding PDF Page Numbering

Would require modifying `overlay.py` to include page number in overlay text. Could add to `OverlayCreator.create_text_overlay()`.

## Dependencies and Versions

- **Python**: 3.13+ (using modern features)
- **PySide6**: 6.10.1+ (Qt 6.x compatible)
- **PyPDF**: 6.6.0+ (using modern merge API)
- **reportlab**: 4.2.0+ (PDF canvas drawing)
- **matplotlib**: 3.10.8+ (included, for future use)

All managed via `uv` package manager (uv.lock ensures reproducibility).

## Known Limitations and Future Improvements

### Current Limitations
- Window size is fixed (550x650px) - not resizable
- Text overlay only, no image annotations
- No PDF preview functionality
- No undo/redo functionality
- Single hospital number per operation

### Planned Improvements
- Customizable overlay position and formatting
- CSV batch processing (multiple hospital numbers)
- PDF preview before download
- Merge with bookmarks/table of contents
- Remember last used center
- Operation log/history
- Dark mode support
- Drag-and-drop file selection

## Performance Considerations

- **In-Memory Processing**: All PDFs processed in memory (BytesIO buffers)
- **No Temporary Files**: Processing doesn't create temporary files (only for printing)
- **Large PDFs**: May consume memory proportional to PDF size
- **Batch Operations**: Multiple PDFs are processed sequentially (single-threaded)

For very large PDFs (>100MB) or many PDFs (>50), consider adding:
- Threading for batch processing
- Streaming file I/O instead of in-memory
- Progress bar improvements

## Troubleshooting Guide

### Application won't start
```
Error: ModuleNotFoundError
Solution: Run `uv sync` to install dependencies
```

### Hospital number validation too strict
- Check regex in `utils/validators.py` (currently `^[a-zA-Z0-9\-]+$`)
- Modify if different characters needed

### PDFs not appearing
- Ensure files are in `E:\homer\homerpdf\files\` folder
- Check filenames end with `.pdf`
- Application scans with `*.pdf` glob pattern

### Text overlay positioning wrong
- Check page dimensions: `print(f"Page: {width}x{height}")`
- Verify font metrics with `canvas.stringWidth()`
- Adjust MARGIN_TOP and MARGIN_RIGHT in `overlay.py`

### Print dialog doesn't appear
- Windows only - uses QDesktopServices.openUrl()
- Requires default PDF viewer set in system
- Alternative: Use download feature first

## Code Quality Notes

- **PEP 8 Compliant**: Code follows Python style guide
- **Type Hints**: Most functions have type hints
- **Docstrings**: All classes and methods documented
- **Error Handling**: Graceful degradation on errors
- **No Magic Numbers**: Constants defined at top of classes
- **Modular Design**: Clear separation of concerns (UI / PDF / Utils)

## Questions and Support

For questions about specific parts of the code:
1. Check docstrings in the relevant module
2. Look at test files for usage examples
3. Review README.md for feature documentation
4. Check this CLAUDE.md for architecture details
