import csv
import os

def add_space_after_commas(input_file, output_file):
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as f_in:
            reader = csv.reader(f_in)
            modified_lines = []

            for row in reader:
                modified_line = ', '.join(row)
                modified_lines.append(modified_line)

        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line in modified_lines:
                f_out.write(line + '\n')

        print(f"✅ File successfully saved as '{output_file}'.")

    except FileNotFoundError:
        print(f"❌ Error: The file '{input_file}' does not exist.")
    except Exception as e:
        print(f"⚠️ An error occurred: {e}")

if __name__ == "__main__":
    input_path = input(" Enter the name of the input CSV file (e.g. data.csv): ").strip()
    output_path = input(" Enter the name of the output file (e.g. data_with_spaces.csv): ").strip()

    add_space_after_commas(input_path, output_path)
