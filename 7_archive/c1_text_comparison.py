#!/usr/bin/env python3
"""Compare multiple text extraction versions of the same document.

For every group of files that share the prefix ``yyyy-mm-partyname`` this script
computes a set of text‑quality metrics for each available extraction method:

* word_count
* sentence_count
* char_count
* avg_word_length
* punctuation_frequency
* lexical_diversity
* ocr_error_rate   – a very rough heuristic

It then elects the *recommended_file* (i.e. the method/filename judged
"best") using a simple quality score:

    quality = word_count * (1 - ocr_error_rate)

The results are written to a single CSV file named
``extraction_comparison_summary.csv`` in the same folder.

Usage
-----
$ python compare_extractions.py /path/to/folder
"""

from __future__ import annotations

import argparse
import csv
import re
import string
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

_METHOD_ORDER = ("from_csv", "pymupdf", "tesseract")

#: Match e.g. ``2019-12-liberal_democrats_tesseract_extraction.txt``
#: or ``2019-12-liberal_democrats_from_csv.txt``
_PATTERN = re.compile(
    r"^"  # start
    r"(?P<prefix>\d{4}-\d{2}-[a-z0-9_]+)"  # yyyy-mm-partyname
    r"_"  # underscore
    r"(?P<method>from_csv|pymupdf_extraction|tesseract_extraction)"  # method
    r"\.txt$",  # .txt extension and end
    re.IGNORECASE,
)

_SENTENCE_BOUNDARY = re.compile(r"[.!?…]+\s|\n+")


def _tokenise(text: str) -> List[str]:
    """Very light‑weight tokenizer that splits on whitespace."""
    return text.split()


def _ocr_error_heuristic(words: List[str]) -> float:
    """Return fraction of *words* that look suspicious.

    A word is flagged if it contains the Unicode replacement character �,
    mixed digits + letters (e.g. "l0ve"), or any non‑ASCII symbol.
    """
    suspicious = 0
    for w in words:
        if "�" in w:
            suspicious += 1
            continue
        if re.search(r"[A-Za-z].*\d|\d.*[A-Za-z]", w):
            suspicious += 1
            continue
        if any(ord(ch) > 127 for ch in w):
            suspicious += 1
    return suspicious / max(len(words), 1)


def _compute_metrics(text: str) -> Dict[str, float]:
    words = _tokenise(text)
    word_count = len(words)
    sentences = _SENTENCE_BOUNDARY.split(text)
    sentences = [s for s in sentences if s.strip()]
    sentence_count = len(sentences)
    char_count = len(text)
    avg_word_length = (sum(len(w) for w in words) / word_count) if word_count else 0
    punctuation_count = sum(1 for ch in text if ch in string.punctuation)
    punctuation_frequency = punctuation_count / max(char_count, 1)
    lexical_diversity = len(set(words)) / max(word_count, 1)
    ocr_error_rate = _ocr_error_heuristic(words)
    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "char_count": char_count,
        "avg_word_length": avg_word_length,
        "punctuation_frequency": punctuation_frequency,
        "lexical_diversity": lexical_diversity,
        "ocr_error_rate": ocr_error_rate,
    }


def _quality_score(metrics: Dict[str, float]) -> float:
    return metrics["word_count"] * (1 - metrics["ocr_error_rate"])


def _gather_files(folder: Path):
    groups: Dict[str, Dict[str, Path]] = defaultdict(dict)
    for file in folder.glob("*.txt"):
        match = _PATTERN.match(file.name)
        if not match:
            continue  # unrelated file
        prefix = match.group("prefix").lower()
        # normalise method names
        raw_method = match.group("method").lower()
        if raw_method.startswith("pymupdf"):
            method = "pymupdf"
        elif raw_method.startswith("tesseract"):
            method = "tesseract"
        else:
            method = "from_csv"
        groups[prefix][method] = file
    return groups


def compare_folder(folder: Path) -> Path:
    """Process *folder* and create the summary CSV. Returns CSV path."""
    groups = _gather_files(folder)
    if not groups:
        raise FileNotFoundError(f"No matching *_extraction.txt or *_from_csv.txt in {folder}")
    csv_path = folder / "extraction_comparison_summary.csv"

    fieldnames = [
        "source_id",
        "word_count",
        "sentence_count",
        "char_count",
        "avg_word_length",
        "punctuation_frequency",
        "lexical_diversity",
        "ocr_error_rate",
        "recommended_file",
    ]
    with csv_path.open("w", newline="", encoding="utf8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        for source_id, files_by_method in sorted(groups.items()):
            # Compute metrics per available method
            metrics_by_method: Dict[str, Dict[str, float]] = {}
            for method, path in files_by_method.items():
                text = path.read_text(encoding="utf8", errors="replace")
                metrics_by_method[method] = _compute_metrics(text)

            # Prepare lists for each metric, following _METHOD_ORDER but omitting missing
            row = {"source_id": source_id}
            for metric_name in (
                "word_count",
                "sentence_count",
                "char_count",
                "avg_word_length",
                "punctuation_frequency",
                "lexical_diversity",
                "ocr_error_rate",
            ):
                row[metric_name] = [
                    round(metrics_by_method[m][metric_name], 4)  # fewer decimals for floats
                    for m in _METHOD_ORDER
                    if m in metrics_by_method
                ]

            # Determine recommended file
            best_method, _ = max(
                ((m, _quality_score(metrics)) for m, metrics in metrics_by_method.items()),
                key=lambda t: t[1],
            )
            row["recommended_file"] = files_by_method[best_method].name
            writer.writerow(row)

    return csv_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare text extraction outputs within a folder.")
    parser.add_argument(
        "folder",
        type=Path,
        help="Folder containing *_extraction.txt and *_from_csv.txt files.",
    )
    args = parser.parse_args()
    csv_path = compare_folder(args.folder.resolve())
    print(f"Summary written to {csv_path}")



# ── run automatically on your cleaned-text folder ────────────────────────
if __name__ == "__main__":
    """
    When the script is executed directly, compare all *_extraction.txt /
    *_from_csv.txt files inside the manifesto folder below and write the
    summary CSV next to them.
    """
    from pathlib import Path

    # ← change this if your folder ever moves
    target_folder = Path(
        "/Users/user/programming/manifestos_and_identity/2b_cleaned_text_files"
    ).resolve()

    csv_path = compare_folder(target_folder)
    print(f"Summary written to {csv_path}")
# ─────────────────────────────────────────────────────────────────────────