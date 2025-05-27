
from __future__ import annotations

import os
import re
from pathlib import Path
import csv

def extract_group_key(filename):
    # Match any of the 3 suffix types, with or without _cleaned
    match = re.match(r"(.+?)_(tesseract_extraction|pymupdf_extraction|from_csv)(?:_cleaned)?\.txt", filename)
    if match:
        return match.group(1)
    return None

def word_count(text):
    return len(text.split())

def sentence_count(text):
    return len(re.findall(r'[.!?]', text))

def character_count(text):
    return len(text)

def ocr_error_rate(text):
    return sum(1 for word in text.split() if re.search(r'[^-]', word)) / max(len(text.split()), 1)

def average_word_length(text):
    words = text.split()
    return sum(len(word) for word in words) / max(len(words), 1)

def punctuation_frequency(text):
    return sum(1 for c in text if c in '.,;:!?') / max(len(text), 1)

def compare_folder(folder_path: str):
    folder = Path(folder_path)
    files = list(folder.glob("*.txt"))

    grouped = {}
    for f in files:
        group_key = extract_group_key(f.name)
        if group_key:
            grouped.setdefault(group_key, {})  # each group is a dict with methods as keys
            if '_tesseract_extraction' in f.name:
                grouped[group_key]['tesseract_extraction'] = f
            elif '_pymupdf_extraction' in f.name:
                grouped[group_key]['pymupdf_extraction'] = f
            elif '_from_csv' in f.name:
                grouped[group_key]['from_csv'] = f

    if not grouped:
        raise FileNotFoundError(f"No matching *_extraction.txt or *_from_csv.txt in {folder}")

    output_file = folder / "comparison_summary.csv"
    with open(output_file, "w", newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "group", "word_counts", "sentence_counts", "char_counts",
            "ocr_error_rates", "avg_word_lengths", "punctuation_freqs"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for group, methods in grouped.items():
            # Define consistent method order
            method_order = ['from_csv', 'pymupdf_extraction', 'tesseract_extraction']

            # Initialize placeholders for each metric
            word_counts = []
            sentence_counts = []
            char_counts = []
            ocr_error_rates = []
            avg_word_lengths = []
            punctuation_freqs = []

            for method in method_order:
                file = methods.get(method)
                if file:
                    with open(file, 'r', encoding='utf-8') as f:
                        text = f.read()
                    word_counts.append(word_count(text))
                    sentence_counts.append(sentence_count(text))
                    char_counts.append(character_count(text))
                    ocr_error_rates.append(ocr_error_rate(text))
                    avg_word_lengths.append(average_word_length(text))
                    punctuation_freqs.append(punctuation_frequency(text))
                else:
                    word_counts.append(None)
                    sentence_counts.append(None)
                    char_counts.append(None)
                    ocr_error_rates.append(None)
                    avg_word_lengths.append(None)
                    punctuation_freqs.append(None)

            # Collect results
            writer.writerow({
                "group": group,
                "word_counts": word_counts,
                "sentence_counts": sentence_counts,
                "char_counts": char_counts,
                "ocr_error_rates": ocr_error_rates,
                "avg_word_lengths": avg_word_lengths,
                "punctuation_freqs": punctuation_freqs
            })

    return str(output_file)

if __name__ == "__main__":
    target_folder = "/Users/user/programming/manifestos_and_identity/2a_text_output_files"
    csv_path = compare_folder(target_folder)
    print(f"Summary CSV written to: {csv_path}")
