"""Dialog for collecting reason for duplicate operations."""

from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt
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

        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        self.setWindowTitle("Duplicate Operation Detected")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # ===== Warning Header =====
        warning_label = QLabel("⚠️ This operation has been performed before")
        warning_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #d97706; padding: 10px;"
        )
        warning_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning_label)

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

        details_label = QLabel(details_text)
        details_label.setWordWrap(True)
        details_label.setStyleSheet("padding: 10px; background-color: #f3f4f6; border-radius: 5px;")
        details_layout.addWidget(details_label)

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
        self.char_counter.setStyleSheet("color: #6b7280; font-size: 9pt;")
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
        self.continue_btn.setStyleSheet(
            "QPushButton:enabled { background-color: #2563eb; color: white; padding: 5px 15px; }"
            "QPushButton:disabled { background-color: #d1d5db; color: #6b7280; padding: 5px 15px; }"
        )

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.continue_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

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

        # Update button state and counter color
        if char_count >= self.MIN_REASON_LENGTH:
            self.continue_btn.setEnabled(True)
            self.char_counter.setStyleSheet("color: #10b981; font-size: 9pt; font-weight: bold;")
        else:
            self.continue_btn.setEnabled(False)
            if char_count > 0:
                self.char_counter.setStyleSheet("color: #dc2626; font-size: 9pt; font-weight: bold;")
            else:
                self.char_counter.setStyleSheet("color: #6b7280; font-size: 9pt;")

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
