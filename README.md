# Hospital PDF Manager

A clean, simple PySide6 desktop application that adds hospital numbers to medical assessment PDFs. Perfect for managing patient documentation across multiple medical centers.

## Features

- **Easy Hospital Number Entry**: Simple input field for hospital numbers
- **Multi-Center Support**: Select from 3 medical centers (CMC Chennai, Manipal Hospital, Ludhiana Hospital)
- **Batch Processing**: Select and process multiple PDFs at once
- **PDF Overlay**: Automatically adds hospital number to the top-right corner of each PDF page
  - Format: "{CENTER_CODE}-{HOSPITAL_NUMBER}" (e.g., "CMC-12345")
- **Download**: Save modified PDFs with automatic naming (`{hospital_number}_{original_name}.pdf`)
- **Print**: Open PDFs in your default viewer for immediate printing
- **Input Validation**: Real-time validation with helpful error messages

## Supported Medical Assessment Forms

The application works with the following PDF files in the `files/` folder:
- ARAT (Action Research Arm Test)
- FMA-UE (Fugl-Meyer Assessment - Upper Extremity)
- MOCA (Montreal Cognitive Assessment)
- MODRANKINSCALE (Modified Rankin Scale)

## System Requirements

- Python 3.13+
- Windows (or any OS with PySide6 support)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   uv sync
   ```

## Running the Application

```bash
uv run python main.py
```

The application window will open with a clean interface.

## How to Use

1. **Enter Hospital Number**: Type the patient's hospital number in the input field (alphanumeric + hyphens allowed, max 20 characters)

2. **Select Center**: Choose the medical center from the dropdown:
   - CMC Chennai
   - Manipal Hospital
   - Ludhiana Hospital

3. **Select PDFs**: Check the PDF files you want to process from the list

4. **Download or Print**:
   - **Download**: Click "Download Selected" to save the modified PDFs to a folder of your choice
   - **Print**: Click "Print Selected" to open the PDFs in your default PDF viewer for printing

## Project Structure

```
homerpdf/
├── main.py                    # Application entry point
├── ui/
│   ├── __init__.py
│   └── main_window.py         # Main GUI window and logic
├── pdf/
│   ├── __init__.py
│   ├── overlay.py             # Text overlay creation (reportlab)
│   └── processor.py           # PDF modification engine (pypdf)
├── utils/
│   ├── __init__.py
│   └── validators.py          # Input validation
├── files/                     # Medical assessment PDFs
│   ├── arat.pdf
│   ├── fma-ue.pdf
│   ├── moca.pdf
│   └── modrankinscale.pdf
├── pyproject.toml             # Project dependencies
└── README.md                  # This file
```

## Technical Details

### Dependencies

- **PySide6** (6.10.1+): Qt for Python - GUI framework
- **PyPDF** (6.6.0+): PDF manipulation and merging
- **reportlab** (4.2.0+): PDF text overlay generation
- **matplotlib** (3.10.8+): Data visualization (included for future enhancements)

### PDF Processing

The application uses:
1. **reportlab** to create transparent overlay PDFs with text positioned at the top-right corner
2. **PyPDF** to merge the overlay with each page of the original PDF
3. In-memory processing (no temporary files required for processing)

### Text Positioning

- Position: 20pt from the right edge, 20pt from the top edge
- Font: Helvetica, 10pt
- Color: Black
- Format: "{CENTER_CODE}-{HOSPITAL_NUMBER}"

## Error Handling

The application gracefully handles:
- Missing or corrupted PDF files
- Invalid input (empty hospital number, special characters)
- File system errors (permission denied, disk full)
- User cancellation of file dialogs

## Troubleshooting

**"No PDFs found in files/ directory"**
- Ensure PDF files are in the `files/` folder
- Check file names end with `.pdf`

**"Cannot write to {path}"**
- Check that the selected download folder is writable
- Ensure you have sufficient disk space

**Hospital number appears invalid**
- Use only letters, numbers, and hyphens
- Maximum 20 characters
- No special characters (@, !, *, etc.)

## Future Enhancements

Potential features for future versions:
- Customizable text position and formatting
- Batch processing from CSV file (list of hospital numbers)
- PDF preview before download/print
- Remember last used center per session
- Export log of processed PDFs

## License

This project is provided as-is for medical center use.
