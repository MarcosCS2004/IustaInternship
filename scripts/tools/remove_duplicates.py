import pandas as pd
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(100000))
        return result['encoding']

def main():
    # Ask user for input CSV
    input_file = input("Enter the path to the CSV file: ").strip()

    try:
        encoding = detect_encoding(input_file)
        print(f"Detected encoding: {encoding}")
    except Exception as e:
        print(f"Error detecting encoding: {e}")
        return

    # Read CSV
    try:
        df = pd.read_csv(input_file, encoding=encoding)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return

    # Display available columns
    print("\nAvailable columns:")
    print(df.columns.tolist())

    # Ask user which column to check
    column_name = input("\nEnter the column name to check for duplicates: ").strip()

    if column_name not in df.columns:
        print(f"Column '{column_name}' not found in the CSV.")
        return

    # Clean whitespace around values
    df[column_name] = df[column_name].astype(str).str.strip()

    # Check for duplicates
    duplicates = df.duplicated(subset=[column_name])
    num_duplicates = duplicates.sum()

    if num_duplicates == 0:
        print(f"\n✅ No duplicates found in column '{column_name}'.")
    else:
        print(f"\n⚠️ Found {num_duplicates} duplicate row(s) based on column '{column_name}'.")

    # Drop duplicates
    df_cleaned = df.drop_duplicates(subset=[column_name])

    # Ask for output filename
    output_file = input("\nEnter the name for the new CSV file (e.g., cleaned.csv): ").strip()

    try:
        df_cleaned.to_csv(output_file, index=False, encoding=encoding)
        print(f"✅ Cleaned CSV saved as '{output_file}'.")
    except Exception as e:
        print(f"Error saving the cleaned file: {e}")

if __name__ == "__main__":
    main()
