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
    return sum(1 for word in text.split() if re.search(r'[^-]', word)) / max(len(text.split()), 1)

def average_word_length(text):
    words = text.split()
    return sum(len(word) for word in words) / max(len(words), 1)

def punctuation_frequency(text):
    return sum(1 for c in text if c in '.,;:!?') / max(len(text), 1)

def format_metric_list(values, method_order):
    """Format a list of values with method labels"""
    formatted = []
    method_labels = {
        'from_csv': 'from_csv',
        'pymupdf_extraction': 'PyMuPDF',
        'tesseract_extraction': 'Tesseract'
    }
    
    for method, value in zip(method_order, values):
        if value is not None:
            label = method_labels.get(method, method)
            if isinstance(value, float):
                formatted.append(f"{label}:{value:.4f}")
            else:
                formatted.append(f"{label}:{value}")
        else:
            formatted.append(f"{method_labels.get(method, method)}:N/A")
    
    return ", ".join(formatted)

def calculate_recommendation(metrics_dict, method_order):
    """Calculate recommendation based on multiple metrics"""
    scores = {}
    
    for i, method in enumerate(method_order):
        score = 0
        valid_metrics = 0
        
        # Word count - higher is generally better (more complete extraction)
        if metrics_dict['word_counts'][i] is not None:
            word_score = metrics_dict['word_counts'][i]
            score += word_score
            valid_metrics += 1
        
        # Character count - higher is generally better
        if metrics_dict['char_counts'][i] is not None:
            char_score = metrics_dict['char_counts'][i] / 100  # Scale down
            score += char_score
            valid_metrics += 1
        
        # OCR error rate - lower is better (invert the score)
        if metrics_dict['ocr_error_rates'][i] is not None:
            error_penalty = metrics_dict['ocr_error_rates'][i] * 1000  # Scale up as penalty
            score -= error_penalty
            valid_metrics += 1
        
        # Average word length - should be reasonable (4-6 is typical)
        if metrics_dict['avg_word_lengths'][i] is not None:
            avg_len = metrics_dict['avg_word_lengths'][i]
            # Penalize very short or very long average word lengths
            if 4 <= avg_len <= 6:
                score += 50
            else:
                score -= abs(avg_len - 5) * 10
            valid_metrics += 1
        
        # Punctuation frequency - moderate is better
        if metrics_dict['punctuation_freqs'][i] is not None:
            punct_freq = metrics_dict['punctuation_freqs'][i]
            # Ideal punctuation frequency around 0.05-0.15
            if 0.05 <= punct_freq <= 0.15:
                score += 30
            else:
                score -= abs(punct_freq - 0.1) * 100
            valid_metrics += 1
        
        if valid_metrics > 0:
            scores[method] = score / valid_metrics
    
    if not scores:
        return "No data available"
    
    # Find the best method
    best_method = max(scores, key=scores.get)
    method_labels = {
        'from_csv': 'from_csv',
        'pymupdf_extraction': 'PyMuPDF',
        'tesseract_extraction': 'Tesseract'
    }
    
    return method_labels.get(best_method, best_method)

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
            "ocr_error_rates", "avg_word_lengths", "punctuation_freqs", "recommendation"
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

            # Prepare metrics for recommendation calculation
            metrics_dict = {
                'word_counts': word_counts,
                'char_counts': char_counts,
                'ocr_error_rates': ocr_error_rates,
                'avg_word_lengths': avg_word_lengths,
                'punctuation_freqs': punctuation_freqs
            }

            # Calculate recommendation
            recommendation = calculate_recommendation(metrics_dict, method_order)

            # Format and write results
            writer.writerow({
                "group": group,
                "word_counts": format_metric_list(word_counts, method_order),
                "sentence_counts": format_metric_list(sentence_counts, method_order),
                "char_counts": format_metric_list(char_counts, method_order),
                "ocr_error_rates": format_metric_list(ocr_error_rates, method_order),
                "avg_word_lengths": format_metric_list(avg_word_lengths, method_order),
                "punctuation_freqs": format_metric_list(punctuation_freqs, method_order),
                "recommendation": recommendation
            })

    return str(output_file)

if __name__ == "__main__":
    target_folder = "/Users/user/programming/manifestos_and_identity/2b_cleaned_text_files"
    csv_path = compare_folder(target_folder)
    print(f"Summary CSV written to: {csv_path}")