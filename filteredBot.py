import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random

# Cabeceras para simular un navegador real
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

def extract_info_from_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Obtener título del sitio
        title = soup.title.string.strip() if soup.title else "not found"

        contact_link = "not found"
        linkedin_link = "not found"

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].lower()

            if 'contact' in href or 'contacto' in href or 'kontakt' in href:
                if href.startswith('/'):
                    contact_link = url.rstrip('/') + href
                elif not href.startswith('http'):
                    contact_link = url.rstrip('/') + '/' + href
                else:
                    contact_link = href

            if 'linkedin.com' in href:
                linkedin_link = href

        return {
            'name': title,
            'contact link': contact_link,
            'linkedin': linkedin_link
        }

    except Exception as e:
        print(f"Error en {url}: {e}")
        return {
            'name': 'not found',
            'contact link': 'not found',
            'linkedin': 'not found'
        }

def process_urls(url_list, output_file='output.csv'):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'contact link', 'linkedin']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for url in url_list:
            info = extract_info_from_url(url)
            writer.writerow(info)
            print(f"Procesado: {url}")
            time.sleep(random.uniform(1, 3))

# Leer URLs desde el CSV
urls = []

with open("filtered_links_Markenrecht_v2.csv", newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'Link' in row and row['Link'].strip():
            urls.append(row['Link'].strip())

# Procesar todas las URLs recogidas
process_urls(urls)
