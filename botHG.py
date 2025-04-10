import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import os
import re

# Function to load law firms from a text file

def load_law_firms_from_file(file_path="filtered_results.txt"):
    law_firms = []

    if not os.path.exists(file_path):
        print(f"⚠️ File '{file_path}' not found.")
        return law_firms

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(r"Name:\s*(.*?)\s*\|\s*URL:\s*(https?://\S+)", line.strip())
            if match:
                name, url = match.groups()
                law_firms.append({"name": name.strip(), "url": url.strip()})

    return law_firms
"""
law_firms = [
    {"name": "Schlun & Elseven Rechtsanwälte", "url": "https://www.hg.org/attorney/schlun-and-elseven-rechtsanwalte/119910"},
    {"name": "MTR Legal Rechtsanwälte", "url": "https://www.hg.org/attorney/mtr-legal-rechtsanwalte/168832"},
    {"name": "Dentons", "url": "https://www.hg.org/attorney/dentons/133970"},
    # Add more as needed
]
"""
async def scrape_firm_info(page, name, url):
    try:
        await page.goto(url)
        await page.wait_for_timeout(1000)  # wait 1 second in case of dynamic content

        # Address - primary method
        address_el = await page.query_selector(".profile-contact-address")
        address = await address_el.inner_text() if address_el else "N/A"

        # Fallback to span[itemprop="address"]
        if address == "N/A":
            fallback_address_el = await page.query_selector("div[itemprop='address']")
            address = await fallback_address_el.inner_text() if fallback_address_el else "N/A"

        # Phone number
        phone_el = await page.query_selector("a[href^='tel:']")
        phone = await phone_el.inner_text() if phone_el else "N/A"

        # External website
        links = await page.query_selector_all("a.bold")
        website = "N/A"
        for link in links:
            href = await link.get_attribute("href")
            if href and "hg.org" not in href:
                website = href
                break

        # Try to find CEO or similar title
        """
        ceo = "N/A"
        content = await page.content()
        ceo_keywords = ["CEO", "Chief Executive Officer", "Managing Partner", "Founder", "Director"]

        for keyword in ceo_keywords:
            if keyword.lower() in content.lower():
                ceo = keyword
                break
        """
        return {
            "Name": name,
            "Address": address.strip(),
            "Phone": phone.strip(),
            "Website": website
        }
    except Exception as e:
        print(f"Error with {name}: {e}")
        return {
            "Name": name,
            "Address": "Error",
            "Phone": "Error",
            "Website": "Error"
        }


async def main():
    law_firms = load_law_firms_from_file("filtered_results.txt")
    if not law_firms:
        print("🚫 No law firms loaded. Exiting.")
        return

    data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        for firm in law_firms:
            print(f"🔍 Scraping: {firm['name']}")
            info = await scrape_firm_info(page, firm['name'], firm['url'])
            data.append(info)

        await browser.close()

    df = pd.DataFrame(data)
    df.to_csv("law_firms_playwright.csv", index=False, encoding="utf-8")
    print("✅ Scraping complete! Results saved to 'law_firms_playwright.csv'.")


# Run the script
asyncio.run(main())
