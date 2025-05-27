import pandas as pd
from pathlib import Path

# Define paths
source_dir = Path("/Users/user/programming/manifestos_and_identity/1_manifesto_files/csv")
output_dir = Path("/Users/user/programming/manifestos_and_identity/2a_text_output_files")

# Create output directory if it doesn't exist
output_dir.mkdir(parents=True, exist_ok=True)

# Process each CSV file in the source directory
for csv_file in source_dir.glob("*.csv"):
    try:
        df = pd.read_csv(csv_file)
        text_data = df["text"].dropna().astype(str).tolist()

        # Combine all text chunks into one string, each followed by a newline
        combined_text = "\n".join(text_data)

        # Construct the output file name
        new_name = csv_file.stem + "_from_csv.txt"
        output_path = output_dir / new_name

        # Write to the output file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(combined_text)

        print(f"Processed: {csv_file.name} -> {new_name}")
    except Exception as e:
        print(f"Error processing {csv_file.name}: {e}")