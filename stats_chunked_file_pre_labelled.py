import pandas as pd

# Path to your input CSV
input_path = '/Users/user/programming/manifestos_and_identity/3_chunked/chunks.csv'
output_path = '/Users/user/programming/manifestos_and_identity/4_statistical_summaries/chunks_summary_stats.csv'

# Load the CSV
df = pd.read_csv(input_path)

# Ensure chunk text is string type and calculate word count per chunk
df['chunk_word_count'] = df['chunk_text'].apply(lambda x: len(str(x).split()))

# Group by document and compute summary statistics
summary = df.groupby('document_name').agg(
    doc_word_count=('chunk_word_count', 'sum'),
    number_of_chunks=('chunk_number', 'count'),
    mean_chunk_size=('chunk_word_count', 'mean'),
    chunk_size_standard_deviation=('chunk_word_count', 'std')
).reset_index()

# Save to CSV
summary.to_csv(output_path, index=False)

print(f"Summary saved to {output_path}")