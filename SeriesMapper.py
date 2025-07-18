import os, requests, json, re
from typing import Tuple


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def hidden_link(text, url) -> str:
    """ Creates a hidden link in the terminal that can be clicked to open the URL. """
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def sanitize(text: str) -> str:
    """ Sanitizes the input by removing special characters that are not allowed in filenames. """
    return re.sub(r'[<>:"/\\|?*]', "", text)  # Remove special characters


def fetch_json(url) -> dict:
    """ Fetches the data in JSON format from the given URL and handles errors. """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise ValueError(f"Error fetching data from {url}: {e}")


def locale_input() -> str:
    """ Prompts the user for a locale input and returns it in lowercase. """
    locale = input("Enter your locale (use ISO 639-1 and possibly ISO 3166-1) [en-US]: ").strip().lower() or "en-us"

    if not (re.match(r"^[a-z]{2}$", locale) or re.match(r'^[a-z]{2}-[A-Z]{2}$', locale)):
        raise ValueError("Invalid locale format. Please enter a valid locale format consisting of 639-1 and 3166-1 values separated by a hyphen (e.g., 'en' or 'en-US').")

    return locale


def get_series_by_title(tmdb, locale) -> Tuple[str, dict]:
    """ Searches for a series by its title and returns the series ID and data. """
    title = input("Enter the title of the series: ")

    search_data = tmdb.search_series(title, locale)

    if not search_data.get("results"):
        return get_series_by_title(tmdb, locale)

    for i, result in enumerate(search_data["results"], start=1):
        first_year = result['first_air_date'].split('-')[0] if result.get('first_air_date') else "N/A"
        link = hidden_link(f"{result['name']}", f"https://www.themoviedb.org/tv/{result['id']}")
        print(f"{i}. {link} (\033[96m{first_year}\033[0m)")

    while True:
        choice = input(f"Select the series by its number (1-{len(search_data['results'])} or \"n\" if it doesn't match): ").strip()
        if choice == "n":
            return get_series_by_title(tmdb, locale)
        elif choice.isdigit() and 1 <= int(choice) <= len(search_data["results"]):
            series_id = search_data["results"][int(choice) - 1]["id"]
            break
        else:
            print(f"\033[31mInvalid choice. Please select a number between 1 and {len(search_data['results'])}.\033[0m")

    series_data = tmdb.get_series_details(series_id, locale)

    if not series_data:
        return get_series_by_title(tmdb, locale)

    return series_id, series_data


def get_series_by_id(tmdb, locale) -> Tuple[str, dict]:
    series_id = input("Enter the id of the series: ").strip()

    if not series_id.isdigit():
        print(f"\033[31mInvalid series ID. Please enter a valid numeric ID.\033[0m")
        return get_series_by_id(tmdb, locale)

    series_data = tmdb.get_series_details(series_id, locale)

    if not series_data:
        return get_series_by_id(tmdb, locale)

    first_year = series_data['first_air_date'].split('-')[0] if series_data.get('first_air_date') else "N/A"
    link = hidden_link(f"{series_data['name']}", f"https://www.themoviedb.org/tv/{series_id}")
    is_correct = input(f"Is \033[1m{link} (\033[96m{first_year}\033[0m) series you are looking for? (y/n): ").strip().lower()

    if is_correct != "y":
        return get_series_by_id(tmdb, locale)
    return series_id, series_data


def get_series(tmdb, locale) -> Tuple[str, dict]:
    while True:
        choice = input("Do you want to input the series ID directly or search by its title? (i/t): ").strip().lower()
        if choice == "i":
            got_series_id, got_series_data = get_series_by_id(tmdb, locale)
            if got_series_id and got_series_data:
                series_id = got_series_id
                series_data = got_series_data
                break

        elif choice == "t":
            got_series_id, got_series_data = get_series_by_title(tmdb, locale)
            if got_series_id and got_series_data:
                series_id = got_series_id
                series_data = got_series_data
                break

    return series_id, series_data


class TMDB:
    """ A class to interact with the TMDB API. """

    def __init__(self):
        api_key = input("Enter your TMDB API key: ").strip()
        if not api_key:
            print("\033[31mAPI key is required to use the TMDB API.\033[0m")
            exit()
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3/"

    def search_series(self, title, locale) -> dict | None:
        """ Searches for a series by its title and returns the first result. """
        search_url = f"{self.base_url}search/tv?api_key={self.api_key}&query={title}&language={locale}"
        search_data = fetch_json(search_url)
        if search_data.get("results"):
            return search_data
        else:
            print(f"\033[31mNo series found with the title '{title}'.\033[0m")
            return None

    def get_series_details(self, series_id, locale) -> dict | None:
        """ Fetches the details of a series by its ID. """
        url = f"{self.base_url}tv/{series_id}?api_key={self.api_key}&language={locale}"
        try:
            return fetch_json(url)
        except Exception as e:
            print(f"\033[31mError fetching series details: {e}\033[0m")
        return None

    def get_season_details(self, series_id, season_number, locale) -> dict:
        """ Fetches the details of a season by its series ID and season number. """
        url = f"{self.base_url}tv/{series_id}/season/{season_number}?api_key={self.api_key}&language={locale}"
        try:
            return fetch_json(url)
        except Exception as e:
            raise Exception(f"Error fetching season details: {e}")


def process_series(tmdb, series_id, series_data, locale) -> dict:
    """ Processes the series data and returns a dictionary with seasons and episodes. """
    series = {
        "title": series_data.get("name"),
        "specials": True,
        "seasons": {}
    }

    include_specials = True if input("Do you want to include specials? (y/n): ").strip().lower() == "y" else False

    number_of_seasons = series_data.get("number_of_seasons")

    if number_of_seasons is None:
        raise Exception("Not valid series data, number_of_seasons is None.")

    print(f"\n\033[34mFound {number_of_seasons} seasons in the series.\033[0m")

    has_specials = False
    if include_specials:
        for season in series_data.get("seasons", []):
            if season.get("season_number") == 0:
                has_specials = True
                break
    else:
        series["specials"] = False
        print("")

    if include_specials and has_specials:
        print(f"\033[34mFound specials in the series.\033[0m\n")
    elif include_specials and not has_specials:
        print(f"\033[33mNo specials found for this series.\033[0m\n")

    for season in series_data.get("seasons", []):
        season_number = season.get("season_number")
        season_name = season.get("name", f"Season {season_number}")

        if season_number == 0 and not include_specials:
            continue

        series["seasons"][season_number] = {
            "name": season_name,
            "episodes": {}
        }

        season_data = tmdb.get_season_details(series_id, season_number, locale)

        for episode in season_data.get("episodes", []):
            episode_number = episode.get("episode_number")
            episode_name = episode.get("name", f"Episode {episode_number}")
            series["seasons"][season_number]["episodes"][episode_number] = episode_name

        print(f"\033[34mFound {len(season_data.get('episodes', []))} episodes in season {season_number}.\033[0m")

    return series


def create_series():
    clear_screen()

    print(f"\033[35mCreating a new series...\033[0m\n")

    tmdb = TMDB()
    user_locale = locale_input()

    series_id, series_data = get_series(tmdb, user_locale)

    series = process_series(tmdb, series_id, series_data, user_locale)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sanitize(f"series-{series_data.get("name", "Unknown").replace(" ", "_")}.json"))

    with open(path, "w", encoding="utf-8") as file:
        json.dump(series, file, ensure_ascii=False, indent=2)

    print(f"\n\033[32mSeries map successfully saved to \"{path}\"!\033[0m")


def print_series_tree_from_file():
    pass


def print_series_tree_from_tmdb():
    pass


def main():
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
                input("Press Enter to continue...")
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[31mProgram interrupted by user.\033[0m")
    except Exception as e:
        print(f"\033[31mAn error occurred: {e}\033[0m")