import pandas as pd
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="")

# Define constructs and their definitions
constructs = {
    "National Identification": "An emotional investment in, and positive attachment to, one’s national group.",
    "Patriotism": "A positive feeling of attachment to, and pride about, one’s country.",
    "National Narcissism": "A belief that one’s nation is exceptional but not sufficiently appreciated by others and is entitled to special privileges and deserves special treatment.",
    "Nationalism": "A belief that one’s country is superior to other countries and should dominate in international relations."
}

def extract_yes_no(text):
    return 1 if text.strip().lower().startswith("yes") else 0

def build_messages(construct, definition, chunk_text):
    return [{"role": "user", "content": f"""{construct}: {definition}
Does this text express {construct}?
Respond only with yes or no.
Text: {chunk_text}"""}]

def call_openai(row_index, construct, definition, chunk_text):
    try:
        messages = build_messages(construct, definition, chunk_text)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0
        )
        result = extract_yes_no(response.choices[0].message.content)
        return row_index, result
    except Exception as e:
        print(f"Error on row {row_index}: {e}")
        return row_index, None

def process_construct_parallel(df, construct, definition, output_file, max_workers=5):
    if construct not in df.columns:
        df[construct] = None

    print(f"\n⏳ Processing '{construct}'...")
    rows_to_process = df[df[construct].isna()]
    save_interval = 1000
    call_counter = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(call_openai, i, construct, definition, row["chunk_text"]): i
            for i, row in rows_to_process.iterrows()
        }

        for future in tqdm(as_completed(futures), total=len(futures)):
            idx, result = future.result()
            df.at[idx, construct] = result
            call_counter += 1

            if call_counter % save_interval == 0:
                print(f"💾 Saving after {call_counter} calls...")
                df.to_csv(output_file, index=False)

    print(f"✅ Finished '{construct}'. Saving final result...")
    df.to_csv(output_file, index=False)
    return df

# --- Main Script ---

input_file = "/Users/user/programming/manifestos_and_identity/5_labelled/labelled.csv"
output_file = "/Users/user/programming/manifestos_and_identity/5_labelled/labelled.csv"

# Manually choose the construct to process here
# Options - "National Identification", "Patriotism", "National Narcissism", "Nationalism"
selected_construct = "Nationalism"  # <--- Change this as needed

df = pd.read_csv(input_file)

if selected_construct not in constructs:
    raise ValueError(f"'{selected_construct}' is not a valid construct. Choose from: {list(constructs.keys())}")

df = process_construct_parallel(df, selected_construct, constructs[selected_construct], output_file, max_workers=4)
df.to_csv(output_file, index=False)