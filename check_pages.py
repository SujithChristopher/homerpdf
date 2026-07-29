"""OCR Page Number Verification Tool.

This script runs OCR on a PDF file (if it is a scanned image-only PDF)
and verifies if all page numbers (typically formatted as "Page X of Y")
are present and readable on every page.
"""

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path

# Try to import pypdf and ocrmypdf
try:
    import pypdf
except ImportError:
    print("[ERROR] pypdf is not installed in the python environment. Please run 'uv sync'.")
    sys.exit(1)

try:
    import ocrmypdf
except ImportError:
    print("[ERROR] ocrmypdf is not installed in the python environment. Please run 'uv sync'.")
    sys.exit(1)

# Dynamically add standard Tesseract OCR path on Windows to process PATH
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR"
if sys.platform == "win32" and os.path.exists(TESSERACT_PATH):
    if TESSERACT_PATH not in os.environ["PATH"]:
        os.environ["PATH"] = TESSERACT_PATH + os.pathsep + os.environ["PATH"]


def verify_page_text(text: str, page_num: int, total_pages: int) -> tuple[str, str]:
    """Analyze the page text to verify if the page number is present.

    Args:
        text: Extracted text from the PDF page.
        page_num: 1-based page index.
        total_pages: Total page count.

    Returns:
        A tuple of (status, match_detail) where:
        - status: "OK" (exact Page X of Y), "PARTIAL" (found Page X or X of Y),
                  "MISSING" (text exists but number not found), or "NO_TEXT".
        - match_detail: Substring/explanation of the match.
    """
    if not text or not text.strip():
        return "NO_TEXT", "No text layer found on this page"

    cleaned_text = " ".join(text.split())

    # 1. Look for exact match "Page X of Y" (case-insensitive, flexible spacing)
    exact_pattern = re.compile(rf"Page\s+{page_num}\s+of\s+{total_pages}", re.IGNORECASE)
    match = exact_pattern.search(cleaned_text)
    if match:
        return "OK", match.group(0)

    # 2. Look for common scanner OCR corruptions like "Page X o1 Y" or "Page X ot Y"
    corrupted_of_pattern = re.compile(rf"Page\s+{page_num}\s+(?:o1|ot|0f|of|o|f)\s+{total_pages}", re.IGNORECASE)
    match = corrupted_of_pattern.search(cleaned_text)
    if match:
        return "OK", f"{match.group(0)} (OCR typo corrected)"

    # 3. Look for partial match "Page X" (case-insensitive)
    partial_page_pattern = re.compile(rf"Page\s+{page_num}\b", re.IGNORECASE)
    match = partial_page_pattern.search(cleaned_text)
    if match:
        return "PARTIAL", f"{match.group(0)} (Missing 'of Y')"

    # 4. Look for partial match "X of Y" (flexible spacing)
    partial_of_pattern = re.compile(rf"\b{page_num}\s+of\s+{total_pages}\b", re.IGNORECASE)
    match = partial_of_pattern.search(cleaned_text)
    if match:
        return "PARTIAL", f"{match.group(0)} (Missing 'Page')"

    return "MISSING", "Page number not detected"


def main():
    parser = argparse.ArgumentParser(
        description="Verify page numbers on a scanned PDF using Tesseract OCR and pypdf."
    )
    parser.add_argument(
        "pdf_path",
        type=str,
        nargs="?",
        default="testpdf/ASDF_merged.pdf",
        help="Path to the PDF file to verify (default: testpdf/ASDF_merged.pdf)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="",
        help="Path to save the OCR'd PDF. If not specified, a temporary file is used.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["skip", "force", "redo"],
        default="skip",
        help=(
            "OCR mode: 'skip' (skip pages with existing text, fast for digital PDFs), "
            "'force' (rasterize all pages and run OCR, best for scanned PDFs), "
            "'redo' (redo OCR on text pages) (default: skip)"
        ),
    )

    args = parser.parse_args()
    input_path = Path(args.pdf_path)

    if not input_path.exists():
        print(f"[ERROR] Input PDF file does not exist: {input_path}")
        sys.exit(1)

    print(f"Loading input PDF: {input_path}")
    print(f"OCR Mode: {args.mode}")

    # Set up output path
    temp_file = None
    if args.output:
        output_path = Path(args.output)
    else:
        # Create a temporary file to hold the OCR'd PDF
        temp_dir = Path(tempfile.gettempdir())
        temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=temp_dir)
        output_path = Path(temp_file.name)
        temp_file.close()

    try:
        # Map mode to ocrmypdf arguments
        ocr_kwargs = {
            "skip_text": args.mode == "skip",
            "force_ocr": args.mode == "force",
            "redo_ocr": args.mode == "redo",
            "progress_bar": False,
        }

        print("Running OCR on PDF (this may take a few moments)...")
        # Run OCR
        exit_code = ocrmypdf.ocr(input_path, output_path, **ocr_kwargs)
        if exit_code != 0:
            print(f"[WARNING] ocrmypdf returned non-zero exit code: {exit_code}")

        # Open and read the OCR'd PDF
        print("Analyzing text layer...")
        reader = pypdf.PdfReader(output_path)
        total_pages = len(reader.pages)
        print(f"Total Pages: {total_pages}")
        print("-" * 75)
        print(f"{'Page':<6} | {'Status':<10} | {'Match Found / Explanation':<50}")
        print("-" * 75)

        stats = {"OK": 0, "PARTIAL": 0, "MISSING": 0, "NO_TEXT": 0}

        for i, page in enumerate(reader.pages):
            page_num = i + 1
            text = page.extract_text()
            status, detail = verify_page_text(text, page_num, total_pages)
            stats[status] += 1

            # Format the output using simple ASCII
            print(f"{page_num:<6} | {status:<10} | {detail:<50}")

        print("-" * 75)
        print("Summary:")
        print(f"  - Fully detected (Page X of Y): {stats['OK']}")
        print(f"  - Partially detected: {stats['PARTIAL']}")
        print(f"  - Missing page number: {stats['MISSING']}")
        print(f"  - Empty text layer: {stats['NO_TEXT']}")
        print("-" * 75)

        if stats["MISSING"] == 0 and stats["NO_TEXT"] == 0:
            print("[OK] All page numbers exist and were successfully verified!")
        else:
            print("[FAIL] Missing or unreadable page numbers/text on some pages.")
            if stats["NO_TEXT"] > 0:
                print("       Note: Pages with NO_TEXT may need to be scanned with OCR enabled,")
                print("             or run this script with --mode force to rasterize and OCR.")
            sys.exit(1)

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        # Help user debug path issues
        if "tesseract" in str(e).lower() or "program not found" in str(e).lower():
            print("\n[TIP] This error usually means Tesseract is not installed or not in your PATH.")
            print(f"      We checked: {TESSERACT_PATH} (exists: {os.path.exists(TESSERACT_PATH)})")
            print("      Ensure you have installed Tesseract OCR and restarted your terminal.")
        sys.exit(1)

    finally:
        # Clean up the temporary file if one was created
        if temp_file and output_path.exists():
            try:
                os.remove(output_path)
            except OSError:
                pass


if __name__ == "__main__":
    main()
