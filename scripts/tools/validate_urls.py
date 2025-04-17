import csv
import requests
import os
from datetime import datetime

# === LOGGING SETUP ===
# Get the root directory of the project (where main.py is)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "run_log.txt")

# Function to write log messages
def log_message(message):
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

# Function to validate URLs
def check_links(url_list):
    valid_links = []
    invalid_links = []

    for url in url_list:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code == 200:
                valid_links.append(url)
            else:
                log_message(f"Invalid link: {url} - Status code: {response.status_code}")
                invalid_links.append(url)
        except requests.RequestException as e:
            log_message(f"Error with {url}: {e}")
            invalid_links.append(url)

    return valid_links, invalid_links

# Main function
def main():
    csv_file = input("Enter the path to the CSV file: ").strip('"').strip()
    field_name = input("Enter the name of the column containing the URLs: ").strip()

    if not os.path.isfile(csv_file):
        print(f"❌ Error: The file '{csv_file}' was not found.")
        return

    try:
        with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            if field_name not in reader.fieldnames:
                print(f"❌ Error: The column '{field_name}' does not exist in the CSV.")
                return

            url_list = [row[field_name] for row in reader if row[field_name].strip()]

        valid_links, invalid_links = check_links(url_list)

        if valid_links:
            with open('valid_links.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([field_name])
                for link in valid_links:
                    writer.writerow([link])
            print(f"✅ Valid links saved to 'valid_links.csv'.")
        else:
            print("No valid links found.")

        if invalid_links:
            with open('invalid_links.csv', mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([field_name])
                for link in invalid_links:
                    writer.writerow([link])
            print(f"⚠️ {len(invalid_links)} invalid links saved to 'invalid_links.csv'.")
            print("See detailed log in 'logs/run_log.txt'.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        log_message(f"Unhandled error: {e}")

# Entry point
if __name__ == "__main__":
    main()
