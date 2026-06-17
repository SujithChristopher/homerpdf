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
        self, pdf_filename: str, hospital_number: str, center_code: str, time_point: str
    ) -> BytesIO:
        """
        Add hospital number overlay to a PDF.

        Args:
            pdf_filename: Name of the PDF file (e.g., "arat.pdf")
            hospital_number: Hospital number to add
            center_code: Center code (e.g., "CMC", "MNP", "LDH")
            time_point: Time point (e.g., "A0", "A1", "A2")

        Returns:
            BytesIO object containing modified PDF

        Raises:
            FileNotFoundError: If PDF file not found
            Exception: If PDF is corrupted or cannot be processed
        """
        pdf_path = self.pdf_dir / pdf_filename

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_filename}")

        # Format the overlay text with time point
        overlay_text = f"{time_point}-{center_code}-{hospital_number}"

        # Read the original PDF
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            writer = PdfWriter()

            # Check if PDF is encrypted
            if reader.is_encrypted:
                raise ValueError(f"Cannot process encrypted PDF: {pdf_filename}")

            # Process each page
            for page_num, page in enumerate(reader.pages):
                # Normalize page size to A4 if it isn't already
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                a4_width, a4_height = 595.27, 841.89
                
                if abs(page_width - a4_width) > 0.1 or abs(page_height - a4_height) > 0.1:
                    page.scale_to(a4_width, a4_height)
                    page_width = a4_width
                    page_height = a4_height

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
        self, pdf_filenames: list, hospital_number: str, center_code: str, time_point: str
    ) -> dict:
        """
        Process multiple PDFs with hospital number overlay.

        Args:
            pdf_filenames: List of PDF filenames
            hospital_number: Hospital number to add
            center_code: Center code
            time_point: Time point (e.g., "A0", "A1", "A2")

        Returns:
            Dictionary mapping filename to BytesIO (modified PDF)
            Entries with errors will have None as value
        """
        results = {}

        for filename in pdf_filenames:
            try:
                results[filename] = self.add_hospital_number(
                    filename, hospital_number, center_code, time_point
                )
            except Exception as e:
                # Store error information
                results[filename] = None
                print(f"Error processing {filename}: {str(e)}")

        return results

    def merge_pdfs(self, pdf_buffers: list, add_page_numbers: bool = True) -> BytesIO:
        """
        Merge multiple PDF buffers into a single PDF, optionally adding continuous page numbers.

        Args:
            pdf_buffers: List of BytesIO objects containing PDFs
            add_page_numbers: If True, adds "Page X of Y" at the bottom right of each page

        Returns:
            BytesIO object containing merged PDF
        """
        # First count total pages if adding page numbers
        total_pages = 0
        if add_page_numbers:
            for pdf_buffer in pdf_buffers:
                try:
                    pdf_buffer.seek(0)
                    reader = PdfReader(pdf_buffer)
                    total_pages += len(reader.pages)
                except Exception as e:
                    print(f"Error reading PDF page count: {str(e)}")

        merger = PdfWriter()
        current_page_idx = 0

        for pdf_buffer in pdf_buffers:
            try:
                pdf_buffer.seek(0)
                reader = PdfReader(pdf_buffer)
                for page in reader.pages:
                    # Normalize page size to A4 if it isn't already
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)
                    a4_width, a4_height = 595.27, 841.89
                    
                    if abs(page_width - a4_width) > 0.1 or abs(page_height - a4_height) > 0.1:
                        page.scale_to(a4_width, a4_height)
                        page_width = a4_width
                        page_height = a4_height
                    
                    if add_page_numbers and total_pages > 0:
                        current_page_idx += 1
                        
                        # Create page number overlay
                        overlay_buffer = OverlayCreator.create_page_number_overlay(
                            current_page_idx, total_pages, page_width, page_height
                        )
                        
                        # Merge overlay page onto original page
                        overlay_pdf = PdfReader(overlay_buffer)
                        overlay_page = overlay_pdf.pages[0]
                        page.merge_page(overlay_page)
                        
                    merger.add_page(page)
            except Exception as e:
                print(f"Error merging PDF page: {str(e)}")
                continue

        # Write merged PDF to buffer
        output_buffer = BytesIO()
        merger.write(output_buffer)
        output_buffer.seek(0)

        return output_buffer
