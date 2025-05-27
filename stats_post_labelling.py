import pandas as pd

# --- File paths ---
input_file = "/Users/user/programming/manifestos_and_identity/5_labelled/labelled.csv"
output_file = "/Users/user/programming/manifestos_and_identity/5_labelled/labelled_summary_stats.csv"

# --- Load input ---
df = pd.read_csv(input_file)

# --- Add word count for each chunk if not already present ---
if "word_count" not in df.columns:
    df["word_count"] = df["chunk_text"].str.split().apply(len)

# --- Define constructs explicitly ---
constructs = [
    "National Identification",
    "Patriotism",
    "National Narcissism",
    "Nationalism"
]

# --- Build aggregation dictionary ---
agg_dict = {
    "chunk_text": "count",
    "word_count": "sum"
}
agg_dict.update({construct: "sum" for construct in constructs if construct in df.columns})

# --- Group by document_name ---
summary_df = df.groupby("document_name").agg(agg_dict).rename(columns={
    "chunk_text": "number_of_chunks",
    "word_count": "total_word_count",
    **{construct: f"count_{construct}" for construct in constructs if construct in df.columns}
}).reset_index()

# --- Save to CSV ---
summary_df.to_csv(output_file, index=False)
print(f"✅ Summary saved to {output_file}")