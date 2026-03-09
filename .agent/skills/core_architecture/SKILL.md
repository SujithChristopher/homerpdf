---
name: Core Architecture
description: Overview of the project structure, technology stack, and high-level data flow.
---

# Core Architecture

## Project Overview
**Hospital PDF Manager** is a PySide6 desktop application designed to add hospital numbers to medical assessment PDFs.

## Technology Stack
- **Python**: 3.13+
- **PySide6**: 6.10.1+ (GUI Framework)
- **PyPDF**: 6.6.0+ (PDF manipulation)
- **reportlab**: 4.2.0+ (PDF text overlay)

## Directory Structure
- `ui/`: User Interface components (PySide6)
- `pdf/`: PDF processing engine and overlay logic
- `redcap/`: REDCap instrument definitions (CSV) and cleanup scripts
- `utils/`: Common utilities (validators, loggers, path helpers)
- `files/`: Source PDF templates

## Data Flow
1. **Input**: User enters hospital number and selects a center/timepoint.
2. **Processing**: `PDFProcessor` merges a `reportlab`-generated overlay onto the selected PDFs.
3. **Output**: Modified PDFs are saved to disk or opened in a system viewer for printing.

## Key Classes
- `MainWindow` (`ui/main_window.py`): Entry point for UI interactions.
- `PDFProcessor` (`pdf/processor.py`): Handles PDF reading, merging, and writing.
- `OverlayCreator` (`pdf/overlay.py`): Creates the text overlay using `reportlab`.
