# 🏛️ Project: Law Firms in Germany

This project automates the search and collection of information about law firms in Germany using APIs, web scraping, custom bots, and data processing. Its goal is to centralize and classify useful data from various sources such as Google, LinkedIn, and law firm-specific websites.

---

## 📁 Project Structure

```
|
├── main.py
|
├── scripts/
│    ├── bots/                                       # Bots for web navigation and scraping
|    │   ├── browsers/                               # General scrapers 
|    │   │   ├── linkedin_bot.py
|    │   │   └── web_finder_bot.py
|    │   ├── lawfirms/                               # Law firm-specific scrapers
|    │   │   ├── bot_scraper.py
|    │   │   └── filtered_bot.py
|    │   └── specific_pages/                         # Step-by-step scrapers from a specific URL
|    │       ├── get_links_step1.py
|    │       └── get_data_from_links_step2.py
|    ├── filters/                                    # Filtering and classification
|    │   ├── filter_links_by_words_step1.py
|    │   ├── filter_useful_links_step2.py
|    │   ├── classify_links_by_category_step3.py
|    │   └── split_by_category_step4.py
|    ├── search/                                     # Initial search via API
|    │   └── search_lawyers_api.py
|    └── tools/                                      # General utility scripts
|        └── put_space_after_comma.py
|
├── data/
|    ├── raw/                                        # Raw, unprocessed data
|    └── processed/                                  # Cleaned/ready data
|
└── logs/                                           # Execution logs
    └── run_log.txt

```

---

## 🛠️ Technologies Used

- **Python 3.9+**
- **Selenium** (browser automation)
- **Requests** and **BeautifulSoup** (HTML scraping)
- **SerpAPI** (Google Search API)
- **Pandas** (data processing)

---

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/MarcosCS2004/IustaInternship

```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## ⚙️ How to Use

### Step 1: Search for law firms via Google API
```bash
python scripts/search/search_lawyers_api.py
```

### Step 2: Filter and classify the collected links
```bash
python scripts/filters/filter_links_by_words_step1.py
python scripts/filters/filter_useful_links_step2.py
python scripts/filters/classify_links_by_category_step3.py
python scripts/filters/split_by_category_step4.py
```

### Step 3: Clean up text (optional)
```bash
python scripts/tools/put_space_after_comma.py
```

### Step 4: Scrape data from specific pages
```bash
python scripts/bots/specific_pages/get_links_step1.py
python scripts/bots/specific_pages/get_data_from_links_step2.py
```

---

## 🧾 Execution Logging (Optional)

To log progress, errors, or key events during script execution, you can use a simple logging function that writes to `logs/run_log.txt`.

### Logging function

```python
from datetime import datetime

def log_message(message):
    with open("logs/run_log.txt", "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")
```

### 💡 Example usage in a script

```python
log_message("Started scraping LinkedIn.")
# ... your code ...
log_message("Scraping completed. 150 profiles found.")
```

> Make sure the `logs/` directory exists, or create it with `os.makedirs("logs", exist_ok=True)` before writing to the log.

---

## Additional Requirements

- A valid Google Search API key (stored as an environment variable or directly in the script).
- (Optional) Active LinkedIn session or cookies if using LinkedIn scraping.

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). You are free to use, modify, or distribute it as long as you retain the copyright.

---

## ✍️ Author

Developed by Geanina Foanta and Marcos Calvo.
