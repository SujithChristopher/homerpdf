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
        description=(
            "Run OCR on generated PDFs and verify that each page is numbered in "
            "physical order as 'Page X of Y'. A directory is scanned recursively."
        )
    )
    parser.add_argument(
        "pdf_paths",
        type=str,
        nargs="*",
        default=["testpdf/ASDF_merged.pdf"],
        help=(
            "PDF file(s) or directory(ies) to verify. Directories are scanned "
            "recursively (default: testpdf/ASDF_merged.pdf)."
        ),
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
    input_paths = []
    missing_paths = []
    for value in args.pdf_paths:
        path = Path(value)
        if path.is_dir():
            input_paths.extend(sorted(path.rglob("*.pdf")))
        elif path.is_file() and path.suffix.lower() == ".pdf":
            input_paths.append(path)
        else:
            missing_paths.append(path)

    input_paths = list(dict.fromkeys(path.resolve() for path in input_paths))
    if missing_paths:
        for path in missing_paths:
            print(f"[ERROR] Input PDF or directory does not exist: {path}")
    if not input_paths:
        print("[ERROR] No PDF files found to verify.")
        sys.exit(1)
    if args.output and len(input_paths) != 1:
        parser.error("--output can only be used when verifying exactly one PDF")

    ocr_kwargs = {
        "skip_text": args.mode == "skip",
        "force_ocr": args.mode == "force",
        "redo_ocr": args.mode == "redo",
        "progress_bar": False,
    }
    overall_failed = bool(missing_paths)
    for input_path in input_paths:
        output_path = Path(args.output) if args.output else None
        temp_file = None
        try:
            print(f"\nPDF: {input_path}")
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False, dir=Path(tempfile.gettempdir())
                )
                output_path = Path(temp_file.name)
                temp_file.close()

            print(f"Running OCR (mode: {args.mode})...")
            ocrmypdf.ocr(input_path, output_path, **ocr_kwargs)

            reader = pypdf.PdfReader(output_path)
            total_pages = len(reader.pages)
            print(f"Total pages: {total_pages}")
            print("-" * 75)
            print(f"{'Page':<6} | {'Status':<10} | {'Match Found / Explanation':<50}")
            print("-" * 75)

            stats = {"OK": 0, "PARTIAL": 0, "MISSING": 0, "NO_TEXT": 0}
            for i, page in enumerate(reader.pages):
                page_num = i + 1
                status, detail = verify_page_text(page.extract_text(), page_num, total_pages)
                stats[status] += 1
                print(f"{page_num:<6} | {status:<10} | {detail:<50}")

            print("-" * 75)
            print(
                f"Summary: {stats['OK']} OK, {stats['PARTIAL']} partial, "
                f"{stats['MISSING']} missing, {stats['NO_TEXT']} with no text"
            )
            pdf_failed = stats["PARTIAL"] + stats["MISSING"] + stats["NO_TEXT"] > 0
            if pdf_failed:
                overall_failed = True
                print("[FAIL] One or more page numbers could not be verified.")
            else:
                print("[OK] Page numbers match physical page order.")
        except Exception as e:
            overall_failed = True
            print(f"[ERROR] Failed to OCR or inspect PDF: {e}")
            if "tesseract" in str(e).lower() or "program not found" in str(e).lower():
                print("\n[TIP] This error usually means Tesseract is not installed or not in your PATH.")
                print(f"      We checked: {TESSERACT_PATH} (exists: {os.path.exists(TESSERACT_PATH)})")
                print("      Ensure you have installed Tesseract OCR and restarted your terminal.")
        finally:
            if temp_file and output_path and output_path.exists():
                output_path.unlink(missing_ok=True)

    if overall_failed:
        sys.exit(1)
    print(f"\n[OK] Verified {len(input_paths)} PDF(s).")


if __name__ == "__main__":
    main()
