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

def tools_menu():
    """Submenu for Tools options."""
    tools_options = {
        "1": ("Add space after commas", "scripts/tools/put_space_after_comma.py"),
        "2": ("Remove duplicate entries", "scripts/tools/remove_duplicates.py"),
        "3": ("Back to main menu", None)
    }

    while True:
        print("\n--- Tools Menu ---")
        for key, (description, _) in tools_options.items():
            print(f"{key}. {description}")
        
        choice = input("Select a tool (1-3): ").strip()

        if choice == "3":
            break
        elif choice in tools_options:
            _, script_path = tools_options[choice]
            run_script(script_path)
        else:
            print("Invalid choice. Please select a number between 1 and 3.")

def filters_menu():
    """Submenu for Filters options."""
    filters_options = {
        "1": ("Filter links by specific keywords (Step 1)", "scripts/filters/filter_links_by_words_step1.py"),
        "2": ("Filter useful links (Step 2)", "scripts/filters/filter_useful_links_step2.py"),
        "3": ("Classify links by category (Step 3)", "scripts/filters/classify_links_by_category_step3.py"),
        "4": ("Split links by category (Step 4)", "scripts/filters/split_by_category_step4.py"),
        "5": ("Back to main menu", None)
    }

    while True:
        print("\n--- Filters Menu ---")
        for key, (description, _) in filters_options.items():
            print(f"{key}. {description}")
        
        choice = input("Select a filter (1-5): ").strip()

        if choice == "5":
            break
        elif choice in filters_options:
            _, script_path = filters_options[choice]
            run_script(script_path)
        else:
            print("Invalid choice. Please select a number between 1 and 5.")

def browsers_menu():
    """Submenu for browser-based bots."""
    browsers_options = {
        "1": ("Run LinkedIn bot", "scripts/bots/browsers/linkedin_bot.py"),
        "2": ("Run Web Finder bot", "scripts/bots/browsers/web_finder_bot.py"),
        "3": ("Back to main menu", None)
    }

    while True:
        print("\n--- Browsers Menu ---")
        for key, (description, _) in browsers_options.items():
            print(f"{key}. {description}")
        
        choice = input("Select a browser script (1-3): ").strip()

        if choice == "3":
            break
        elif choice in browsers_options:
            _, script_path = browsers_options[choice]
            run_script(script_path)
        else:
            print("Invalid choice. Please select a number between 1 and 3.")

def main():
    set_project_root()

    options = {
        "1": ("Search for law firms via Google API", "scripts/search/search_lawyers_api.py"),
        "2": ("Filters", "filters_menu"),
        "3": ("Tools", "tools_menu"),
        "4": ("Scrape links from specific pages (Step 1)", "scripts/bots/specific_pages/get_links_step1.py"),
        "5": ("Scrape data from collected links (Step 2)", "scripts/bots/specific_pages/get_data_from_links_step2.py"),
        "6": ("Scrape data from anwalt.de", "scripts/bots/specific_pages/get_data_from_anwalt.py"),
        "7": ("Browsers", "browsers_menu"),
        "8": ("Exit", None)
    }

    while True:
        print("\n====== Law Firm Data Collection - Main Menu ======")
        for key, (description, _) in options.items():
            print(f"{key}. {description}")

        choice = input("Select an option (1-8): ").strip()

        if choice == "8":
            print("Exiting... Goodbye!")
            break
        elif choice == "2":
            filters_menu()
        elif choice == "3":
            tools_menu()
        elif choice == "7":
            browsers_menu()
        elif choice in options:
            _, script_path = options[choice]
            run_script(script_path)
        else:
            print("Invalid choice. Please select a number between 1 and 8.")

if __name__ == "__main__":
    main()
