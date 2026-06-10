---
name: Legacy Font Translation
description: Guidelines for converting and cleaning legacy visual-order fonts (KrutiDev, Asees) to Unicode for Hindi and Punjabi translations.
---

# Legacy Font Translation

This skill covers the conversion, reordering, and cleaning of Hindi and Punjabi translations derived from legacy visual-order fonts (e.g., KrutiDev for Hindi, Asees/Anmol Lipi for Punjabi) to clean Unicode.

## 1. Vowel Reordering (Sihari / Chhoti I)

In legacy visual-order fonts, the short vowel sign (Sihari `ਿ` in Gurmukhi, or Chhoti I `ि` in Devanagari) is physically typed and stored *before* the consonant. In Unicode, it must be stored *after* the consonant cluster.

### Punjabi Asees Sihari Reordering Rules
- Pattern: Match `i` followed by Gurmukhi consonants.
- Subjoined Consonants: The vowel must be shifted past subjoined R (`੍ਰ`) or subjoined H (`੍ਹ`).
- Exceptions: Do not shift past nasalizers/geminating marks like adhak (`ੱ`) or tippi (`ੰ`).
- Code snippet:
  ```python
  # Reorder visual 'i' past Gurmukhi consonants and optional subjoined markers
  punj_consonant = r'[\u0a05-\u0a39\u0a59-\u0a5c\u0a5e]'
  pattern = r'ਿ((?:' + punj_consonant + r'੍)*' + punj_consonant + r')'
  text = re.sub(pattern, r'\1\u0a3f', text)
  ```

### Devanagari Sihari Reordering Rules
- Pattern: Match `ि` U+093f followed by Devanagari consonants.
- Conjuncts: The vowel sign must move past halant-joined consonant clusters (e.g., `स` + `्` + `त`).
- Code snippet:
  ```python
  dev_consonant = r'[क-हक़-य़]'
  pattern = r'ि((?:' + dev_consonant + r'़?्)*़?' + dev_consonant + r'़?)'
  text = re.sub(pattern, r'\1ि', text)
  ```

## 2. Glyph-to-Unicode Mapping Artifacts

Text extracted directly from PDFs using simple extractors often leaks visual placeholders from other blocks (Cyrillic, Georgian) instead of standard Devanagari or Gurmukhi characters:

- **Cyrillic Small Letter Narrow O (`ᲂ` / U+1c82)**: Maps to Devanagari vowel sign O + Bindu (`ों` U+094b + U+0902).
- **Georgian Small Letter Labial Sign (`ᱶ` / U+1c76)**: Maps to Devanagari vowel sign E + Bindu (`ें` U+0947 + U+0902).
- **Georgian Capital Letter An (`Ა` / U+1c90)**: Maps to Devanagari vowel sign O + Bindu (`ों`).
- **Limbu Letter Dha (`ᱫ` / U+1c5d)**: Maps to conjunct double-ta (`त्त` U+0924 + U+094d + U+0924).
- **Adhak/Tippi Independent Vowels (Punjabi)**: Clean up compound characters like `ੲਿ` -> `ਇ`, `ੳੁ` -> `ਉ`, `ਅਾ` -> `ਆ`.

## 3. Bilingual Mapping Standard

All translation files under `redcap/translation/` must adhere to:
1. **Strictly Bilingual Format**: Use `English / Translation` or `English <br> Translation` as dictated by the REDCap schema.
2. **Zero Kannada Leaks**: Ensure no character codes in the Kannada block (`\u0c80-\u0cff`) remain in Hindi (`hi`), Punjabi (`pa`), Tamil (`ta`), or Telugu (`te`) translation files.
3. **Clinical Exclusions**: Clinical/observer-rated scales must remain in English; only patient-facing questionnaires (PHQ-9, SIPSO, CSI, FSS, MAL) and key demographic headers (Subject ID, Screening Subject ID) should be translated.
