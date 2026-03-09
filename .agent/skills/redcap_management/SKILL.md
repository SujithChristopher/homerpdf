---
name: REDCap Management
description: Instructions for adding/modifying instruments, managing display logic, and handling translations.
---

# REDCap Management

## Adding a New Instrument
1. **Create Instrument CSV**: Place a new CSV (e.g., `instrument_name.csv`) in the `redcap/` directory.
    - Must include `homer_id` as the first column.
    - Define fields using REDCap format (Variable Name, Form Name, Field Type, Label, etc.).
2. **Setup Display Logic**: Update `redcap/final/form_display_logic.csv`.
    - Add the new form name to the appropriate events (a1_arm_1, a2_arm_1).
    - Define control conditions (e.g., `[a0_arm_1][patient_demographics_complete] = '2'`).
3. **Regenerate Dictionary**: Run the cleanup script:
    - Path: `redcap/clean_redcap.py`
    - Command: `python redcap/clean_redcap.py`
    - Output: `redcap/final/final.csv`
4. **UI Visibility**: Add a placeholder PDF with a matching name in the `files/` directory.

## Instrument Field Standards
- Use `text` for numerical scores with `number` or `int` validation.
- Use `radio` for multiple choice questions.
- Use `calc` for automated score totals.
- All fields automatically get `@READONLY-IF([completed_assessment_complete] = '2')` via the cleanup script.

## Translations
- Located in `redcap/translation/`.
- Format: JSON files mapping internal keys to localized strings.
- Always check `sipso_template.json` for structure.
