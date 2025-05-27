import os
import shutil
import re

# Define input and output folders
input_folder = "/Users/user/programming/manifestos_and_identity/2d_checked_and_further_cleaned_text_files"
output_folder = "/Users/user/programming/manifestos_and_identity/2e_final_pre_chunked_files"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Define suffixes to remove
suffixes_to_remove = [
    "_tesseract_extraction",
    "_pymupdf_extraction",
    "_from_csv",
    "_manual_extraction"
]

# Go through all .txt files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        new_filename = filename
        for suffix in suffixes_to_remove:
            new_filename = re.sub(suffix, "", new_filename, flags=re.IGNORECASE)
        
        src_path = os.path.join(input_folder, filename)
        dest_path = os.path.join(output_folder, new_filename)

        shutil.copyfile(src_path, dest_path)
        print(f"Copied and renamed: {filename} -> {new_filename}")