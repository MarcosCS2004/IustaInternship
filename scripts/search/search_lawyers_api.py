from serpapi import GoogleSearch
import csv

# Your SerpAPI key
API_KEY = ""

# Ask the user for search input
query = input("What type of law firm are you looking for?: ")

# Ask the user for the minimum number of results
min_results = int(input("What is the minimum number of results you want?: "))

# Set location to Germany for national search
location = "Germany"

# Search parameters
params = {
    "engine": "google",
    "q": f"{query} in {location}",
    "api_key": API_KEY,
    "location": location,
    "hl": "de",  # German results
    "gl": "de",
    "start": 0,
}

# Track seen links to avoid duplicates
seen_links = set()

# Prepare the filename
filename = f"links_{query.replace(' ', '_')}.csv"

# Open CSV to write only links
with open(filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Link"])  # Just the links

    total_links = 0
    page = 0

    while total_links < min_results:
        params["start"] = page
        search = GoogleSearch(params)
        results = search.get_dict()
        items = results.get("organic_results", [])

        for item in items:
            link = item.get("link", "")
            if link and link not in seen_links:
                seen_links.add(link)
                writer.writerow([link])
                print(link)  # Show the link in console
                total_links += 1

        page += 10

print(f"\nSearch completed! {total_links} links saved to '{filename}'")
