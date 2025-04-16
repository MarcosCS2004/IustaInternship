import requests
from bs4 import BeautifulSoup
import csv
import time
import random

# Headers to simulate a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def extract_info_from_url(url):
    try:
        # Make the request to the URL
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Get the title of the site
        title = soup.title.string.strip() if soup.title else "not found"

        contact_link = "not found"
        linkedin_link = "not found"

        # Search through all anchor tags to find contact or LinkedIn links
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].lower()

            if "contact" in href or "contacto" in href or "kontakt" in href:
                if href.startswith("/") or not href.startswith("http"):
                    contact_link = url.rstrip("/") + href if not href.startswith("http") else href
                else:
                    contact_link = href

            if "linkedin.com" in href:
                linkedin_link = href

        return {"name": title, "contact link": contact_link, "linkedin": linkedin_link}

    except Exception as e:
        print(f"Error on {url}: {e}")
        return {
            "name": "not found",
            "contact link": "not found",
            "linkedin": "not found",
        }

def process_urls(url_list, output_file="output.csv"):
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "contact link", "linkedin"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Process each URL and extract the necessary information
        for url in url_list:
            info = extract_info_from_url(url)
            writer.writerow(info)
            print(f"Processed: {url}")
            time.sleep(random.uniform(1, 3))

def main():
    # Ask the user for input parameters
    input_file = input("Enter the input CSV file path (e.g., 'filtered_links_Markenrecht_v2.csv'): ").strip()
    url_column = input("Enter the name of the column containing the URLs (e.g., 'Link'): ").strip()
    output_file = input("Enter the output CSV file path (e.g., 'output.csv'): ").strip()

    # Read URLs from the CSV
    urls = []

    try:
        with open(input_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Ensure the specified URL column exists and is not empty
                if url_column in row and row[url_column].strip():
                    urls.append(row[url_column].strip())

        # Process all the collected URLs
        process_urls(urls, output_file)
        print(f"✅ The file has been processed and saved as '{output_file}'")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' could not be found.")
    except Exception as e:
        print(f"Error processing the file: {e}")

if __name__ == "__main__":
    main()
