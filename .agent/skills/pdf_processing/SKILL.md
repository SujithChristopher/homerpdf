---
name: PDF Processing
description: Details on PDF overlay creation, merging, and coordinate systems.
---

# PDF Processing

## Overlay Creation (`pdf/overlay.py`)
- Uses **reportlab** `Canvas` to draw text.
- **Coordinate System**: (0,0) is at the bottom-left of the page.
- **Margins**: Controlled by `MARGIN_TOP` and `MARGIN_RIGHT`.
- **Text Format**: `"{event_name}-{center_code}-{hospital_number}"`.

## PDF Manipulation (`pdf/processor.py`)
- Uses **PyPDF** `PdfReader` and `PdfWriter`.
- **Merge Logic**: `page.merge_page(overlay_page)` overlaying the text on top of the original content.
- **Merging Multiple PDFs**: `merger.add_page(page)` for all pages in a list of PDF buffers.

## Testing
- Use a mock hospital number (e.g., `12345`) and center (e.g., `CMC`) to verify positioning.
- Coordinates are in **points** (1/72 inch).
