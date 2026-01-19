"""Dialog for collecting reason for duplicate operations."""

from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTextEdit,
    QPushButton,
    QGroupBox,
    QDialogButtonBox,
)


class ReprintReasonDialog(QDialog):
    """Dialog for collecting reason for duplicate operation."""

    MIN_REASON_LENGTH = 10
    MAX_REASON_LENGTH = 500

    PRESET_REASONS = [
        "Lost original file",
        "Damaged/corrupted print",
        "Administrative correction required",
        "Patient record update",
        "File sent to wrong recipient",
        "Quality issue with previous print",
        "Other (please specify)",
    ]

    def __init__(self, parent, operation_type: str, previous_operation: dict):
        """
        Initialize dialog with previous operation details.

        Args:
            parent: Parent widget
            operation_type: Type of operation (download/print)
            previous_operation: Dict with previous operation details
        """
        super().__init__(parent)

        self.operation_type = operation_type
        self.previous_operation = previous_operation
        self.reason = None

        # Get theme colors
        self.palette = self.palette()
        self.is_dark = self.palette.color(QPalette.Window).lightness() < 128

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle("Duplicate Operation Detected")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # ===== Warning Header =====
        self.warning_label = QLabel("⚠️ This operation has been performed before")
        self.warning_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.warning_label)

        # ===== Previous Operation Details =====
        details_group = QGroupBox("Previous Operation Details")
        details_layout = QVBoxLayout()

        # Parse timestamp
        try:
            dt = datetime.fromisoformat(self.previous_operation["timestamp"])
            timestamp_str = dt.strftime("%Y-%m-%d %I:%M:%S %p")
        except Exception:
            timestamp_str = self.previous_operation["timestamp"]

        # Create details text
        details_text = f"""
<b>Date:</b> {timestamp_str}<br>
<b>Operation:</b> {self.previous_operation['operation_type'].title()}<br>
<b>Time Point:</b> {self.previous_operation['time_point']}<br>
<b>Center:</b> {self.previous_operation['center_code']}<br>
<b>Hospital Number:</b> {self.previous_operation['hospital_number']}<br>
<b>PDF Files:</b> {', '.join(self.previous_operation['pdf_files'])}<br>
<b>Merged:</b> {'Yes' if self.previous_operation['merge_flag'] else 'No'}<br>
"""

        if self.previous_operation.get("username"):
            details_text += f"<b>User:</b> {self.previous_operation['username']}<br>"

        self.details_label = QLabel(details_text)
        self.details_label.setWordWrap(True)
        details_layout.addWidget(self.details_label)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # ===== Reason Input =====
        reason_group = QGroupBox("Reason for Duplicate Operation (Required)")
        reason_layout = QVBoxLayout()

        # Preset reasons dropdown
        preset_label = QLabel("Select a reason:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- Select a preset reason --")
        for reason in self.PRESET_REASONS:
            self.preset_combo.addItem(reason)
        self.preset_combo.currentIndexChanged.connect(self.on_preset_selected)

        reason_layout.addWidget(preset_label)
        reason_layout.addWidget(self.preset_combo)

        # Additional details text input
        details_label = QLabel("Additional details (required, 10-500 characters):")
        self.reason_text = QTextEdit()
        self.reason_text.setPlaceholderText(
            "Please provide a detailed reason for performing this operation again..."
        )
        self.reason_text.setMaximumHeight(120)
        self.reason_text.textChanged.connect(self.on_text_changed)

        reason_layout.addWidget(details_label)
        reason_layout.addWidget(self.reason_text)

        # Character counter
        self.char_counter = QLabel("0 / 500 characters (minimum 10 required)")
        reason_layout.addWidget(self.char_counter)

        reason_group.setLayout(reason_layout)
        layout.addWidget(reason_group)

        # ===== Buttons =====
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        self.continue_btn = QPushButton(f"Continue with {self.operation_type.title()}")
        self.continue_btn.clicked.connect(self.accept_with_validation)
        self.continue_btn.setEnabled(False)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.continue_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def apply_theme(self):
        """Apply theme-aware styling to dialog components."""
        # Get system palette colors
        palette = self.palette
        is_dark = self.is_dark

        # Define colors based on theme
        if is_dark:
            warning_color = "#fbbf24"  # Brighter yellow for dark mode
            details_bg = palette.color(QPalette.Window).lighter(120).name()
            text_color = palette.color(QPalette.Text).name()
            border_color = palette.color(QPalette.Mid).name()
            button_primary = palette.color(QPalette.Highlight).name()
            button_primary_text = palette.color(QPalette.HighlightedText).name()
            success_color = "#10b981"
            error_color = "#ef4444"
            muted_color = palette.color(QPalette.Mid).name()
        else:
            warning_color = "#d97706"  # Orange for light mode
            details_bg = palette.color(QPalette.Window).darker(105).name()
            text_color = palette.color(QPalette.Text).name()
            border_color = palette.color(QPalette.Mid).name()
            button_primary = palette.color(QPalette.Highlight).name()
            button_primary_text = palette.color(QPalette.HighlightedText).name()
            success_color = "#059669"
            error_color = "#dc2626"
            muted_color = "#6b7280"

        # Store colors for dynamic updates
        self.success_color = success_color
        self.error_color = error_color
        self.muted_color = muted_color

        # Apply styles
        self.warning_label.setStyleSheet(
            f"font-size: 14pt; font-weight: bold; color: {warning_color}; padding: 10px;"
        )

        self.details_label.setStyleSheet(
            f"padding: 10px; background-color: {details_bg}; border-radius: 5px; color: {text_color};"
        )

        # Apply global dialog stylesheet
        stylesheet = f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {border_color};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: {text_color};
            }}

            QComboBox {{
                padding: 6px;
                border: 1px solid {border_color};
                border-radius: 4px;
                color: {text_color};
            }}

            QTextEdit {{
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 6px;
                color: {text_color};
            }}

            QTextEdit:focus {{
                border: 2px solid {button_primary};
            }}

            QPushButton {{
                padding: 8px 16px;
                border: 1px solid {border_color};
                border-radius: 4px;
                font-weight: bold;
                color: {text_color};
            }}

            QPushButton:hover:!disabled {{
                border: 2px solid {button_primary};
            }}

            QLabel {{
                color: {text_color};
            }}
        """

        # Style continue button specially
        continue_btn_style = f"""
            QPushButton {{
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}

            QPushButton:enabled {{
                background-color: {button_primary};
                color: {button_primary_text};
                border: none;
            }}

            QPushButton:enabled:hover {{
                background-color: {palette.color(QPalette.Highlight).lighter(110).name()};
            }}

            QPushButton:disabled {{
                background-color: {palette.color(QPalette.Window).name()};
                color: {muted_color};
                border: 1px solid {border_color};
            }}
        """

        self.setStyleSheet(stylesheet)
        self.continue_btn.setStyleSheet(continue_btn_style)

        # Update char counter with default color
        self.char_counter.setStyleSheet(f"color: {muted_color}; font-size: 9pt;")

    def on_preset_selected(self, index: int):
        """Handle preset reason selection."""
        if index > 0:  # Not the placeholder item
            preset_reason = self.preset_combo.currentText()
            # If "Other" is selected, just clear the text
            if preset_reason != "Other (please specify)":
                # Prepend preset reason to text
                current_text = self.reason_text.toPlainText()
                if not current_text.startswith(preset_reason):
                    self.reason_text.setPlainText(preset_reason)

    def on_text_changed(self):
        """Handle text changes and update character counter."""
        text = self.reason_text.toPlainText().strip()
        char_count = len(text)

        # Update counter
        self.char_counter.setText(f"{char_count} / {self.MAX_REASON_LENGTH} characters (minimum {self.MIN_REASON_LENGTH} required)")

        # Enforce max length
        if char_count > self.MAX_REASON_LENGTH:
            # Truncate text
            cursor = self.reason_text.textCursor()
            cursor_pos = cursor.position()
            self.reason_text.setPlainText(text[:self.MAX_REASON_LENGTH])
            cursor.setPosition(min(cursor_pos, self.MAX_REASON_LENGTH))
            self.reason_text.setTextCursor(cursor)
            return

        # Update button state and counter color (using theme-aware colors)
        if char_count >= self.MIN_REASON_LENGTH:
            self.continue_btn.setEnabled(True)
            self.char_counter.setStyleSheet(f"color: {self.success_color}; font-size: 9pt; font-weight: bold;")
        else:
            self.continue_btn.setEnabled(False)
            if char_count > 0:
                self.char_counter.setStyleSheet(f"color: {self.error_color}; font-size: 9pt; font-weight: bold;")
            else:
                self.char_counter.setStyleSheet(f"color: {self.muted_color}; font-size: 9pt;")

    def accept_with_validation(self):
        """Validate and accept the dialog."""
        text = self.reason_text.toPlainText().strip()

        if len(text) < self.MIN_REASON_LENGTH:
            # This shouldn't happen due to button state, but extra validation
            return

        if len(text) > self.MAX_REASON_LENGTH:
            return

        # Store the reason
        self.reason = text

        # Accept dialog
        self.accept()

    def get_reason(self) -> Optional[str]:
        """
        Show dialog and return reason or None if cancelled.

        Returns:
            Reason string if accepted, None if cancelled
        """
        result = self.exec()

        if result == QDialog.Accepted:
            return self.reason

        return None
