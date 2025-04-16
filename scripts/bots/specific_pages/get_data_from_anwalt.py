from playwright.sync_api import sync_playwright
import csv
import time
import random
import os

# Ask user for input/output file and column names
input_csv = input("Enter the name of the input CSV file (e.g., data.csv): ").strip()
output_csv = input("Enter the name for the output CSV file (e.g., results.csv): ").strip()
link_column = input("Enter the column name containing the lawyer profile links: ").strip()
specialty_column = input("Enter the column name containing the lawfields: ").strip()

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False, slow_mo=100)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        viewport={"width": 1280, "height": 720},
    )
    page = context.new_page()

    # Check if output file already exists to avoid rewriting the header
    file_exists = os.path.isfile(output_csv)

    with open(output_csv, 'a', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file)
        if not file_exists:
            writer.writerow(['Name', 'Address', 'LinkedIn', 'Website', 'Email', 'Lawyers', 'Lawfields'])

        try:
            with open(input_csv, 'r', encoding='utf-8') as input_file:
                reader = csv.DictReader(input_file)
                for row in reader:
                    url = row.get(link_column, '').strip()
                    lawfields = row.get(specialty_column, 'No specialties provided').strip()

                    if not url:
                        print("⚠️ Skipping row with missing URL.")
                        continue

                    print(f"Visiting: {url}")

                    try:
                        page.goto(url, timeout=60000)
                        page.wait_for_selector("main", timeout=30000)
                        page.wait_for_timeout(random.randint(2000, 4000))

                        page.mouse.wheel(0, 1000)
                        page.wait_for_timeout(random.randint(1000, 2000))

                        name_element = page.query_selector('h1.text-lg.font-bold.mb-0')
                        name = name_element.inner_text().strip() if name_element else "No name found"

                        address_element = page.query_selector('button.text-sm\\/\\[22px\\].text-info-500.font-semibold')
                        address = address_element.inner_text().strip() if address_element else "No address found"

                        linkedin_element = page.query_selector('a.anw-social-media-linkedin')
                        linkedin = linkedin_element.get_attribute("href") if linkedin_element else "No LinkedIn link"

                        website_element = page.query_selector('a.flex.items-center.gap-1')
                        website = website_element.get_attribute("href") if website_element else "No website"

                        email_element = page.query_selector('span.mr-1')
                        email = email_element.inner_text().strip() if email_element and "@" in email_element.inner_text() else "No email"

                        lawyer_elements = page.query_selector_all('a.anw-default.text-sm\\/\\[22px\\].font-semibold')
                        seen = set()
                        lawyers = []
                        for el in lawyer_elements:
                            name_text = el.inner_text().replace("Link in einem neuen Tab öffnen", "").strip()
                            if name_text and name_text not in seen:
                                seen.add(name_text)
                                lawyers.append(name_text)

                        lawyers_info = "; ".join(lawyers)

                        writer.writerow([name, address, linkedin, website, email, lawyers_info, lawfields])
                        print(f"✅ Saved: {name} with {len(lawyers)} lawyer(s)")

                        time.sleep(random.uniform(4, 7))

                    except Exception as e:
                        print(f"❌ Error visiting {url}: {e}")
                        page.screenshot(path=f"error_{int(time.time())}.png")

        except FileNotFoundError:
            print(f"❌ File '{input_csv}' not found. Please check the path and try again.")

    browser.close()
    print(f"✔️ Done. Results saved to '{output_csv}'")
