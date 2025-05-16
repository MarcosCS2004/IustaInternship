import pandas as pd
import json
from unidecode import unidecode
from rapidfuzz import fuzz
import re

# --- Load multiple JSON files ---
json_paths = input("📄 Enter the paths to JSON files (comma-separated): ").strip().split(",")
combined_objects = []
json_row_origins = []

for file_idx, path in enumerate(json_paths, start=1):
    path = path.strip()
    try:
        with open(path, encoding='utf-8') as f:
            json_data = json.load(f)

        extracted = []
        if isinstance(json_data, list) and isinstance(json_data[0], list) and isinstance(json_data[0][1], list):
            for pair in json_data:
                if isinstance(pair, list) and len(pair) == 2 and isinstance(pair[1], list):
                    extracted.extend(pair[1])
        else:
            extracted.extend(json_data if isinstance(json_data, list) else [json_data])

        for i, obj in enumerate(extracted):
            combined_objects.append(obj)
            safe_id = obj.get("safeId")
            json_row_origins.append({
                "safeId": safe_id,
                "row_number": i + 1,
                "file_number": file_idx
            })
    except Exception as e:
        print(f"⚠️ Could not load JSON from {path}: {e}")

if not combined_objects:
    print("❌ No valid JSON objects found. Exiting.")
    exit(1)

json_df = pd.DataFrame(combined_objects)

# --- Ask which field to save ---
print("\n📋 Available fields in JSON:")
for key in json_df.columns:
    print(f" - {key}")
json_field_to_save = input("\n🔑 Which field from the JSON should be saved in the new column?: ").strip()

if json_field_to_save not in json_df.columns:
    print(f"\n❌ Error: Field '{json_field_to_save}' not found in the JSON.")
    exit(1)

# --- Load CSV ---
csv_path = input("\n📄 Enter the path to the main CSV file: ").strip()
header_row = int(input("🔢 Which row contains the header in the CSV? (0-based index): ").strip())

with open(csv_path, encoding='utf-8') as f:
    first_line = f.readline().strip()

df = pd.read_csv(csv_path, header=header_row, dtype=str)

# --- Ask if the CSV has a unique ID column ---
id_column_exists = input("\n❓ Does your CSV have a unique ID column? (yes/no): ").strip().lower()

if id_column_exists == "yes":
    print("\n🆔 Available columns in the CSV:")
    for col in df.columns:
        print(f" - {col}")
    id_column = input("\n🔑 Enter the name of the column that contains the unique ID: ").strip()

    if id_column not in df.columns:
        print(f"❌ Error: ID column '{id_column}' not found in the CSV.")
        exit(1)
else:
    print("\n❗ No unique ID column found. Any duplicates will be marked in logs.")

# --- Ask for new column name ---
new_column_name = input("\n📦 What should be the name of the new column to add?: ").strip()
if new_column_name not in df.columns:
    df[new_column_name] = ""
else:
    df[new_column_name] = df[new_column_name].astype("object")

if "logs" not in df.columns:
    df["logs"] = ""
else:
    df["logs"] = df["logs"].astype(str)

# --- Define field mapping ---
print("\n🧩 Define the mapping between CSV and JSON fields (format: csvField:jsonField, separated by commas).")
print("📌 Example: straße:streetName, hausnummer:houseNumber, ort:city\n")
mapping_input = input("Enter field mapping: ").strip()
field_mapping = {}

for pair in mapping_input.split(","):
    if ":" not in pair:
        continue
    csv_field, json_field = map(str.strip, pair.split(":"))
    if csv_field not in df.columns:
        print(f"⚠️ CSV field '{csv_field}' not found. Skipping.")
        continue
    if json_field not in json_df.columns:
        print(f"⚠️ JSON field '{json_field}' not found. Skipping.")
        continue
    field_mapping[csv_field] = json_field

if not field_mapping:
    print("❌ No valid field mappings defined. Exiting.")
    exit(1)

print("\n🧠 Matching dictionary defined:")
print(field_mapping)

# --- Normalize relevant columns in both dataframes ---
def normalize(text):
    if pd.isna(text):
        return ""
    text = unidecode(str(text)).lower().strip()
    text = re.sub(r"\s*-\s*", "-", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\d+)\s*-\s*(\d+)", r"\1-\2", text)

    substitutions = {
        r"\bstrasse\b": "strasse",
        r"\bstr\.\b": "strasse",
        r"\bstr\b": "strasse",
        r"\bstraße\b": "strasse",
        r"\bmommsenstr\b": "mommsenstrasse",
        r"\bpl\.\b": "platz",
        r"\bpl\b": "platz",
        r"\bal\.\b": "allee",
        r"\bal\b": "allee",
        r"\bbahnhofstrasse\b": "bahnhofstrasse",
        r"\bbahnhofstraße\b": "bahnhofstrasse",
        r"\bbahnhofstr\.\b": "bahnhofstrasse",
        r"\bbahnhofstr\b": "bahnhofstrasse"
    }
    for pattern, replacement in substitutions.items():
        text = re.sub(pattern, replacement, text)
    text = re.sub(r"[.,]", "", text)
    return text

for csv_col, json_col in field_mapping.items():
    df[f"_norm_{csv_col}"] = df[csv_col].apply(normalize)
    json_df[f"_norm_{json_col}"] = json_df[json_col].apply(normalize)

output_file = input("\n💾 Enter the name of the output file (include extension .csv or .json): ").strip()

# --- Check file extension to determine format ---
if not output_file.endswith(('.csv', '.json')):
    print("⚠️ Invalid file extension. Please use .csv or .json.")
    exit(1)

# --- Match function ---
def find_matches(row):
    matches = []
    for j_idx, jrow in json_df.iterrows():
        match_count = 0
        matched_fields = []
        mismatched_fields = []
        for csv_col, json_col in field_mapping.items():
            csv_val = row.get(f"_norm_{csv_col}", "")
            json_val = jrow.get(f"_norm_{json_col}", "")
            score = fuzz.token_sort_ratio(csv_val, json_val)

            if score >= 85:
                matched_fields.append(csv_col)
                match_count += 1
            else:
                mismatched_fields.append(csv_col)
        if len(field_mapping) > 0 and match_count > 0:
            origin = next((o for o in json_row_origins if o["safeId"] == jrow.get("safeId")), None)
            matches.append({
                "jrow": jrow,
                "matched_fields": matched_fields,
                "mismatched_fields": mismatched_fields,
                "file_number": origin["file_number"] if origin else "?",
                "row_number": origin["row_number"] if origin else "?"
            })
    return matches

# --- Create 'MultipleMatches' column if needed ---
if "MultipleMatches" not in df.columns:
    df["MultipleMatches"] = ""

# --- Process rows ---
print("\n🔍 Matching CSV... Please wait.")
matched_count = 0
row_hashes = {}
duplicate_map = {}

for idx, row in df.iterrows():
    hashable = tuple(row.get(col, "") for col in field_mapping.keys())
    log_entries = []

    is_duplicate = False

    if hashable in row_hashes:
        duplicate_idx = row_hashes[hashable]
        if id_column_exists == "yes":
            duplicate_id = df.at[duplicate_idx, id_column]
            df.at[idx, new_column_name] = df.at[duplicate_idx, new_column_name]
            log_entries.append(f"duplicate of id {duplicate_id}")
        else:
            log_entries.append(f"duplicate found in row {duplicate_idx} (no ID column)")
        is_duplicate = True

        existing_log = str(df.at[duplicate_idx, "logs"])
        new_log_entry = f"duplicate of id {df.at[idx, id_column]}" if id_column_exists == "yes" else "duplicate found"
        if "duplicate" not in existing_log.lower():
            if existing_log:
                df.at[duplicate_idx, "logs"] = f"{existing_log}, {new_log_entry}"
            else:
                df.at[duplicate_idx, "logs"] = new_log_entry
    else:
        row_hashes[hashable] = idx

    matches = find_matches(row)

    if not matches:
        log_entries.append("not match")
    else:
        exact = [m for m in matches if len(m["matched_fields"]) == len(field_mapping)]
        partial = [m for m in matches if m["matched_fields"] and m["mismatched_fields"]]

        if len(exact) == 1:
            match = exact[0]
            value = match["jrow"].get(json_field_to_save)
            df.at[idx, new_column_name] = value
            log_entries.append(f"exact match from file {match['file_number']}")
            matched_count += 1
        elif len(exact) > 1:
            file_counts = {}
            for m in exact:
                file_counts[m['file_number']] = file_counts.get(m['file_number'], 0) + 1
            sources = []
            for file_num, count in file_counts.items():
                if count > 1:
                    sources.append(f"file {file_num} ({count} matches)")
                else:
                    sources.append(f"file {file_num}")
            # Collect multiple match values
            safe_ids = [m["jrow"].get(json_field_to_save, "") for m in exact if m["jrow"].get(json_field_to_save)]
            df.at[idx, "MultipleMatches"] = ", ".join(safe_ids)
            log_entries.append(f"{len(exact)} matches exact: {', '.join(sources)}")
        elif partial:
            best = max(partial, key=lambda x: len(x["matched_fields"]))
            fields = ", ".join(best["matched_fields"])
            log_entries.append(f"only [{fields}] from file {best['file_number']}")
        else:
            log_entries.append("not match")

    df.at[idx, "logs"] = ", ".join(log_entries)

# --- Drop temporary normalized columns before saving ---
temp_cols = [col for col in df.columns if col.startswith("_norm_")]
df.drop(columns=temp_cols, inplace=True)

# --- Save output based on file extension ---
if output_file.endswith('.csv'):
    with open(csv_path, encoding='utf-8') as f:
        first_line = f.readline().strip()

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        if first_line:
            f.write(first_line + "\n")
        df.to_csv(f, index=False, header=True)
elif output_file.endswith('.json'):
    df.to_json(output_file, orient="records", force_ascii=False, indent=2)

print(f"\n✅ Done. Exact matches added: {matched_count}/{len(df)} rows.")
print(f"📤 Output saved to: {output_file}")
