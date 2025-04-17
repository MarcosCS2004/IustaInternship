import csv
import requests
import os
from datetime import datetime

# === LOGGING SETUP ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "run_log.txt")

def log_message(message):
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

# Function to check if a link is valid
def check_link(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
    except requests.RequestException as e:
        log_message(f"Error with {url}: {e}")
        return False

def main():
    csv_file = input("📄 Enter the path to the CSV file: ").strip('"').strip()
    field_name = input("🔍 Enter the name of the column containing the links: ").strip()

    if not os.path.isfile(csv_file):
        print(f"❌ Error: The file '{csv_file}' was not found.")
        return

    try:
        valid_rows = []
        invalid_rows = []

        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames

            if field_name not in headers:
                print(f"❌ Error: The column '{field_name}' does not exist in the CSV.")
                return

            total = 0
            for index, row in enumerate(reader, start=2):  # Line 2 = first row after header
                url = row[field_name].strip()
                if not url:
                    continue
                total += 1
                print(f"🔍 Checking line {index}: {url}")
                if check_link(url):
                    valid_rows.append(row)
                else:
                    invalid_rows.append(row)
                    log_message(f"Invalid link at line {index}: {url}")

        # Save valid rows
        if valid_rows:
            with open('valid_links.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(valid_rows)
            print(f"\n✅ {len(valid_rows)} valid links saved to 'valid_links.csv'.")

        # Save invalid rows
        if invalid_rows:
            with open('invalid_links.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(invalid_rows)
            print(f"⚠️ {len(invalid_rows)} invalid links saved to 'invalid_links.csv'.")
            print("📄 See detailed log in 'logs/run_log.txt'.")

        # Final summary
        print("\n📊 Summary:")
        print(f"   Lines processed:  {total}")
        print(f"   Valid links:      {len(valid_rows)}")
        print(f"   Invalid links:    {len(invalid_rows)}")

    except Exception as e:
        print(f"🚨 Unexpected error: {e}")
        log_message(f"Unhandled error: {e}")

if __name__ == "__main__":
    main()
