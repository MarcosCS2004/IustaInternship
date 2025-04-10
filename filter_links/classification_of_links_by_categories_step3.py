import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from datetime import datetime

def analyze_law_page(url):
    """
    Analyzes a web page to determine if it's a lawyer directory, law firm, or other.
    Focused on German law websites with English detection logic.
    
    Args:
        url (str): URL to analyze
        
    Returns:
        str: "Lawyer directory", "Law firm", or "Other"
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        
        # German and English keywords for lawyer directories
        directory_keywords = [
            # German terms
            'anwaltsverzeichnis', 'anwaltssuche', 'anwaltsliste',
            'rechtsanwaltskammer', 'anwaltskammer', 'anwaltsdatenbank',
            'anwalt finden', 'anwälte suchen', 'anwaltsregister',
            # English terms
            'lawyer directory', 'attorney search', 'find a lawyer',
            'lawyer list', 'attorney listing', 'lawyer database',
            'bar association', 'legal directory'
        ]
        
        # German and English keywords for law firms
        firm_keywords = [
            # German terms
            'kanzlei', 'rechtsanwälte', 'anwaltskanzlei',
            'anwaltsbüro', 'anwaltsteam', 'anwaltssozietät',
            'fachanwälte', 'anwaltsgruppe', 'rechtsanwaltsbüro',
            # English terms
            'law firm', 'legal firm', 'attorneys at law',
            'legal office', 'law office', 'legal team',
            'lawyers', 'attorneys', 'legal services',
            'our lawyers', 'legal experts'
        ]
        
        # Check for lawyer directory patterns
        for keyword in directory_keywords:
            if keyword in page_text:
                return "Lawyer directory"
        
        # Check for law firm patterns
        for keyword in firm_keywords:
            if keyword in page_text:
                return "Law firm"
        
        # Check HTML structure patterns
        # 1. Lawyer directories typically have multiple profiles
        lawyer_profiles = soup.find_all(class_=re.compile(
            r'anwalt|attorney|lawyer|profile|profil|team|member|mitglied', 
            re.I
        ))
        if len(lawyer_profiles) > 3:
            return "Lawyer directory"
        
        # 2. Law firms often have "about us" or "our team" sections
        team_sections = soup.find_all(class_=re.compile(
            r'team|unser-team|über-uns|about|attorneys|lawyers|anwälte', 
            re.I
        ))
        if team_sections:
            return "Law firm"
        
        # 3. Check page title and meta description
        title = soup.title.string.lower() if soup.title else ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc = meta_desc.get('content', '').lower() if meta_desc else ""
        
        for keyword in directory_keywords:
            if keyword in title or keyword in meta_desc:
                return "Lawyer directory"
        
        for keyword in firm_keywords:
            if keyword in title or keyword in meta_desc:
                return "Law firm"
        
        # 4. Check for common German law firm URL patterns
        domain = urlparse(url).netloc.lower()
        if any(word in domain for word in ['kanzlei', 'rechtsanwaelte', 'anwalt', 'ra-']):
            return "Law firm"
        
        # 5. Check for imprint/impressum which often contains firm info
        impressum = soup.find('a', href=re.compile(r'impressum|imprint', re.I))
        if impressum:
            impressum_text = requests.get(
                requests.compat.urljoin(url, impressum['href']), 
                headers=headers
            ).text.lower()
            if any(keyword in impressum_text for keyword in firm_keywords):
                return "Law firm"
        
        return "Other"
        
    except requests.exceptions.RequestException as e:
        print(f"Network error analyzing {url}: {str(e)}")
        return "Error: Request failed"
    except Exception as e:
        print(f"Error analyzing {url}: {str(e)}")
        return "Error: Analysis failed"

def process_law_firm_csv(input_file, output_file):
    """
    Processes a CSV file with URLs and analyzes each one for law firm/directory identification.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    try:
        # Read input CSV
        df = pd.read_csv(input_file)
        
        # Verify required column exists
        if 'url' not in df.columns:
            raise ValueError("Input CSV must contain a 'url' column")
        
        print(f"Starting analysis of {len(df)} URLs at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Analyze each URL
        df['type'] = df['url'].apply(analyze_law_page)
        
        # Calculate statistics
        stats = df['type'].value_counts()
        print("\nAnalysis completed with the following results:")
        print(stats)
        
        # Save results
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
        
        return df
        
    except Exception as e:
        print(f"Error processing CSV files: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    # Configuration
    INPUT_CSV = 'resultados_m2.csv'  # Input CSV with 'url' column
    OUTPUT_CSV = 'german_law_analysis.csv'  # Output CSV with results
    
    # Run analysis
    process_law_firm_csv(INPUT_CSV, OUTPUT_CSV)