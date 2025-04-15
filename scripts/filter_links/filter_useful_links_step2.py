import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time


def contains_relevant_info(text):
    text = text.lower()

    has_email = re.search(r"\b[\w.-]+?@\w+?\.\w+?\b", text)

    address_keywords = [
        "address",
        "dirección",
        "direccion",
        "street",
        "avenue",
        "calle",
        "adresse",
        "straße",
        "strasse",
        "platz",
        "hausnummer",
    ]

    name_keywords = [
        "law firm",
        "abogado",
        "attorney",
        "firma",
        "law office",
        "anwalt",
        "rechtsanwalt",
        "kanzlei",
        "jurist",
    ]

    has_address = any(keyword in text for keyword in address_keywords)
    has_name = any(keyword in text for keyword in name_keywords)

    return has_email or has_address or has_name


def analyze_links(csv_path, link_column, output_csv):
    df = pd.read_csv(csv_path)
    filtered_links = []

    for index, row in df.iterrows():
        url = row[link_column]
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                if contains_relevant_info(text):
                    filtered_links.append({"url": url})
        except Exception as e:
            print(f"Error with {url}: {e}")

        time.sleep(1)

    result_df = pd.DataFrame(filtered_links)
    result_df.to_csv(output_csv, index=False)
    print(
        f"Analysis complete. {len(result_df)} links with relevant information saved to '{output_csv}'."
    )


# Run
analyze_links("filtered_links_Markenrecht_v2.csv", "Link", "useful_links_result.csv")
