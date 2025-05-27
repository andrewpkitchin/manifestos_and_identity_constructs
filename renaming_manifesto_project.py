import pandas as pd
from pathlib import Path
import shutil
import re

# --- CONFIGURATION ---
code_csv_path = Path("manifesto_project_codes.csv")
pdf_folder = Path("0a_manifesto_project_files/pdf")
csv_folder = Path("0a_manifesto_project_files/csv")
additional_folder = Path("0b_additional_manifesto_files")
output_folder = Path("1_manifesto_files")
output_folder.mkdir(parents=True, exist_ok=True)

# --- LOAD PARTY CODE MAPPING ---
df = pd.read_csv(code_csv_path)
party_code_map = {
    str(row["party"]): row["partyname"].lower().replace(" ", "_").replace("-", "_")
    for _, row in df.iterrows()
}

# --- SPECIAL CASES ---
special_cases = {
    "leave": "leave",
    "remain": "remain",
    "reform": "reform_uk"
}

rename_log = []

# --- HANDLE FILES WITH PARTY CODES (e.g. 51320_198706.pdf) ---
def handle_code_files(folder: Path, ext: str):
    for file_path in folder.glob(f"*.{ext}"):
        match = re.match(r"(\d+)_(\d{6})", file_path.stem)
        if not match:
            continue
        code, yyyymm = match.groups()
        year, month = yyyymm[:4], yyyymm[4:]
        party = party_code_map.get(code, code)
        new_name = f"{year}-{month}-{party}.{ext}"
        shutil.copy(file_path, output_folder / new_name)
        rename_log.append((file_path.name, new_name))

# --- HANDLE FILES IN ADDITIONAL FOLDER ---
def handle_additional_files(folder: Path):
    for file_path in folder.glob("*.pdf"):
        fname = file_path.stem.lower()

        match = re.match(r"manifesto_(\d{6})[_-](.+)", fname)
        if match:
            yyyymm, raw_party = match.groups()
            year, month = yyyymm[:4], yyyymm[4:]
            party = special_cases.get(raw_party, raw_party.replace(" ", "_").replace("-", "_"))
            new_name = f"{year}-{month}-{party}.pdf"
        elif "leave" in fname:
            new_name = "2016-06-leave.pdf"
        elif "remain" in fname:
            new_name = "2016-06-remain.pdf"
        else:
            continue

        shutil.copy(file_path, output_folder / new_name)
        rename_log.append((file_path.name, new_name))

# --- EXECUTE RENAMING ---
handle_code_files(pdf_folder, "pdf")
handle_code_files(csv_folder, "csv")
handle_additional_files(additional_folder)

# --- SAVE LOG ---
log_df = pd.DataFrame(rename_log, columns=["old_name", "new_name"])
log_df.to_csv(output_folder / "renaming_log.csv", index=False)

print(f"Renaming complete. {len(rename_log)} files processed.")