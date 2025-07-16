import os, requests, json
from datetime import datetime


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def hidden_link(text, url):
    """ Creates a hidden link in the terminal that can be clicked to open the URL. """
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def fetch_json(url):
    """ Fetches the data in JSON format from the given URL and handles errors. """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"\033[31mError fetching data: {e}\033[0m")
        exit()


def locale_input():
    """ Prompts the user for a locale input and returns it in lowercase. """
    locale = input("Enter your locale (use the ISO standard) [en-US]: ").strip().lower() or "en-us"
    return locale

def get_series_id(tmdb, locale):
    series_id = None
    while True:
        choice = input("Do you want to input the series ID directly or search by its title? (i/t): ").strip().lower()
        if choice == "i":
            series_id = input("Enter the id of the series: ").strip()
            break
        elif choice == "t":
            while True:
                title = input("Enter the title of the series: ").strip()
                search_data = tmdb.search_series(title, locale)
                if search_data.get("results"):
                    for i, result in enumerate(search_data["results"], start=1):
                        print(f"{i}. {result['name']} (\033[96m{result['first_air_date'].split('-')[0]}\033[0m)")
                    while True:
                        choice = input(f"Select the series by its number (1-{len(search_data['results'])}): ").strip()
                        if choice.isdigit() and 1 <= int(choice) <= len(search_data["results"]):
                            series_id = search_data["results"][int(choice) - 1]["id"]
                            break
                        else:
                            print(f"\033[31mInvalid choice. Please select a number between 1 and {len(search_data['results'])}.\033[0m")
                    print(f"\033[32mSeries ID: {series_id}\033[0m")
                else:
                    print(f"\033[31mNo series found with the title '{title}'.\033[0m")
                    exit()
                break
    if not series_id:
        print("\033[31mSeries ID could not be determined.\033[0m")
        exit()
    return series_id


class TMDB:
    """ A class to interact with the TMDB API. """

    def __init__(self):
        api_key = input("Enter your TMDB API key: ").strip()
        if not api_key:
            print("\033[31mAPI key is required to use the TMDB API.\033[0m")
            exit()
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3/"

    def search_series(self, title, locale):
        """ Searches for a series by its title and returns the first result. """
        search_url = f"{self.base_url}search/tv?api_key={self.api_key}&query={title}&language={locale}"
        search_data = fetch_json(search_url)
        if search_data.get("results"):
            return search_data
        else:
            print(f"\033[31mNo series found with the title '{title}'.\033[0m")
            return None


def create_series():
    clear_screen()

    print(f"\033[35mCreating a new series...\033[0m\n")

    tmdb = TMDB()
    user_locale = locale_input()

    series_id = get_series_id(tmdb, user_locale)


def print_series_tree_from_file():
    pass


def print_series_tree_from_tmdb():
    pass


def main():
    try:
        while True:
            clear_screen()
            print(f"\033[1;36mWelcome to the Series mapper!\033[0m\n" +
                  "Select an action (or use -1 for exit):\n" +
                  "\t1. Fetch new series data into a file\n" +
                  "\t2. Print series tree from file\n" +
                  "\t3. Print series tree from TMDB")

            action = input("Action: ")

            match action:
                case "-1":
                    print(f"\033[31mExiting the program...\033[0m")
                    break
                case "1":
                    create_series()
                case "2":
                    print("\033[33mNot implemented yet...\033[0m")
                    input("Press Enter to continue...")
                    continue
                    print_series_tree_from_file()
                case "3":
                    print("\033[33mNot implemented yet...\033[0m")
                    input("Press Enter to continue...")
                    continue
                    print_series_tree_from_tmdb()
                case _:
                    print(f"\033[31mInvalid action selected. Please try again.\033[0m")
                    input("Press Enter to continue...")
    except KeyboardInterrupt:
        print("\n\033[31mProgram interrupted by user.\033[0m")
    except Exception as e:
        print(f"\033[31mAn error occurred: {e}\033[0m")


if __name__ == "__main__":
    main()