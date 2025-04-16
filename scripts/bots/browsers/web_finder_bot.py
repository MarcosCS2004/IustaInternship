import csv
import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import (
    unquote,
    urlparse,
    parse_qs,
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
]

def duckduckgo_first_result(query):
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"

    try:
        time.sleep(random.uniform(1.5, 3.0))
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        results = soup.select("a.result__a")
        if results:
            link = results[0]["href"]

            # Parse and extract actual destination if it's a DuckDuckGo redirect
            parsed = urlparse(link)
            query_params = parse_qs(parsed.query)
            if "uddg" in query_params:
                real_url = unquote(query_params["uddg"][0])
                print(f"✅ Extracted real URL: {real_url}")
                return real_url
            else:
                print(f"✅ Direct URL: {link}")
                return link
        else:
            return ""
    except Exception as e:
        print(f"Error searching '{query}': {e}")
        return ""


# Asking user for input CSV file path, output CSV file name, and column name containing the company names
input_file = input("Enter the path to your input CSV file: ").strip()  # Ask for input CSV file
column_name = input("Enter the name of the column that contains the company names: ").strip()  # Ask for column name
output_file_name = input("Enter the name for the output CSV file: ").strip()  # Ask for output CSV file name

output_rows = []

try:
    with open(input_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        
        # Add 'Website' to the fieldnames if it's not already present
        fieldnames = (
            reader.fieldnames + ["Website"]
            if "Website" not in reader.fieldnames
            else reader.fieldnames
        )

        for row in reader:
            # Fetching the company name from the user-provided column
            name = row[column_name]
            query = f"{name} website"
            print(f"Searching for: {query}")
            link = duckduckgo_first_result(query)
            row["Website"] = link
            output_rows.append(row)

    # Write the updated data back to a new CSV file
    with open(output_file_name, mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"✅ File updated with website links and saved as '{output_file_name}'.")

except Exception as e:
    print(f"General error: {e}")
