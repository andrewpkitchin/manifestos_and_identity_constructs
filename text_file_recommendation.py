import pandas as pd
import shutil
from pathlib import Path

# Define paths
input_dir = Path("/Users/user/programming/manifestos_and_identity/2b_cleaned_text_files")
output_dir = Path("/Users/user/programming/manifestos_and_identity/2c_checked_and_further_cleaned_text_files")

# Make sure the output directory exists
output_dir.mkdir(parents=True, exist_ok=True)

# Load the comparison summary
csv_path = "/Users/user/programming/manifestos_and_identity/2b_cleaned_text_files/comparison_summary.csv"  # Update if running locally
df = pd.read_csv(csv_path)

# Process each row
for idx, row in df.iterrows():
    base_name = row['group']  # This column should hold the yyyy_mm_partyname string
    recommended_method = row['recommendation']  # e.g. 'tesseract', 'pymupdf', etc.

    # Check for _from_csv file
    csv_filename = f"{base_name}_from_csv.txt"
    csv_path = input_dir / csv_filename

    if csv_path.exists():
        selected_file = csv_path
    else:
        # If no _from_csv, use recommended method
        recommended_filename = f"{base_name}_{recommended_method}_extraction.txt"
        recommended_path = input_dir / recommended_filename
        if recommended_path.exists():
            selected_file = recommended_path
        else:
            print(f"Skipping {base_name}: No _from_csv or recommended file found.")
            continue

    # Copy the selected file
    dest_path = output_dir / selected_file.name
    shutil.copy(selected_file, dest_path)
    print(f"Copied: {selected_file.name}")

print("File transfer complete.")