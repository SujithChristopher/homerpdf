import csv
import os
import re

def clean_name(name):
    """Clean variable and form names for REDCap: lowercase, underscores only."""
    if not name:
        return ""
    name = name.strip().lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    # Remove leading numbers
    name = re.sub(r'^[0-9]+', '', name)
    # Remove redundant underscores
    name = re.sub(r'_+', '_', name)
    return name.strip('_')

def process_redcap_csvs(input_dir, output_file):
    all_rows = []
    seen_vars = set()
    
    # 1. Define Demographics Form Rows
    demographics_form = "patient_demographics"
    demo_fields = [
        ["homer_id", demographics_form, "", "text", "Record ID (HOMER ID)", "", "", "", "", "", "y", "", "", "", "", "", "", ""],
        ["hospital_id", demographics_form, "", "text", "Hospital ID", "", "", "", "", "", "y", "", "", "", "", "", "", ""],
        ["assessor_name", demographics_form, "", "text", "Name of Assessor", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        ["date_of_assessment", demographics_form, "", "text", "Date of Assessment", "", "", "date_ymd", "", "", "", "", "", "", "", "", "", ""],
        ["time_since_stroke", demographics_form, "", "text", "Time Since Stroke", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        ["affected_side", demographics_form, "", "radio", "Affected Side", "1, Left | 2, Right | 3, Bilateral", "", "", "", "", "", "", "", "", "", "", "", ""],
        ["dominant_hand", demographics_form, "", "radio", "Dominant Hand", "1, Left | 2, Right | 3, Ambidextrous", "", "", "", "", "", "", "", "", "", "", "", ""],
        ["stroke_type", demographics_form, "", "text", "Stroke Type", "", "", "", "", "", "", "", "", "", "", "", "", ""],
    ]
    
    standard_header = [
        'Variable / Field Name', 'Form Name', 'Section Header', 'Field Type', 
        'Field Label', 'Choices, Calculations, OR Slider Labels', 'Field Note', 
        'Text Validation Type OR Show Slider Number', 'Text Validation Min', 
        'Text Validation Max', 'Identifier?', 'Branching Logic (Show field only if...)', 
        'Required Field?', 'Custom Alignment', 'Question Number (surveys only)', 
        'Matrix Group Name', 'Matrix Ranking?', 'Field Annotation'
    ]

    for field in demo_fields:
        dict_row = dict(zip(standard_header, field))
        all_rows.append(dict_row)
        seen_vars.add(field[0])

    files = [f for f in os.listdir(input_dir) if f.endswith('.csv') and f != os.path.basename(output_file) and f != "clean_redcap.py"]
    files.sort()

    print(f"Found files: {files}")

    for filename in files:
        filepath = os.path.join(input_dir, filename)
        with open(filepath, mode='r', encoding='utf-8-sig') as f:
            raw_reader = csv.reader(f)
            try:
                file_header = next(raw_reader)
            except StopIteration:
                continue
            
            for row in raw_reader:
                if not row or not row[0].strip() or row[0].strip() == 'Variable / Field Name' or row[0].strip().lower() == 'record id':
                    continue

                if len(row) >= 19:
                    var_name = row[0].strip()
                    form_name = row[1].strip()
                    section = row[2]
                    f_type = row[3]
                    label = row[4]
                    choice = row[5]
                    calc = row[6]
                    slider = row[7]
                    note = row[8] if len(row) > 8 else ""
                    val_type = row[9] if len(row) > 9 else ""
                    val_min = row[10] if len(row) > 10 else ""
                    val_max = row[11] if len(row) > 11 else ""
                    ident = row[12] if len(row) > 12 else ""
                    branch = row[13] if len(row) > 13 else ""
                    req = row[14] if len(row) > 14 else ""
                    align = row[15] if len(row) > 15 else ""
                    q_num = row[16] if len(row) > 16 else ""
                    matrix = row[17] if len(row) > 17 else ""
                    rank = row[18] if len(row) > 18 else ""
                    annot = row[19] if len(row) > 19 else ""
                    
                    merged_choice = ""
                    if choice.strip(): merged_choice = choice.strip()
                    elif calc.strip(): merged_choice = calc.strip()
                    elif slider.strip(): merged_choice = slider.strip()
                elif len(row) == 18:
                    var_name, form_name, section, f_type, label, merged_choice, note, val_type, val_min, val_max, ident, branch, req, align, q_num, matrix, rank, annot = row + [""] * (18 - len(row))
                else:
                    continue

                if var_name.strip().lower() == 'homer_id':
                    continue
                
                # REMOVE redundant admin fields (date, examiner) from follow-up forms
                if any(re.match(p, var_name.lower()) for p in [r'.*_date$', r'.*_examiner$']):
                    continue

                cleaned_var = clean_name(var_name)
                if cleaned_var in seen_vars:
                    original_var = cleaned_var
                    counter = 1
                    while cleaned_var in seen_vars:
                        cleaned_var = f"{original_var}_{counter}"
                        counter += 1
                
                seen_vars.add(cleaned_var)
                
                f_type = f_type.lower().strip()
                valid_field_types = ['text', 'notes', 'radio', 'dropdown', 'calc', 'file', 'checkbox', 'yesno', 'truefalse', 'descriptive', 'slider']
                if f_type not in valid_field_types:
                    f_type = 'text' if label else 'descriptive'
                
                if f_type != 'text':
                    val_type = val_min = val_max = ""

                ident = 'y' if ident.lower().strip() == 'y' else ""
                req = 'y' if req.lower().strip() == 'y' else ""
                rank = 'y' if rank.lower().strip() == 'y' else ""
                
                valid_alignments = ['LV', 'LH', 'RV', 'RH']
                if align.upper().strip() not in valid_alignments:
                    align = ""
                
                validation_types = ['date_ymd', 'date_mdy', 'date_dmy', 'datetime_ymd', 'datetime_seconds_ymd', 'int', 'float', 'number', 'email', 'phone']
                if any(v in merged_choice for v in validation_types) and f_type == 'text':
                    if not val_type:
                        val_type = merged_choice
                        merged_choice = ""

                new_row = {
                    'Variable / Field Name': cleaned_var,
                    'Form Name': clean_name(form_name),
                    'Section Header': section,
                    'Field Type': f_type,
                    'Field Label': label,
                    'Choices, Calculations, OR Slider Labels': merged_choice,
                    'Field Note': note,
                    'Text Validation Type OR Show Slider Number': val_type,
                    'Text Validation Min': val_min,
                    'Text Validation Max': val_max,
                    'Identifier?': ident,
                    'Branching Logic (Show field only if...)': branch,
                    'Required Field?': req,
                    'Custom Alignment': align,
                    'Question Number (surveys only)': q_num,
                    'Matrix Group Name': matrix,
                    'Matrix Ranking?': rank,
                    'Field Annotation': annot
                }
                all_rows.append(new_row)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=standard_header)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Successfully merged {len(files)} files into {output_file}")
    print(f"Total rows (including Demographics): {len(all_rows)}")

if __name__ == "__main__":
    input_directory = r"e:\homer\homerpdf\redcap"
    output_csv = r"e:\homer\homerpdf\redcap\final\final.csv"
    process_redcap_csvs(input_directory, output_csv)
