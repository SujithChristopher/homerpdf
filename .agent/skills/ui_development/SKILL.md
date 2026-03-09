---
name: UI Development
description: Best practices and common tasks for the PySide6 UI.
---

# UI Development

## Layout Guidelines
- Main window size is fixed at **550x650px**.
- Use `QGroupBox` to categorize inputs (Patient Info, Included Files).
- Button states are automatically toggled by `validate_inputs()`.

## Themes and Styling
- Styles are defined in `apply_theme()` within `ui/main_window.py`.
- **Light/Dark Mode**: Detected using `palette.color(QPalette.Window).lightness()`.
- Use the defined theme variables (`group_bg`, `input_bg`, `text_color`) for all custom styles.

## New Widget Workflow
1. Add widget in `setup_ui()`.
2. Connect signals (e.g., `textChanged`, `clicked`) to handler methods.
3. Update `validate_inputs()` if the new widget is a required field.
4. Call `on_input_changed()` to sync button states.

## Navigation
- Use `QFileDialog` for selecting directories.
- Use `QMessageBox` for user feedback (Success/Error).
- Use `QProgressDialog` for long-running PDF operations.
