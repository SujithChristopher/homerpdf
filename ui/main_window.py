"""Main application window for Hospital PDF Manager."""

import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, QTimer
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
    QCheckBox,
)

from pdf.processor import PDFProcessor
from utils.validators import validate_hospital_number
from utils.paths import get_files_dir


class MainWindow(QMainWindow):
    """Main application window for Hospital PDF Manager."""

    # Center mapping
    CENTERS = [
        ("CMC", "CMC Vellore"),
        ("MNP", "Manipal Hospital"),
        ("LDH", "Ludhiana Hospital"),
    ]

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setWindowTitle("Hospital PDF Manager")
        self.setFixedSize(550, 650)

        # Initialize PDF processor with correct path (works in dev and packaged)
        self.pdf_dir = get_files_dir()
        self.processor = PDFProcessor(self.pdf_dir)

        # Setup UI
        self.setup_ui()

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

        info_layout.addLayout(hospital_layout)
        info_layout.addLayout(center_layout)
        info_group.setLayout(info_layout)

        # ===== PDF Selection Group =====
        pdf_group = QGroupBox("Select PDF Files")
        pdf_layout = QVBoxLayout()

        self.pdf_list = QListWidget()
        self.pdf_list.itemChanged.connect(self.on_selection_changed)

        # Populate PDF list
        pdf_files = sorted(self.pdf_dir.glob("*.pdf"))
        for pdf_file in pdf_files:
            item = QListWidgetItem(pdf_file.stem.upper())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, pdf_file.name)
            self.pdf_list.addItem(item)

        if not pdf_files:
            self.pdf_list.addItem("No PDFs found in files/ directory")

        pdf_layout.addWidget(self.pdf_list)
        pdf_group.setLayout(pdf_layout)

        # ===== Merge Option =====
        merge_layout = QHBoxLayout()
        self.merge_checkbox = QCheckBox("Merge into single PDF")
        self.merge_checkbox.setChecked(False)
        merge_layout.addWidget(self.merge_checkbox)
        merge_layout.addStretch()

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
        main_layout.addLayout(merge_layout)
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

        # Setup status bar
        self.statusBar().showMessage("Ready")

    def validate_inputs(self) -> bool:
        """
        Validate hospital number and PDF selection.

        Returns:
            True if validation passes, False otherwise
        """
        # Validate hospital number
        hospital_number = self.hospital_input.text().strip()
        is_valid, error_msg = validate_hospital_number(hospital_number)

        if not is_valid:
            self.set_input_invalid(True)
            return False

        # Check if any PDFs are selected
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
            # Add red border to input field
            self.hospital_input.setStyleSheet(
                "border: 2px solid red; border-radius: 3px; padding: 2px;"
            )
        else:
            # Remove red border
            self.hospital_input.setStyleSheet("")

    def on_input_changed(self):
        """Handle changes to hospital number or center selection."""
        self.update_button_states()

    def on_selection_changed(self):
        """Handle changes to PDF selection."""
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
        Get list of selected PDF filenames.

        Returns:
            List of selected PDF filenames
        """
        selected = []
        for i in range(self.pdf_list.count()):
            item = self.pdf_list.item(i)
            if item.checkState() == Qt.Checked:
                pdf_filename = item.data(Qt.UserRole)
                if pdf_filename:
                    selected.append(pdf_filename)
        return selected

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
        selected_pdfs = self.get_selected_pdfs()
        merge_pdfs = self.merge_checkbox.isChecked()

        if not selected_pdfs:
            QMessageBox.warning(self, "No Selection", "Please select at least one PDF")
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
                    pdf_filename, hospital_number, center_code
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
        selected_pdfs = self.get_selected_pdfs()
        merge_pdfs = self.merge_checkbox.isChecked()

        if not selected_pdfs:
            QMessageBox.warning(self, "No Selection", "Please select at least one PDF")
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
                    pdf_filename, hospital_number, center_code
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
            else:
                error_msg = "Failed to prepare PDFs for printing:\n"
                for error in errors:
                    error_msg += f"  • {error}\n"
                QMessageBox.critical(self, "Print Failed", error_msg)

            self.statusBar().showMessage(f"Opened {successful} PDF(s) for printing")


# Import QApplication for processEvents
from PySide6.QtWidgets import QApplication
