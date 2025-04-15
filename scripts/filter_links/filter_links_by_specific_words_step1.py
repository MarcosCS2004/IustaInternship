import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Input and output file names
input_csv = "links_Verkehrsrecht.csv"
output_csv = "filtered_links_Verkehrsrecht_v2.csv"  # Output file

# Keywords related to the topics you're interested in
keywords = ["markenrecht", "verkehrsrecht"]

# Read the CSV file with proper encoding and quoting
df = pd.read_csv(input_csv, encoding="utf-8", quoting=1)
column_name = "Link"  # Update this if your column has a different name
urls = df[column_name].dropna().unique()

# List to store the filtered results
filtered_results = []

# Headers to mimic a browser and avoid blocking
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Loop through each URL and scrape the content
for url in urls:
    try:
        print(f"Visiting: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True).lower()
            # Check if any of the keywords are in the page content
            if any(keyword in page_text for keyword in keywords):
                filtered_results.append(url)
        else:
            print(f"Error accessing {url} (status code {response.status_code})")
    except Exception as e:
        print(f"Failed to access {url}: {e}")

    time.sleep(1)  # Pause to avoid overwhelming the sites

# Save filtered URLs to a new CSV (without quotes around the URLs)
with open(output_csv, "w", encoding="utf-8") as f:
    f.write("Link\n")  # Write header
    for url in filtered_results:
        f.write(f"{url}\n")  # Write each URL without quotes

print(
    f"\n✅ Process completed. {len(filtered_results)} links containing the keywords were saved."
)
