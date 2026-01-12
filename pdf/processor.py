"""PDF processing and hospital number overlay functionality."""

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .overlay import OverlayCreator


class PDFProcessor:
    """Processes PDFs and adds hospital number overlay."""

    def __init__(self, pdf_dir: Path):
        """
        Initialize the PDF processor.

        Args:
            pdf_dir: Path to directory containing PDF files
        """
        self.pdf_dir = Path(pdf_dir)

    def add_hospital_number(
        self, pdf_filename: str, hospital_number: str, center_code: str
    ) -> BytesIO:
        """
        Add hospital number overlay to a PDF.

        Args:
            pdf_filename: Name of the PDF file (e.g., "arat.pdf")
            hospital_number: Hospital number to add
            center_code: Center code (e.g., "CMC", "MNP", "LDH")

        Returns:
            BytesIO object containing modified PDF

        Raises:
            FileNotFoundError: If PDF file not found
            Exception: If PDF is corrupted or cannot be processed
        """
        pdf_path = self.pdf_dir / pdf_filename

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_filename}")

        # Format the overlay text
        overlay_text = f"{center_code}-{hospital_number}"

        # Read the original PDF
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            writer = PdfWriter()

            # Check if PDF is encrypted
            if reader.is_encrypted:
                raise ValueError(f"Cannot process encrypted PDF: {pdf_filename}")

            # Process each page
            for page_num, page in enumerate(reader.pages):
                # Get page dimensions
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)

                # Create overlay PDF
                overlay_buffer = OverlayCreator.create_text_overlay(
                    overlay_text, page_width, page_height
                )

                # Read overlay as PDF
                overlay_pdf = PdfReader(overlay_buffer)
                overlay_page = overlay_pdf.pages[0]

                # Merge overlay onto original page
                page.merge_page(overlay_page)

                # Add modified page to writer
                writer.add_page(page)

        # Write to BytesIO buffer
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        return output_buffer

    def process_multiple(
        self, pdf_filenames: list, hospital_number: str, center_code: str
    ) -> dict:
        """
        Process multiple PDFs with hospital number overlay.

        Args:
            pdf_filenames: List of PDF filenames
            hospital_number: Hospital number to add
            center_code: Center code

        Returns:
            Dictionary mapping filename to BytesIO (modified PDF)
            Entries with errors will have None as value
        """
        results = {}

        for filename in pdf_filenames:
            try:
                results[filename] = self.add_hospital_number(
                    filename, hospital_number, center_code
                )
            except Exception as e:
                # Store error information
                results[filename] = None
                print(f"Error processing {filename}: {str(e)}")

        return results

    def merge_pdfs(self, pdf_buffers: list) -> BytesIO:
        """
        Merge multiple PDF buffers into a single PDF.

        Args:
            pdf_buffers: List of BytesIO objects containing PDFs

        Returns:
            BytesIO object containing merged PDF
        """
        merger = PdfWriter()

        for pdf_buffer in pdf_buffers:
            try:
                pdf_buffer.seek(0)
                reader = PdfReader(pdf_buffer)
                for page in reader.pages:
                    merger.add_page(page)
            except Exception as e:
                print(f"Error merging PDF: {str(e)}")
                continue

        # Write merged PDF to buffer
        output_buffer = BytesIO()
        merger.write(output_buffer)
        output_buffer.seek(0)

        return output_buffer
