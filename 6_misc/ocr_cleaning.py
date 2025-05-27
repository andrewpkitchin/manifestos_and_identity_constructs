import re
from pathlib import Path

def safe_digit_fix(text):
    # Case 1: Specific known replacements
    text = re.sub(r'\b2lst\b', '21st', text, flags=re.IGNORECASE)

    # Case 2: Numbered list item fix (l. Intro → 1. Intro)
    text = re.sub(r'\b(l)(\.\s)', r'1\2', text)

    # Case 3: Fix 4-char words likely to be years (like 2OlO → 2010)
    def fix_possible_years(match):
        word = match.group(0)
        corrected = word.replace('l', '1').replace('O', '0')
        if corrected.isdigit():
            year = int(corrected)
            if 1800 <= year <= 2100:
                return corrected
        return word
    text = re.sub(r'\b[\dOl]{4}\b', fix_possible_years, text)

    # Case 4: Symbol-number patterns (like £lO → £10)
    def fix_symbol_numbers(match):
        symbol, digits = match.groups()
        fixed = digits.replace('l', '1').replace('O', '0')
        return f"{symbol}{fixed}"
    text = re.sub(r'([£$#%])([\dOl]{1,6})', fix_symbol_numbers, text)

    # Case 5: Lone £l → £1
    text = re.sub(r'\b£l\b', '£1', text)

    # Case 6: General numeric-looking words (like lO0 → 100)
    def fix_general_numbers(match):
        word = match.group(0)
        return word.replace('l', '1').replace('O', '0')
    text = re.sub(r'\b[\dOl]{2,6}\b', fix_general_numbers, text)

    return text

def process_folder(input_folder, output_folder):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    for file_path in input_path.glob("*.txt"):
        with open(file_path, 'r', encoding='utf-8') as infile:
            text = infile.read()

        corrected_text = safe_digit_fix(text)

        out_file = output_path / file_path.name
        with open(out_file, 'w', encoding='utf-8') as outfile:
            outfile.write(corrected_text)

        print(f"Corrected: {file_path.name}")


# Example usage
if __name__ == "__main__":
    input_dir = "/Users/user/programming/manifestos_and_identity/2d_checked_and_further_cleaned_text_files"
    output_dir = "/Users/user/programming/manifestos_and_identity/2d_checked_and_further_cleaned_text_files"
    process_folder(input_dir, output_dir)