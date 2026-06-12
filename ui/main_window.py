"""Main application window for Hospital PDF Manager."""

import os
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, QTimer, QItemSelectionModel
from PySide6.QtGui import QDesktopServices, QColor, QPalette
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QProgressDialog,
    QRadioButton,
    QButtonGroup,
)

from pdf.processor import PDFProcessor
from utils.validators import validate_hospital_number
import csv
from utils.paths import get_files_dir, get_base_dir
from utils.operation_logger import OperationLogger


class ReadOnlyListWidget(QListWidget):
    """A QListWidget that prevents user selection updates but allows programmatic selection."""
    def selectionCommand(self, index, event=None):
        return QItemSelectionModel.NoUpdate


class MainWindow(QMainWindow):
    """Main application window for Hospital PDF Manager."""

    # Center mapping
    CENTERS = [
        ("CMC", "CMC Vellore"),
        ("MNP", "Manipal Hospital"),
        ("LDH", "Ludhiana Hospital"),
    ]

    # Mapping of REDCap form names to PDF file names
    FORM_TO_PDF = {
        "homer_screening_form": "00 HOMER- SCREENING FORM.pdf",
        "fugl_meyer_assessment_ue": "01 fma-ue.pdf",
        "montreal_cognitive_assessment": "06 moca.pdf",
        "modified_ashworth_scale": "08. Modified Ashworth Scale Instructions.pdf",
        "action_research_arm_test": "02 arat.pdf",
        "motor_activity_log": "03 Motor Activity Log.pdf",
        "cahai7_score_form": "04 CAHAI-7.pdf",
        "sipso_questionnaire": "05 SIPSO.pdf",
        "modified_rankin_scale": "07 modrankinscale.pdf",
        "caregiver_strain_index": "09 csi.pdf",
        "patient_health_questionnaire_phq9": "10 phq9.pdf",
        "nih_stroke_scale": "12 NIHSS.pdf",
        "box_and_block_test": "13 Box and Block.pdf",
        "eq_5d_5l": "14 EQ-5D-5L.pdf",
    }

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Hospital PDF Manager")
        self.setFixedSize(550, 650)

        # Initialize PDF processor with correct path (works in dev and packaged)
        self.pdf_dir = get_files_dir()
        self.processor = PDFProcessor(self.pdf_dir)

        # Initialize operation logger
        log_dir = Path(os.getenv("LOCALAPPDATA")) / "HospitalPDFManager"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.operation_logger = OperationLogger(log_dir / "operations.db")

        # Load event mappings from events.csv
        self.load_events()

        # Setup UI
        self.setup_ui()

        # Apply theme-aware styling
        self.apply_theme()

        # Center the window on screen
        self.center_window()

    def center_window(self):
        """Center the window on the screen."""
        from PySide6.QtGui import QScreen

        screen = self.screen()
        screen_geometry = screen.geometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def load_events(self):
        """Load events from events.csv and map them to PDF files."""
        self.event_pdfs = {
            "screening": set(),
            "a0": set(),
            "a1": set(),
            "a2": set()
        }
        
        events_csv_path = get_base_dir() / "redcap" / "example" / "events.csv"
        if not events_csv_path.exists():
            # Fallback if events.csv not found
            print(f"events.csv not found at {events_csv_path}")
            # Populate default mappings based on standard events.csv
            screening_forms = ["homer_screening_form", "fugl_meyer_assessment_ue", "montreal_cognitive_assessment", "modified_ashworth_scale", "numeric_pain_rating_scale"]
            a_forms = [
                "patient_demographics", "fugl_meyer_assessment_ue", "sipso_questionnaire",
                "action_research_arm_test", "caregiver_strain_index", "motor_activity_log",
                "modified_rankin_scale", "patient_health_questionnaire_phq9", "modified_ashworth_scale",
                "box_and_block_test", "cahai7_score_form", "nih_stroke_scale", "eq_5d_5l",
                "completed_assessment"
            ]
            for form in screening_forms:
                pdf = self.FORM_TO_PDF.get(form)
                if pdf:
                    self.event_pdfs["screening"].add(pdf)
            for tp in ["a0", "a1", "a2"]:
                for form in a_forms:
                    pdf = self.FORM_TO_PDF.get(form)
                    if pdf:
                        self.event_pdfs[tp].add(pdf)
            return

        try:
            with open(events_csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    event_name = row.get("unique_event_name", "").lower()
                    form = row.get("form", "")
                    pdf = self.FORM_TO_PDF.get(form)
                    if not pdf:
                        continue
                    
                    if "screening" in event_name:
                        self.event_pdfs["screening"].add(pdf)
                    elif "a0" in event_name:
                        self.event_pdfs["a0"].add(pdf)
                    elif "a1" in event_name:
                        self.event_pdfs["a1"].add(pdf)
                    elif "a2" in event_name:
                        self.event_pdfs["a2"].add(pdf)
        except Exception as e:
            print(f"Error loading events.csv: {e}")

    def apply_theme(self):
        """Apply theme-aware styling that works in both light and dark mode."""
        # Get system palette colors
        palette = self.palette()
        is_dark = palette.color(QPalette.Window).lightness() < 128

        # Define colors based on theme
        if is_dark:
            # Dark mode colors
            group_bg = palette.color(QPalette.Window).lighter(110).name()
            input_bg = palette.color(QPalette.Base).name()
            text_color = palette.color(QPalette.Text).name()
            border_color = palette.color(QPalette.Mid).name()
            button_bg = palette.color(QPalette.Button).name()
            button_hover = palette.color(QPalette.Button).lighter(120).name()
            button_disabled_bg = palette.color(QPalette.Window).name()
            button_disabled_text = palette.color(QPalette.Mid).name()
        else:
            # Light mode colors
            group_bg = palette.color(QPalette.Window).darker(105).name()
            input_bg = palette.color(QPalette.Base).name()
            text_color = palette.color(QPalette.Text).name()
            border_color = palette.color(QPalette.Mid).name()
            button_bg = palette.color(QPalette.Button).name()
            button_hover = palette.color(QPalette.Button).darker(110).name()
            button_disabled_bg = palette.color(QPalette.Window).name()
            button_disabled_text = palette.color(QPalette.Mid).name()

        # Apply comprehensive stylesheet
        stylesheet = f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {border_color};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: {group_bg};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: {text_color};
            }}

            QLineEdit {{
                padding: 6px;
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {input_bg};
                color: {text_color};
            }}

            QLineEdit:focus {{
                border: 2px solid {palette.color(QPalette.Highlight).name()};
                padding: 5px;
            }}

            QComboBox {{
                padding: 6px;
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {input_bg};
                color: {text_color};
            }}

            QComboBox:focus {{
                border: 2px solid {palette.color(QPalette.Highlight).name()};
            }}

            QComboBox::drop-down {{
                border: none;
                padding-right: 5px;
            }}

            QListWidget {{
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px;
                background-color: {input_bg};
                color: {text_color};
            }}

            QListWidget::item {{
                padding: 4px;
                border-radius: 3px;
            }}

            QListWidget::item:hover {{
                background-color: {palette.color(QPalette.Highlight).lighter(150).name()};
            }}

            QListWidget::item:selected {{
                background-color: {palette.color(QPalette.Highlight).name()};
                color: {palette.color(QPalette.HighlightedText).name()};
                font-weight: bold;
            }}

            QPushButton {{
                padding: 8px 16px;
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {button_bg};
                color: {text_color};
                font-weight: bold;
            }}

            QPushButton:hover:!disabled {{
                background-color: {button_hover};
                border: 2px solid {palette.color(QPalette.Highlight).name()};
            }}

            QPushButton:pressed {{
                background-color: {palette.color(QPalette.Highlight).name()};
            }}

            QPushButton:disabled {{
                background-color: {button_disabled_bg};
                color: {button_disabled_text};
                border: 1px solid {border_color};
            }}

            QCheckBox {{
                spacing: 8px;
                color: {text_color};
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {border_color};
                border-radius: 3px;
                background-color: {input_bg};
            }}

            QCheckBox::indicator:checked {{
                background-color: {palette.color(QPalette.Highlight).name()};
                border: 1px solid {palette.color(QPalette.Highlight).name()};
            }}

            QRadioButton {{
                spacing: 8px;
                color: {text_color};
            }}

            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {border_color};
                border-radius: 9px;
                background-color: {input_bg};
            }}

            QRadioButton::indicator:checked {{
                background-color: {palette.color(QPalette.Highlight).name()};
                border: 3px solid {input_bg};
            }}

            QLabel {{
                color: {text_color};
            }}

            QStatusBar {{
                color: {text_color};
                border-top: 1px solid {border_color};
            }}
        """

        self.setStyleSheet(stylesheet)

    def setup_ui(self):
        """Setup the UI components and layout."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # ===== Patient Information Group =====
        info_group = QGroupBox("Patient Information")
        info_layout = QVBoxLayout()

        # Hospital Number
        hospital_layout = QHBoxLayout()
        hospital_label = QLabel("Hospital Number:")
        hospital_label.setMinimumWidth(120)
        self.hospital_input = QLineEdit()
        self.hospital_input.setPlaceholderText("Enter hospital number...")
        self.hospital_input.textChanged.connect(self.on_input_changed)
        hospital_layout.addWidget(hospital_label)
        hospital_layout.addWidget(self.hospital_input)

        # Center Selection
        center_layout = QHBoxLayout()
        center_label = QLabel("Center:")
        center_label.setMinimumWidth(120)
        self.center_combo = QComboBox()
        for code, display_name in self.CENTERS:
            self.center_combo.addItem(display_name, userData=code)
        self.center_combo.currentIndexChanged.connect(self.on_input_changed)
        center_layout.addWidget(center_label)
        center_layout.addWidget(self.center_combo)
        center_layout.addStretch()

        # Time Point Selection (Radio Buttons)
        timepoint_layout = QHBoxLayout()
        timepoint_label = QLabel("Time Point:")
        timepoint_label.setMinimumWidth(120)

        # Create button group for radio buttons (ensures only one can be selected)
        self.timepoint_group = QButtonGroup()

        # Create radio buttons
        self.radio_screening = QRadioButton("Screening")
        self.timepoint_group.addButton(self.radio_screening)

        timepoint_layout.addWidget(timepoint_label)
        timepoint_layout.addWidget(self.radio_screening)
        timepoint_layout.addStretch()

        # Other Time Points Row
        other_timepoints_layout = QHBoxLayout()
        other_timepoints_label = QLabel("Other Time Points:")
        other_timepoints_label.setMinimumWidth(120)

        self.radio_a0 = QRadioButton("A0")
        self.radio_a1 = QRadioButton("A1")
        self.radio_a2 = QRadioButton("A2")

        self.timepoint_group.addButton(self.radio_a0)
        self.timepoint_group.addButton(self.radio_a1)
        self.timepoint_group.addButton(self.radio_a2)

        # Connect to validation and PDF highlighting updates
        self.radio_screening.toggled.connect(self.on_timepoint_changed)
        self.radio_a0.toggled.connect(self.on_timepoint_changed)
        self.radio_a1.toggled.connect(self.on_timepoint_changed)
        self.radio_a2.toggled.connect(self.on_timepoint_changed)

        # Add to layout
        other_timepoints_layout.addWidget(other_timepoints_label)
        other_timepoints_layout.addWidget(self.radio_a0)
        other_timepoints_layout.addWidget(self.radio_a1)
        other_timepoints_layout.addWidget(self.radio_a2)
        other_timepoints_layout.addStretch()

        info_layout.addLayout(hospital_layout)
        info_layout.addLayout(center_layout)
        info_layout.addLayout(timepoint_layout)
        info_layout.addLayout(other_timepoints_layout)
        info_group.setLayout(info_layout)

        # ===== PDF Information Group =====
        pdf_group = QGroupBox("Included Files")
        pdf_layout = QVBoxLayout()

        # Dynamic checkable PDF list (read-only to user clicks)
        self.pdf_list = ReadOnlyListWidget()
        self.pdf_list.setSelectionMode(QListWidget.MultiSelection)
        self.pdf_list.itemSelectionChanged.connect(self.on_input_changed)

        # Populate the QListWidget with all available PDFs (including 06 moca.pdf)
        pdf_files = sorted([f for f in self.pdf_dir.glob("*.pdf")])
        for pdf_file in pdf_files:
            item = QListWidgetItem(pdf_file.stem.upper())
            item.setData(Qt.UserRole, pdf_file.name)
            self.pdf_list.addItem(item)
        
        pdf_layout.addWidget(self.pdf_list)
        pdf_group.setLayout(pdf_layout)

        # ===== Action Buttons =====
        button_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.clicked.connect(self.on_download_clicked)
        self.download_btn.setEnabled(False)

        self.print_btn = QPushButton("Print Selected")
        self.print_btn.clicked.connect(self.on_print_clicked)
        self.print_btn.setEnabled(False)

        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.print_btn)

        # ===== Assemble main layout =====
        main_layout.addWidget(info_group)
        main_layout.addWidget(pdf_group)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        # Setup status bar
        self.statusBar().showMessage("Ready")

    def validate_inputs(self) -> bool:
        """
        Validate hospital number and time point selection.

        Returns:
            True if validation passes, False otherwise
        """
        # Validate hospital number
        hospital_number = self.hospital_input.text().strip()
        is_valid, error_msg = validate_hospital_number(hospital_number)

        if not is_valid:
            self.set_input_invalid(True)
            return False

        # Validate time point selection (mandatory)
        time_point = self.get_selected_timepoint()
        if not time_point:
            return False

        # Validate that at least one PDF is selected
        selected_pdfs = self.get_selected_pdfs()
        if not selected_pdfs:
            return False

        self.set_input_invalid(False)
        return True

    def set_input_invalid(self, is_invalid: bool):
        """
        Set visual feedback for invalid input.

        Args:
            is_invalid: True if input is invalid
        """
        if is_invalid:
            # Get theme-aware error color
            palette = self.palette()
            is_dark = palette.color(QPalette.Window).lightness() < 128

            # Use a bright red that works in both modes
            error_color = "#ff5555" if is_dark else "#dc3545"
            bg_color = palette.color(QPalette.Base).name()
            text_color = palette.color(QPalette.Text).name()

            # Add red border to input field with theme-aware colors
            self.hospital_input.setStyleSheet(
                f"""
                QLineEdit {{
                    border: 2px solid {error_color};
                    border-radius: 4px;
                    padding: 5px;
                    background-color: {bg_color};
                    color: {text_color};
                }}
                """
            )
        else:
            # Reset to default styling (empty string lets main stylesheet take over)
            self.hospital_input.setStyleSheet("")

    def on_input_changed(self):
        """Handle changes to hospital number or center selection."""
        self.update_button_states()



    def update_button_states(self):
        """Update button enabled/disabled states based on validation."""
        is_valid = self.validate_inputs()
        self.download_btn.setEnabled(is_valid)
        self.print_btn.setEnabled(is_valid)

        # Update input styling
        hospital_number = self.hospital_input.text().strip()
        if hospital_number:
            is_valid_number, _ = validate_hospital_number(hospital_number)
            self.set_input_invalid(not is_valid_number)
        else:
            self.set_input_invalid(False)

    def get_selected_pdfs(self) -> list:
        """
        Get list of selected PDF filenames from the QListWidget.

        Returns:
            List of selected PDF filenames
        """
        selected_items = self.pdf_list.selectedItems()
        return [item.data(Qt.UserRole) for item in selected_items]

    def get_selected_timepoint(self) -> str:
        """
        Get the selected time point (Screening, A0, A1, or A2).

        Returns:
            Selected time point string or empty string if none selected
        """
        if self.radio_screening.isChecked():
            return "Screening"
        elif self.radio_a0.isChecked():
            return "A0"
        elif self.radio_a1.isChecked():
            return "A1"
        elif self.radio_a2.isChecked():
            return "A2"
        return ""

    def on_timepoint_changed(self):
        """Handle timepoint selection changes by updating highlighting."""
        self.update_pdf_selection()
        self.on_input_changed()

    def update_pdf_selection(self):
        """Update the selected PDFs in the QListWidget based on selected timepoint."""
        timepoint = self.get_selected_timepoint().lower()
        if not timepoint:
            self.pdf_list.clearSelection()
            return
            
        # Get target PDFs for the selected timepoint
        target_pdfs = self.event_pdfs.get(timepoint, set())
        
        # Block signals temporarily to prevent redundant validation calls during selection loop
        self.pdf_list.blockSignals(True)
        for i in range(self.pdf_list.count()):
            item = self.pdf_list.item(i)
            filename = item.data(Qt.UserRole)
            if filename in target_pdfs:
                item.setSelected(True)
            else:
                item.setSelected(False)
        self.pdf_list.blockSignals(False)
        
        # Trigger single validation update
        self.on_input_changed()

    def on_download_clicked(self):
        """Handle download button click."""
        # Get save directory from user
        save_dir = QFileDialog.getExistingDirectory(
            self, "Select Download Location", str(Path.home())
        )

        if not save_dir:
            return  # User cancelled

        save_dir = Path(save_dir)

        # Get inputs
        hospital_number = self.hospital_input.text().strip()
        center_code = self.center_combo.currentData()
        time_point = self.get_selected_timepoint()
        selected_pdfs = self.get_selected_pdfs()
        merge_pdfs = True

        if not selected_pdfs:
            QMessageBox.warning(self, "No Selection", "Please select at least one PDF")
            return

        # Check for duplicate operation
        duplicate_info = self.operation_logger.check_duplicate(
            time_point, center_code, hospital_number, selected_pdfs, "download", merge_pdfs
        )

        reprint_reason = None
        if duplicate_info:
            # Show reason dialog
            from ui.reprint_dialog import ReprintReasonDialog

            dialog = ReprintReasonDialog(self, "download", duplicate_info)
            reprint_reason = dialog.get_reason()

            if reprint_reason is None:
                # User cancelled
                self.statusBar().showMessage("Download cancelled by user")
                return

        # Create progress dialog
        progress = QProgressDialog(
            "Downloading PDFs...", None, 0, len(selected_pdfs), self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(False)
        progress.show()

        # Process each PDF
        successful = 0
        failed = 0
        errors = []
        processed_pdfs = []

        for idx, pdf_filename in enumerate(selected_pdfs):
            progress.setValue(idx)
            QApplication.processEvents()  # Update UI

            try:
                # Process PDF
                modified_pdf = self.processor.add_hospital_number(
                    pdf_filename, hospital_number, center_code, time_point
                )
                processed_pdfs.append((pdf_filename, modified_pdf))
                successful += 1

            except FileNotFoundError as e:
                failed += 1
                errors.append(f"{pdf_filename}: File not found")
            except ValueError as e:
                failed += 1
                errors.append(f"{pdf_filename}: {str(e)}")
            except Exception as e:
                failed += 1
                errors.append(f"{pdf_filename}: {str(e)}")

        progress.close()

        # Save PDFs
        if merge_pdfs and len(processed_pdfs) > 0:
            # Merge all PDFs into one
            try:
                pdf_buffers = [pdf for _, pdf in processed_pdfs]
                merged_pdf = self.processor.merge_pdfs(pdf_buffers)

                # Create output filename
                output_filename = f"{hospital_number}_merged.pdf"
                output_path = save_dir / output_filename

                # Save to file
                with open(output_path, "wb") as f:
                    f.write(merged_pdf.getvalue())

                message = f"Downloaded merged PDF to:\n{save_dir}\n\nFile: {output_filename}"
                QMessageBox.information(self, "Success", message)
                self.statusBar().showMessage(f"Downloaded merged PDF")

                # Log operation
                self.operation_logger.log_operation(
                    time_point,
                    center_code,
                    hospital_number,
                    selected_pdfs,
                    "download",
                    merge_pdfs,
                    is_duplicate=(duplicate_info is not None),
                    reprint_reason=reprint_reason,
                    output_path=str(save_dir),
                )

            except Exception as e:
                error_msg = f"Failed to merge and save PDFs: {str(e)}"
                QMessageBox.critical(self, "Merge Failed", error_msg)
                self.statusBar().showMessage("Merge failed")
        else:
            # Save individual PDFs
            for pdf_filename, modified_pdf in processed_pdfs:
                try:
                    # Create output filename
                    output_filename = f"{hospital_number}_{Path(pdf_filename).stem}.pdf"
                    output_path = save_dir / output_filename

                    # Save to file
                    with open(output_path, "wb") as f:
                        f.write(modified_pdf.getvalue())

                except PermissionError:
                    failed += 1
                    errors.append(f"{output_filename}: Permission denied (check folder permissions)")
                except Exception as e:
                    failed += 1
                    errors.append(f"{pdf_filename}: {str(e)}")

            # Show results
            if successful > 0:
                message = f"Downloaded {successful} PDF(s) to:\n{save_dir}"
                if failed > 0:
                    message += f"\n\nFailed: {failed} PDF(s)"
                    for error in errors:
                        message += f"\n  • {error}"
                    QMessageBox.warning(self, "Partial Success", message)
                else:
                    QMessageBox.information(self, "Success", message)

                # Log operation (only log if at least one PDF was successful)
                self.operation_logger.log_operation(
                    time_point,
                    center_code,
                    hospital_number,
                    selected_pdfs,
                    "download",
                    merge_pdfs,
                    is_duplicate=(duplicate_info is not None),
                    reprint_reason=reprint_reason,
                    output_path=str(save_dir),
                )
            else:
                error_msg = "Failed to download PDFs:\n"
                for error in errors:
                    error_msg += f"  • {error}\n"
                QMessageBox.critical(self, "Download Failed", error_msg)

            self.statusBar().showMessage(f"Downloaded {successful} PDF(s)")

    def on_print_clicked(self):
        """Handle print button click."""
        # Get inputs
        hospital_number = self.hospital_input.text().strip()
        center_code = self.center_combo.currentData()
        time_point = self.get_selected_timepoint()
        selected_pdfs = self.get_selected_pdfs()
        merge_pdfs = True

        if not selected_pdfs:
            QMessageBox.warning(self, "No Selection", "Please select at least one PDF")
            return

        # Check for duplicate operation
        duplicate_info = self.operation_logger.check_duplicate(
            time_point, center_code, hospital_number, selected_pdfs, "print", merge_pdfs
        )

        reprint_reason = None
        if duplicate_info:
            # Show reason dialog
            from ui.reprint_dialog import ReprintReasonDialog

            dialog = ReprintReasonDialog(self, "print", duplicate_info)
            reprint_reason = dialog.get_reason()

            if reprint_reason is None:
                # User cancelled
                self.statusBar().showMessage("Print cancelled by user")
                return

        # Create temp directory
        try:
            temp_dir = Path(tempfile.gettempdir()) / "homerpdf_print"
            temp_dir.mkdir(exist_ok=True)
        except Exception as e:
            QMessageBox.critical(
                self, "System Error", f"Cannot create temporary directory: {str(e)}"
            )
            return

        # Create progress dialog
        progress = QProgressDialog(
            "Preparing PDFs for printing...", None, 0, len(selected_pdfs), self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(False)
        progress.show()

        # Process each PDF
        successful = 0
        failed = 0
        errors = []
        processed_pdfs = []

        for idx, pdf_filename in enumerate(selected_pdfs):
            progress.setValue(idx)
            QApplication.processEvents()  # Update UI

            try:
                # Process PDF
                modified_pdf = self.processor.add_hospital_number(
                    pdf_filename, hospital_number, center_code, time_point
                )
                processed_pdfs.append((pdf_filename, modified_pdf))
                successful += 1

            except Exception as e:
                failed += 1
                errors.append(f"{pdf_filename}: {str(e)}")

        progress.close()

        # Open PDFs
        if merge_pdfs and len(processed_pdfs) > 0:
            # Merge all PDFs and open as one
            try:
                pdf_buffers = [pdf for _, pdf in processed_pdfs]
                merged_pdf = self.processor.merge_pdfs(pdf_buffers)

                # Save to temp
                temp_filename = f"{hospital_number}_merged.pdf"
                temp_path = temp_dir / temp_filename

                with open(temp_path, "wb") as f:
                    f.write(merged_pdf.getvalue())

                # Open with system viewer
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(temp_path)))

                message = f"Opened merged PDF in your default viewer for printing"
                QMessageBox.information(self, "Success", message)
                self.statusBar().showMessage("Opened merged PDF for printing")

                # Log operation
                self.operation_logger.log_operation(
                    time_point,
                    center_code,
                    hospital_number,
                    selected_pdfs,
                    "print",
                    merge_pdfs,
                    is_duplicate=(duplicate_info is not None),
                    reprint_reason=reprint_reason,
                    output_path=None,  # Print uses temp directory
                )

            except Exception as e:
                error_msg = f"Failed to merge and open PDFs: {str(e)}"
                QMessageBox.critical(self, "Merge Failed", error_msg)
                self.statusBar().showMessage("Merge failed")
        else:
            # Open individual PDFs
            for pdf_filename, modified_pdf in processed_pdfs:
                try:
                    # Save to temp
                    temp_filename = f"{hospital_number}_{Path(pdf_filename).stem}.pdf"
                    temp_path = temp_dir / temp_filename

                    with open(temp_path, "wb") as f:
                        f.write(modified_pdf.getvalue())

                    # Open with system viewer
                    QDesktopServices.openUrl(QUrl.fromLocalFile(str(temp_path)))

                except Exception as e:
                    failed += 1
                    errors.append(f"{pdf_filename}: {str(e)}")

            # Show results
            if successful > 0:
                message = f"Opened {successful} PDF(s) in your default viewer for printing"
                if failed > 0:
                    message += f"\n\nFailed: {failed} PDF(s)"
                    for error in errors:
                        message += f"\n  • {error}"
                    QMessageBox.warning(self, "Partial Success", message)
                else:
                    QMessageBox.information(self, "Success", message)

                # Log operation (only log if at least one PDF was successful)
                self.operation_logger.log_operation(
                    time_point,
                    center_code,
                    hospital_number,
                    selected_pdfs,
                    "print",
                    merge_pdfs,
                    is_duplicate=(duplicate_info is not None),
                    reprint_reason=reprint_reason,
                    output_path=None,  # Print uses temp directory
                )
            else:
                error_msg = "Failed to prepare PDFs for printing:\n"
                for error in errors:
                    error_msg += f"  • {error}\n"
                QMessageBox.critical(self, "Print Failed", error_msg)

            self.statusBar().showMessage(f"Opened {successful} PDF(s) for printing")


# Import QApplication for processEvents
from PySide6.QtWidgets import QApplication
