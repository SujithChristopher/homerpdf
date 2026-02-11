"""Hospital PDF Manager - Main application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    """Initialize and run the application."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Homer PDF Manager")
    app.setApplicationVersion("0.1.0")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
