---
name: Motor Activity Log (MAL) Assessment
description: Standards, exact task order, wording, REDCap configuration, and language policies for the Motor Activity Log (MAL).
---

# Motor Activity Log (MAL) Assessment

## Instrument Overview
The **Motor Activity Log (UE MAL)** is a semi-structured interview assessing arm use during 30 activities of daily living (ADLs) after stroke.

## Exact 30 Tasks (Original Order & Verbatim Wording)
All implementations (REDCap CSVs, dictionaries, and documentation) must preserve this exact sequence and wording:
1. Turn on a light with a light switch
2. Open drawer
3. Remove an item of clothing from a drawer
4. Pick up phone
5. Wipe off a kitchen counter or other surface
6. Get out of a car (includes only the movement needed to get body from sitting to standing outside of the car, once the door is open).
7. Open refrigerator
8. Open a door by turning a door knob / handle
9. Use a TV remote control
10. Wash your hands (includes lathering and rinsing hands; does not include turning water on and off with a faucet handle).
11. Turning water on/off with knob/lever on faucet
12. Dry your hands
13. Put on your socks
14. Take off your socks
15. Put on your shoes (includes tying shoestrings and fastening straps)
16. Take off your shoes (includes untying shoestrings and unfastening straps)
17. Get up from a chair with armrests
18. Pull chair away from table before sitting down
19. Pull chair toward table after sitting down
20. Pick up a glass, bottle, drinking cup, or can (does not need to include drinking)
21. Brush your teeth (does not include preparation of toothbrush or brushing dentures unless the dentures are brushed while left in the mouth)
22. Put on makeup base, lotion, or shaving cream on face
23. Use a key to unlock a door
24. Write on paper (If hand used to write pre-stroke is more affected, score item; if non-writing hand pre-stroke is more affected, drop item and assign N/A)
25. Carry an object in your hand (draping an item over the arm is not acceptable)
26. Use a fork or spoon for eating (refers to the action of bringing food to the mouth with fork or spoon)
27. Comb your hair
28. Pick up a cup by a handle
29. Button a shirt
30. Eat half a sandwich or finger foods

## REDCap Form Architecture

### 1. Continuous Table Layout
- All 30 tasks are embedded in **one continuous HTML table** under the descriptive field `mal_table` (Section Header: `MOTOR ACTIVITY LOG TASKS`).
- **Do not split** tasks into separate tables or chunked section headers (e.g., `TASKS 1-5`, `TASKS 6-10`).
- Columns: Task (31%), AS (12%), HW (12%), Code (12%), Comments (33%).

### 2. Field Types & Scoring Scales
- **Amount Scale (AS)**: `mal_as_1` to `mal_as_30` (dropdown, choices: `0, 0 | 0.5, 0.5 | 1, 1 | 1.5, 1.5 | 2, 2 | 2.5, 2.5 | 3, 3 | 3.5, 3.5 | 4, 4 | 4.5, 4.5 | 5, 5`). Mandatory (`Required Field? = 'y'`).
- **How Well Scale (HW)**: `mal_hw_1` to `mal_hw_30` (dropdown, choices same as AS). Mandatory (`Required Field? = 'y'`).
- **Codes for "No" Responses (Why)**: `mal_why_1` to `mal_why_30` (dropdown, choices: `1, 1 | 2, 2 | 3, 3 | 4, 4 | 5, 5`).
  - **Must be OPTIONAL** (`Required Field? = ""`).
  - Exempted in `redcap/clean_redcap.py` via `is_code_field`.
  - If a code is selected accidentally, selecting the default `-- select --` clears/deletes the value without validation error.
- **Comments**: `mal_comm_1` to `mal_comm_30` (text). Optional.
- **Mean Scores**:
  - `mal_mean_as`: `([mal_as_1]+...+[mal_as_30]) / 30` (calc).
  - `mal_mean_hw`: `([mal_hw_1]+...+[mal_hw_30]) / 30` (calc).

## Single-Language Policy in REDCap
- **MAL is single-language only (English)** in REDCap Multi-Language Management (MLM).
- **Do not add** bilingual translations (`English / Translated`) for MAL in `redcap/translation/*_single_doc.json`. Doing so corrupts the 5-column table layout.
- Other relevant assessments (CSI, SIPSO, EQ-5D, PHQ-9, FSS) remain bilingual.
- Printed language copies are available as standalone PDF files in `files/`:
  - English: `07 EN MAL.pdf`
  - Tamil: `07 TA MAL.pdf`
  - Telugu: `07 TE MAL.pdf`
  - Hindi: `07 HI MAL.pdf`
  - Punjabi: `07 PA MAL.pdf`
  - Kannada: `07 KA MAL.pdf`
