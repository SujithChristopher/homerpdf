"""Text overlay creation for PDFs using reportlab."""

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class OverlayCreator:
    """Creates transparent PDF overlays with text positioned at top-right corner."""

    # Font settings
    FONT_NAME = "Helvetica"
    FONT_SIZE = 10

    # Positioning (in points)
    MARGIN_TOP = 20  # Distance from top edge
    MARGIN_RIGHT = 20  # Distance from right edge

    @staticmethod
    def create_text_overlay(
        text: str, page_width: float, page_height: float
    ) -> BytesIO:
        """
        Create a transparent PDF with text positioned at top-right corner.

        Args:
            text: The text to display (e.g., "CMC-12345")
            page_width: Width of the page in points
            page_height: Height of the page in points

        Returns:
            BytesIO containing the overlay PDF
        """
        buffer = BytesIO()

        # Create canvas with transparent background
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

        # Calculate text position (top-right corner)
        # Canvas coordinates have origin at bottom-left, so we need to adjust
        text_width = c.stringWidth(text, OverlayCreator.FONT_NAME, OverlayCreator.FONT_SIZE)
        x = page_width - text_width - OverlayCreator.MARGIN_RIGHT
        y = page_height - OverlayCreator.MARGIN_TOP - OverlayCreator.FONT_SIZE

        # Draw the text
        c.setFont(OverlayCreator.FONT_NAME, OverlayCreator.FONT_SIZE)
        c.drawString(x, y, text)

        # Save the canvas
        c.save()

        # Get the PDF bytes
        buffer.seek(0)
        return buffer
