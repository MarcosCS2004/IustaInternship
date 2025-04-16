import csv
import re
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

def extract_info_from_content(content, text_content):
    """
    Extracts useful information like company name, emails, phones, addresses, 
    CEO names, and LinkedIn profiles from the webpage content.
    """
    # Extract emails
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content)
    
    # Extract phone numbers
    phones = re.findall(r"\+?\d[\d\-\(\) ]{7,}\d", text_content)

    # Extract the company name from the title tag
    title = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    company_name = title.group(1).strip() if title else "Not found"

    # Attempt to extract CEO information using a regex
    ceo_match = re.findall(
        r"(Mr\.|Ms\.|Dr\.|Prof\.)?\s?[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s?\(?((CEO|Chief Executive|Managing Partner|Founder|Managing Director)[^)]+)?\)?",
        text_content,
    )
    ceo_candidates = [" ".join(filter(None, match)).strip() for match in ceo_match]
    ceo_candidates = list(
        set(
            [
                name
                for name in ceo_candidates
                if any(
                    title in name
                    for title in ["CEO", "Founder", "Managing", "Director"]
                )
            ]
        )
    )

    # Extract addresses using a regex pattern
    address_pattern = re.compile(r"\d{5}\s[A-Za-zäöüÄÖÜß\-\s]+")
    addresses = address_pattern.findall(text_content)

    # Extract LinkedIn profiles
    linkedin_links = re.findall(
        r"https://[a-z]+\.linkedin\.com/(in|company)/[a-zA-Z0-9\-_%]+", content
    )
    linkedin_links = list(
        set(
            [
                "https://" + match[0] + ".linkedin.com/" + match[1]
                for match in linkedin_links
            ]
        )
    )

    return {
        "company_name": company_name,
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "addresses": list(set(addresses)),
        "ceo_candidates": ceo_candidates,
        "linkedin_profiles": linkedin_links,
    }


def crawl_links_from_csv(csv_file, output_file):
    """
    Crawls URLs from the input CSV file, extracts relevant data, 
    and saves the data into an output CSV file.
    """
    data_rows = []

    # Read the input CSV to extract the URLs
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        urls = [row["Link"] for row in reader if row.get("Link")]

    # Use Playwright to visit the URLs and extract information
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for url in urls:
            try:
                print(f"Crawling: {url}")
                page.goto(url, timeout=15000)
                content = page.content()
                text_content = page.inner_text("body")
                info = extract_info_from_content(content, text_content)

                # Prepare the data for writing to the output CSV
                row = {
                    "source_url": url,
                    "company_name": info["company_name"],
                    "emails": "; ".join(info["emails"]),
                    "phones": "; ".join(info["phones"]),
                    "addresses": "; ".join(info["addresses"]),
                    "ceo_candidates": "; ".join(info["ceo_candidates"]),
                    "linkedin_profiles": "; ".join(info["linkedin_profiles"]),
                }
                data_rows.append(row)

            except Exception as e:
                print(f"Error visiting {url}: {e}")
                continue

        browser.close()

    # Write the extracted data to the output CSV file
    fieldnames = [
        "source_url",
        "company_name",
        "emails",
        "phones",
        "addresses",
        "ceo_candidates",
        "linkedin_profiles",
    ]
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)

    print(f"\n✅ Data saved to {output_file}")


def main():
    """
    Main function to ask the user for input and output file paths, 
    and crawl the URLs from the input CSV file.
    """
    # Ask the user for input parameters
    input_file = input("Enter the input CSV file path (e.g., 'links_Markenrecht.csv'): ").strip()
    url_column = input("Enter the name of the column containing the URLs (e.g., 'Link'): ").strip()
    output_file = input("Enter the output CSV file path (e.g., 'web_data_output.csv'): ").strip()

    # Read URLs from the input CSV
    urls = []

    try:
        with open(input_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Ensure the specified URL column exists and is not empty
                if url_column in row and row[url_column].strip():
                    urls.append(row[url_column].strip())

        # Process all the collected URLs
        crawl_links_from_csv(input_file, output_file)
        print(f"✅ The file has been processed and saved as '{output_file}'")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' could not be found.")
    except Exception as e:
        print(f"Error processing the file: {e}")


if __name__ == "__main__":
    main()
