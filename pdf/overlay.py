"""Text overlay creation for PDFs using reportlab."""

from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class OverlayCreator:
    """Creates transparent PDF overlays with text at top-right (hospital number) and bottom-left (date/time)."""

    # Font settings
    FONT_NAME = "Helvetica"
    FONT_SIZE = 10

    # Positioning (in points)
    MARGIN_TOP = 20  # Distance from top edge
    MARGIN_RIGHT = 20  # Distance from right edge
    MARGIN_BOTTOM = 20  # Distance from bottom edge
    MARGIN_LEFT = 20  # Distance from left edge

    @staticmethod
    def create_text_overlay(
        text: str, page_width: float, page_height: float
    ) -> BytesIO:
        """
        Create a transparent PDF with text at top-right (hospital number) and bottom-left (date/time).

        Args:
            text: The text to display at top-right (e.g., "CMC-12345")
            page_width: Width of the page in points
            page_height: Height of the page in points

        Returns:
            BytesIO containing the overlay PDF with hospital number at top-right
            and current date/time at bottom-left
        """
        buffer = BytesIO()

        # Create canvas with transparent background
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

        # Calculate text position (top-right corner)
        # Canvas coordinates have origin at bottom-left, so we need to adjust
        text_width = c.stringWidth(text, OverlayCreator.FONT_NAME, OverlayCreator.FONT_SIZE)
        x = page_width - text_width - OverlayCreator.MARGIN_RIGHT
        y = page_height - OverlayCreator.MARGIN_TOP - OverlayCreator.FONT_SIZE

        # Draw the hospital number text (top-right)
        c.setFont(OverlayCreator.FONT_NAME, OverlayCreator.FONT_SIZE)
        c.drawString(x, y, text)

        # Add current date and time to bottom-left
        datetime_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        x_datetime = OverlayCreator.MARGIN_LEFT
        y_datetime = OverlayCreator.MARGIN_BOTTOM
        c.drawString(x_datetime, y_datetime, datetime_text)

        # Save the canvas
        c.save()

        # Get the PDF bytes
        buffer.seek(0)
        return buffer
