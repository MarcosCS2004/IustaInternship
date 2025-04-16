import pandas as pd  # For handling CSV files
import requests  # For making HTTP requests
from bs4 import BeautifulSoup  # For parsing HTML content
from urllib.parse import urlparse  # For analyzing URL components
import re  # For regular expressions
from datetime import datetime  # For timestamps (if needed)

# Analyze a single web page and classify it as a law firm, lawyer directory, or other
def analyze_law_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        }

        # Make request to the URL
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse the page and extract all text
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text().lower()

        # Keywords to identify lawyer directories
        directory_keywords = [
            "anwaltsverzeichnis", "anwaltssuche", "anwaltsliste", "rechtsanwaltskammer", "anwaltskammer",
            "anwaltsdatenbank", "anwalt finden", "anwälte suchen", "anwaltsregister", "lawyer directory",
            "attorney search", "find a lawyer", "lawyer list", "attorney listing", "lawyer database",
            "bar association", "legal directory",
        ]

        # Keywords to identify law firms
        firm_keywords = [
            "kanzlei", "rechtsanwälte", "anwaltskanzlei", "anwaltsbüro", "anwaltsteam", "anwaltssozietät",
            "fachanwälte", "anwaltsgruppe", "rechtsanwaltsbüro", "law firm", "legal firm", "attorneys at law",
            "legal office", "law office", "legal team", "lawyers", "attorneys", "legal services",
            "our lawyers", "legal experts",
        ]

        # Check if page contains directory-related keywords
        for keyword in directory_keywords:
            if keyword in page_text:
                return "Lawyer directory"

        # Check if page contains law firm-related keywords
        for keyword in firm_keywords:
            if keyword in page_text:
                return "Law firm"

        # Check class names that might indicate lawyer profiles
        lawyer_profiles = soup.find_all(class_=re.compile(r"anwalt|attorney|lawyer|profile|profil|team|member|mitglied", re.I))
        if len(lawyer_profiles) > 3:
            return "Lawyer directory"

        # Check class names for "team" or "about us" sections, which are common in law firm websites
        team_sections = soup.find_all(class_=re.compile(r"team|unser-team|über-uns|about|attorneys|lawyers|anwälte", re.I))
        if team_sections:
            return "Law firm"

        # Check title and meta description for classification clues
        title = soup.title.string.lower() if soup.title else ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc.get("content", "").lower() if meta_desc else ""

        for keyword in directory_keywords:
            if keyword in title or keyword in meta_desc:
                return "Lawyer directory"

        for keyword in firm_keywords:
            if keyword in title or keyword in meta_desc:
                return "Law firm"

        # Analyze domain name for common law firm-related terms
        domain = urlparse(url).netloc.lower()
        if any(word in domain for word in ["kanzlei", "rechtsanwaelte", "anwalt", "ra-"]):
            return "Law firm"

        # Try checking the "Impressum" (legal notice) page for firm-related terms
        impressum = soup.find("a", href=re.compile(r"impressum|imprint", re.I))
        if impressum:
            impressum_text = requests.get(requests.compat.urljoin(url, impressum["href"]), headers=headers).text.lower()
            if any(keyword in impressum_text for keyword in firm_keywords):
                return "Law firm"

        return "Other"

    # Handle HTTP/network errors
    except requests.exceptions.RequestException as e:
        print(f"Network error analyzing {url}: {str(e)}")
        return "Error: Request failed"

    # Handle any other unexpected issues
    except Exception as e:
        print(f"Error analyzing {url}: {str(e)}")
        return "Error: Analysis failed"

# Process a CSV file and classify each URL
def process_law_firm_csv(input_file, url_column, output_file):
    try:
        df = pd.read_csv(input_file)

        # Check if specified column exists
        if url_column not in df.columns:
            raise ValueError(f"Input CSV must contain a '{url_column}' column")

        print(f"\nStarting analysis of {len(df)} URLs...")

        # Apply analysis function to each URL and create new column
        df["type"] = df[url_column].apply(analyze_law_page)

        # Print classification summary
        stats = df["type"].value_counts()
        print("\nAnalysis completed with the following results:")
        print(stats)

        # Save the results to output file
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to '{output_file}'")

        return df

    except Exception as e:
        print(f"Error processing CSV files: {str(e)}")
        return None

# Entry point for running the script
if __name__ == "__main__":
    print("== German Law Website Analyzer ==")

    # Get user inputs
    input_csv = input("Enter the path to your input CSV file: ").strip()
    url_column = input("Enter the name of the column with the URLs: ").strip()
    output_csv = input("Enter a name for the output CSV file (e.g., results.csv): ").strip()

    # Start processing
    process_law_firm_csv(input_csv, url_column, output_csv)
