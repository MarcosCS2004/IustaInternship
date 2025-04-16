import pandas as pd
import os
from datetime import datetime

def split_csv_by_category(input_file, output_folder="categorized_results", category_column="type"):
    """
    Splits a CSV file into multiple files based on categories found in a specified column.

    Args:
        input_file (str): Path to input CSV file
        output_folder (str): Folder to store output files
        category_column (str): Name of the column containing categories
    """
    try:
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Read input CSV
        df = pd.read_csv(input_file)

        # Verify the category column exists
        if category_column not in df.columns:
            raise ValueError(f"Input CSV must contain a column named '{category_column}' with categories")

        # Get unique categories
        categories = df[category_column].unique()
        print(f"Found {len(categories)} categories: {', '.join(map(str, categories))}")

        # Create one CSV file per category
        created_files = []
        for category in categories:
            # Filter data by category
            category_df = df[df[category_column] == category]

            # Create valid filename (replace special characters)
            safe_category_name = "".join(c if c.isalnum() else "_" for c in str(category))
            output_file = os.path.join(output_folder, f"{safe_category_name}.csv")

            # Save the file
            category_df.to_csv(output_file, index=False)
            created_files.append(output_file)

            print(f"Saved {len(category_df)} records to {output_file}")

        # Create summary file
        summary_file = os.path.join(output_folder, "_summary.txt")
        with open(summary_file, "w") as f:
            f.write(f"Category Analysis Summary\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source file: {input_file}\n")
            f.write(f"\nCategories found:\n")
            for cat in categories:
                count = len(df[df[category_column] == cat])
                f.write(f"- {cat}: {count} records\n")
            f.write(f"\nFiles created:\n")
            for file in created_files:
                f.write(f"- {file}\n")

        print(f"\n✅ Process completed. Created {len(created_files)} CSV files.")
        print(f"📝 Summary saved to: {summary_file}")

        return created_files

    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return None

if __name__ == "__main__":
    # Interactive configuration via input
    print("== CSV Splitter by Category ==")
    input_csv = input("Enter the path to your input CSV file: ").strip()
    category_column = input("Enter the name of the column with categories: ").strip()
    output_folder = input("Enter the name of the folder for the output files: ").strip()

    # Execute the function
    split_csv_by_category(
        input_file=input_csv,
        output_folder=output_folder,
        category_column=category_column,
    )
