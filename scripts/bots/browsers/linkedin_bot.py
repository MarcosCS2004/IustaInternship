import csv
import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import unquote, urlparse, parse_qs

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
]

BLACKLIST = ["jobs", "school", "pulse", "learning", "feed"]

def is_valid_linkedin_url(url):
    return (
        "linkedin.com/in" in url
        or "linkedin.com/company" in url
    ) and not is_blacklisted_linkedin_url(url)

def is_blacklisted_linkedin_url(url):
    return any(bad in url for bad in BLACKLIST)

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

            # Parse out the "uddg" parameter if it's a redirect link
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

# User input
input_file = input("Enter the path to your input CSV file: ").strip()
output_file_name = input("Enter the name for the output CSV file: ").strip()
column_name = input("Enter the name of the column that contains the law firm names: ").strip()

output_rows = []

try:
    with open(input_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        fieldnames = (
            reader.fieldnames + ["LinkedIn"]
            if "LinkedIn" not in reader.fieldnames
            else reader.fieldnames
        )

        for row in reader:
            name = row[column_name]
            query = f"LinkedIn {name}"
            print(f"🔎 Searching for: {query}")
            link = duckduckgo_first_result(query)

            if is_valid_linkedin_url(link):
                row["LinkedIn"] = link
                print("✅ LinkedIn link accepted.")
            else:
                row["LinkedIn"] = "Not found"
                print("❌ No valid LinkedIn link found.")

            output_rows.append(row)

    with open(output_file_name, mode="w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\n✅ Done! File saved as '{output_file_name}' with LinkedIn links.")

except Exception as e:
    print(f"General error: {e}")
