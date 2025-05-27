import os
import re
import pandas as pd
from pathlib import Path
from nltk.tokenize import sent_tokenize
import nltk

# Ensure punkt is available
nltk.download('punkt', download_dir='/Users/user/nltk_data')
nltk.data.path.append('/Users/user/nltk_data')


def split_cleaned_text_to_chunks(txt_path: str, max_length: int = 280):
    with open(txt_path, 'r', encoding='utf-8') as file:
        text = file.read()

    sentences = sent_tokenize(text.replace('\n', ' ').strip())

    chunks = []
    current_chunk = ""
    chunk_number = 1

    for sentence in sentences:
        if len(sentence) > max_length:
            continue
        if len(current_chunk) + len(sentence) + (1 if current_chunk else 0) <= max_length:
            current_chunk += (" " if current_chunk else "") + sentence
        else:
            chunks.append((chunk_number, current_chunk.strip()))
            chunk_number += 1
            current_chunk = sentence

    if current_chunk:
        chunks.append((chunk_number, current_chunk.strip()))

    return [
        {"document_name": os.path.basename(txt_path), "chunk_number": num, "chunk_text": chunk}
        for num, chunk in chunks
    ]


def process_txt_folder(folder_path: str, output_csv: str):
    existing_files = set()

    if os.path.exists(output_csv):
        existing_df = pd.read_csv(output_csv)
        existing_files = set(existing_df["document_name"].unique())
    else:
        existing_df = pd.DataFrame()

    all_chunks = []

    for file in Path(folder_path).glob("*.txt"):
        if file.name not in existing_files:
            print(f"Processing new file: {file.name}")
            chunks = split_cleaned_text_to_chunks(str(file))
            all_chunks.extend(chunks)
        else:
            print(f"Skipping existing file: {file.name}")

    if all_chunks:
        new_df = pd.DataFrame(all_chunks)
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
        final_df.to_csv(output_csv, index=False, encoding="utf-8")
        print(f"Added {len(new_df)} new chunks.")
    else:
        print("No new files to process.")


if __name__ == "__main__":
    base_dir = "/Users/user/programming/manifestos_and_identity/"
    input_folder = os.path.join(base_dir, "test_folder")
    output_csv_path = os.path.join(base_dir, "test.csv")

    process_txt_folder(input_folder, output_csv_path)