import pandas as pd  # For reading and writing CSV files
import requests  # To make HTTP requests
from bs4 import BeautifulSoup  # For parsing and extracting text from HTML
import time  # For adding delays between requests

if __name__ == "__main__":
    print("== Keyword Link Filter ==")

    # Ask user for input values
    input_csv = input("Enter the path to your input CSV file: ").strip()
    column_name = input("Enter the name of the column containing the URLs: ").strip()
    output_csv = input("Enter the name for the output CSV file: ").strip()
    keyword_input = input("Enter keywords to search for (separated by commas): ").strip()

    # Process keywords (e.g. ["markenrecht", "verkehrsrecht"])
    keywords = [k.strip().lower() for k in keyword_input.split(",") if k.strip()]
    if not keywords:
        print("❌ No keywords provided. Exiting.")
        exit()

    try:
        # Read the input CSV file
        df = pd.read_csv(input_csv, encoding="utf-8", quoting=1)
        if column_name not in df.columns:
            print(f"❌ Column '{column_name}' not found in CSV.")
            exit()

        urls = df[column_name].dropna().unique()  # Get unique, non-null URLs
        filtered_results = []  # Store URLs that match keywords

        # Headers to mimic a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Visit each URL and search for keywords
        for url in urls:
            try:
                print(f"Visiting: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    page_text = soup.get_text(separator=" ", strip=True).lower()
                    if any(keyword in page_text for keyword in keywords):
                        filtered_results.append(url)
                else:
                    print(f"⚠️ Error accessing {url} (status code {response.status_code})")
            except Exception as e:
                print(f"⚠️ Failed to access {url}: {e}")
            time.sleep(1)  # Sleep to avoid overwhelming servers

        # Save the matching URLs to the output file
        with open(output_csv, "w", encoding="utf-8") as f:
            f.write(f"{column_name}\n")
            for url in filtered_results:
                f.write(f"{url}\n")

        print(f"\n✅ Process completed. {len(filtered_results)} matching links saved to '{output_csv}'.")

    except Exception as e:
        print(f"❌ Error during processing: {e}")
