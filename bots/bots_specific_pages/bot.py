from playwright.sync_api import sync_playwright
import re

# Enhanced keywords (English and German)
TRAFFIC_KEYWORDS = ["traffic", "verkehr", "transport", "auto", "fahrzeug", "straße"]
FULL_SERVICE_KEYWORDS = [r"full[\s-]?service", "vollservice", "komplettservice"]
LICENSE_KEYWORDS = ["license", "lizenz", "erlaubnis", "genehmigung"]


def matches_criteria(text):
    """Checks if the text meets at least one of the criteria"""
    text_lower = text.lower()

    # For traffic
    traffic_match = any(
        re.search(rf"\b{keyword}\b", text_lower) for keyword in TRAFFIC_KEYWORDS
    )

    # For Full Service (uses regex)
    full_service_match = any(
        re.search(keyword, text_lower) for keyword in FULL_SERVICE_KEYWORDS
    )

    # For licenses
    license_match = any(
        re.search(rf"\b{keyword}\b", text_lower) for keyword in LICENSE_KEYWORDS
    )

    return traffic_match or full_service_match or license_match


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=False,
        slow_mo=100,
    )

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        viewport={"width": 1280, "height": 720},
    )

    page = context.new_page()

    with open("filtered_results.txt", "w", encoding="utf-8") as f:
        for i in range(1, 11):
            url = f"https://www.hg.org/lawfirms/germany?page={i}"
            print(f"Navigating to: {url}")

            try:
                page.goto(url, timeout=60000)
                page.wait_for_selector("div.listing", timeout=30000)

                listings = page.query_selector_all("div.listing")
                for listing in listings:
                    speciality_element = listing.query_selector("h3")
                    if speciality_element:
                        speciality = speciality_element.text_content().strip()
                        if matches_criteria(speciality):
                            link_element = listing.query_selector(
                                "h3 a"
                            ) or listing.query_selector("a[href]")
                            if link_element:
                                href = link_element.get_attribute("href")
                                title = (
                                    link_element.get_attribute("title") or "No title"
                                )
                                f.write(
                                    f"Name: {title} | Speciality {speciality} | URL: {href}\n"
                                )
                                print(f"Record found: {title} - {speciality}")
                            else:
                                f.write(
                                    f"Specialty: {speciality} | Link not available\n"
                                )

            except Exception as e:
                print(f"Error on page {i}: {e}")
                page.screenshot(path=f"error_page_{i}.png")

    print("Process completed. Results saved in filtered_results.txt")
    browser.close()
