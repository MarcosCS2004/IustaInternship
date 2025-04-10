import csv
import re
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

input_file = "links_Markenrecht.csv"
output_file = "web_data_output.csv"

def extract_info_from_content(content, text_content):
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content)
    phones = re.findall(r"\+?\d[\d\-\(\) ]{7,}\d", text_content)

    title = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
    company_name = title.group(1).strip() if title else "Not found"

    ceo_match = re.findall(r"(Mr\.|Ms\.|Dr\.|Prof\.)?\s?[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s?\(?((CEO|Chief Executive|Managing Partner|Founder|Managing Director)[^)]+)?\)?", text_content)
    ceo_candidates = [" ".join(filter(None, match)).strip() for match in ceo_match]
    ceo_candidates = list(set([name for name in ceo_candidates if any(title in name for title in ["CEO", "Founder", "Managing", "Director"])]))

    address_pattern = re.compile(r"\d{5}\s[A-Za-zäöüÄÖÜß\-\s]+")
    addresses = address_pattern.findall(text_content)

    linkedin_links = re.findall(r"https://[a-z]+\.linkedin\.com/(in|company)/[a-zA-Z0-9\-_%]+", content)
    linkedin_links = list(set(["https://" + match[0] + ".linkedin.com/" + match[1] for match in linkedin_links]))

    return {
        "company_name": company_name,
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "addresses": list(set(addresses)),
        "ceo_candidates": ceo_candidates,
        "linkedin_profiles": linkedin_links,
    }

def crawl_links_from_csv(csv_file, output_file):
    data_rows = []

    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        urls = [row["Link"] for row in reader if row.get("Link")]

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

                row = {
                    "source_url": url,
                    "company_name": info["company_name"],
                    "emails": "; ".join(info["emails"]),
                    "phones": "; ".join(info["phones"]),
                    "addresses": "; ".join(info["addresses"]),
                    "ceo_candidates": "; ".join(info["ceo_candidates"]),
                    "linkedin_profiles": "; ".join(info["linkedin_profiles"])
                }
                data_rows.append(row)

            except Exception as e:
                print(f"Error visiting {url}: {e}")
                continue

        browser.close()

    fieldnames = ["source_url", "company_name", "emails", "phones", "addresses", "ceo_candidates", "linkedin_profiles"]
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)

    print(f"\n✅ Data saved to {output_file}")

# Ejecutar el script
crawl_links_from_csv(input_file, output_file)
