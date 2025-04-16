import os
import sys

def set_project_root():
    """Ensure the script always runs from the root directory of the project."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

def run_script(script_path):
    """Execute a Python script given its path relative to the project root."""
    try:
        os.system(f"python {script_path}")
    except Exception as e:
        print(f"An error occurred while running {script_path}: {e}")

def main():
    set_project_root()

    options = {
        "1": ("Search for law firms via Google API", "scripts/search/search_lawyers_api.py"),
        "2": ("Filter links by specific keywords (Step 1)", "scripts/filters/filter_links_by_words_step1.py"),
        "3": ("Filter useful links (Step 2)", "scripts/filters/filter_useful_links_step2.py"),
        "4": ("Classify links by category (Step 3)", "scripts/filters/classify_links_by_category_step3.py"),
        "5": ("Split links by category (Step 4)", "scripts/filters/split_by_category_step4.py"),
        "6": ("Format text: Add space after commas", "scripts/tools/put_space_after_comma.py"),
        "7": ("Scrape links from specific pages (Step 1)", "scripts/bots/specific_pages/get_links_step1.py"),
        "8": ("Scrape data from collected links (Step 2)", "scripts/bots/specific_pages/get_data_from_links_step2.py"),
        "9": ("Scrape data from anwalt.de", "scripts/bots/specific_pages/get_data_from_anwalt.py"),
        "10": ("Exit", None)
    }

    while True:
        print("\n====== Law Firm Data Collection - Main Menu ======")
        for key, (description, _) in options.items():
            print(f"{key}. {description}")

        choice = input("Select an option (1-10): ").strip()

        if choice == "10":
            print("Exiting... Goodbye!")
            break
        elif choice in options:
            _, script_path = options[choice]
            run_script(script_path)
        else:
            print("Invalid choice. Please select a number between 1 and 10.")

if __name__ == "__main__":
    main()
