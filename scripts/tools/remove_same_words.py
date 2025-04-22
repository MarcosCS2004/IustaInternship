import pandas as pd
import re

def clean_csv():
    # User inputs
    file_name = input("Enter the CSV file name (including '.csv'): ")
    column_name = input("Enter the column name to filter: ")
    phrase_to_remove = input("Enter the phrase to remove (rows containing it will be deleted): ")
    output_file = input("Enter the name for the cleaned output file (including '.csv'): ")

    try:
        # Read the CSV file
        df = pd.read_csv(file_name)

        # Check if the column exists
        if column_name not in df.columns:
            print(f"Column '{column_name}' does not exist in the file.")
            return

        # Compile the regex pattern (case insensitive)
        pattern = re.compile(re.escape(phrase_to_remove), re.IGNORECASE)

        # Filter rows where the column does NOT contain the phrase
        filtered_df = df[~df[column_name].astype(str).str.contains(pattern)]

        # Save the cleaned CSV
        filtered_df.to_csv(output_file, index=False)
        print(f"✅ Cleaned file saved as '{output_file}' with {len(filtered_df)} rows.")
    
    except FileNotFoundError:
        print(f"❌ File '{file_name}' not found.")
    except Exception as e:
        print(f"⚠️ An error occurred: {e}")

if __name__ == "__main__":
    clean_csv()
