import pandas as pd  # For reading and writing CSV files
import requests  # To fetch webpage content
from bs4 import BeautifulSoup  # For parsing HTML
import re  # For regex operations like email detection
import time  # To pause between requests

# Function to determine if the page contains relevant legal or contact information
def contains_relevant_info(text):
    text = text.lower()  # Normalize text for keyword checks

    # Check for presence of an email address
    has_email = re.search(r"\b[\w.-]+?@\w+?\.\w+?\b", text)

    # Address-related keywords (only in English and German)
    address_keywords = [
        "address", "street", "avenue",  # English
        "adresse", "straße", "strasse", "platz", "hausnummer"  # German
    ]

    # Legal-related name keywords (only in English and German)
    name_keywords = [
        "law firm", "attorney", "law office",  # English
        "anwalt", "rechtsanwalt", "kanzlei", "jurist"  # German
    ]

    # Check if address or name keywords are present
    has_address = any(keyword in text for keyword in address_keywords)
    has_name = any(keyword in text for keyword in name_keywords)

    return has_email or has_address or has_name

# Main function to process links from a CSV file
def analyze_links(csv_path, link_column, output_csv):
    try:
        # Load input CSV
        df = pd.read_csv(csv_path)

        # Check that the specified link column exists
        if link_column not in df.columns:
            print(f"❌ Column '{link_column}' not found in CSV.")
            return

        filtered_links = []  # Will store relevant URLs

        # Process each URL one by one
        for index, row in df.iterrows():
            url = row[link_column]
            try:
                print(f"Visiting: {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    text = soup.get_text(separator=" ", strip=True)

                    # Check if the content is relevant
                    if contains_relevant_info(text):
                        filtered_links.append({"url": url})
            except Exception as e:
                print(f"⚠️ Error with {url}: {e}")

            time.sleep(1)  # Delay between requests

        # Save results to new CSV
        result_df = pd.DataFrame(filtered_links)
        result_df.to_csv(output_csv, index=False)
        print(f"\n✅ Analysis complete. {len(result_df)} links with relevant information saved to '{output_csv}'.")

    except Exception as e:
        print(f"❌ Error processing CSV: {e}")

# Interactive script entry point
if __name__ == "__main__":
    print("== Link Relevance Analyzer ==")
    csv_path = input("Enter the path to your input CSV file: ").strip()
    link_column = input("Enter the name of the column with the links: ").strip()
    output_csv = input("Enter the name for the output CSV file: ").strip()

    analyze_links(csv_path, link_column, output_csv)
