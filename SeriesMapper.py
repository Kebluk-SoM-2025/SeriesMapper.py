import os
import requests
import json
import re
from typing import Tuple
from dataclasses import dataclass


@dataclass
class Season:
    """ A class to represent a season with its episodes. """
    name: str
    episodes: dict[int, str] # Mapping episode number to an Episode object


@dataclass
class Series:
    """ A class to represent a series with its seasons and episodes. """
    title: str
    specials: bool
    seasons: dict[int, Season] # Mapping season number to a Season object


class TMDB:
    """ A class to interact with the TMDB API. """
    def __init__(self) -> None:
        api_key = input("Enter your TMDB API key: ").strip()
        if not api_key:
            print("\033[31mAPI key is required to use the TMDB API.\033[0m")
            exit()
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3/"

    def search_series(self, title: str, locale: str) -> dict | None:
        """ Searches for a series by its title and returns the first result. """
        search_url = f"{self.base_url}search/tv?api_key={self.api_key}&query={title}&language={locale}"
        search_data = fetch_json(search_url)
        if search_data.get("results"):
            return search_data
        else:
            print(f"\033[31mNo series found with the title '{title}'.\033[0m")
            return None


    def get_series_details(self, series_id: str, locale: str) -> dict:
        """ Fetches the details of a series by its ID. """
        url = f"{self.base_url}tv/{series_id}?api_key={self.api_key}&language={locale}"
        try:
            return fetch_json(url)
        except Exception as e:
            raise Exception(f"\033[31mError fetching series details: {e}\033[0m")


    def get_season_details(self, series_id: str, season_number: str, locale: str) -> dict | None:
        """ Fetches the details of a season by its series ID and season number. """
        url = f"{self.base_url}tv/{series_id}/season/{season_number}?api_key={self.api_key}&language={locale}"
        try:
            return fetch_json(url)
        except Exception as e:
            print(f"\033[31mError fetching season details: {e}")
        return None


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def hidden_link(text: str, url: str) -> str:
    """ Creates a hidden link in the terminal that can be clicked to open the URL. """
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


def sanitize(text: str) -> str:
    """ Sanitizes the input by removing special characters that are not allowed in filenames. """
    return re.sub(r'[<>:"/\\|?*]', "", text)


def fetch_json(url: str) -> dict:
    """ Fetches the data in JSON format from the given URL and handles errors. """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise ValueError(f"Error fetching data from {url}: {e}")


def get_series_by_title(tmdb: TMDB, locale: str) -> Tuple[str, dict]:
    """ Searches for a series by its title and returns the series ID and data. """
    title = input("Enter the title of the series: ")

    # Retrieve the series data from TMDB using the provided title and locale
    search_data = tmdb.search_series(title, locale)

    # If no results are found, call the function again to get a new title
    if not search_data.get("results"):
        return get_series_by_title(tmdb, locale)

    # If results are found, display them with clickable links
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


def get_series_by_id(tmdb: TMDB, locale: str) -> Tuple[str, dict]:
    """ Gets the series ID and data by directly inputting the series ID. """
    series_id = input("Enter the id of the series: ").strip()

    # Validate the series ID
    if not series_id.isdigit():
        print(f"\033[31mInvalid series ID. Please enter a valid numeric ID.\033[0m")
        return get_series_by_id(tmdb, locale)

    # Fetch the series details using the provided ID
    series_data = tmdb.get_series_details(series_id, locale)

    if not series_data:
        return get_series_by_id(tmdb, locale)

    # If the series data is found, display its name and first air date as a clickable link
    first_year = series_data['first_air_date'].split('-')[0] if series_data.get('first_air_date') else "N/A"
    link = hidden_link(f"{series_data['name']}", f"https://www.themoviedb.org/tv/{series_id}")

    is_not_correct = (input(f"Is \033[1m{link} (\033[96m{first_year}\033[0m) series you are looking for? (y/n) [y]: ").strip().lower() or "y") != "y"

    # If the user rejects the series, call the function again to get a new series ID
    if is_not_correct:
        return get_series_by_id(tmdb, locale)
    return series_id, series_data


def get_series(tmdb: TMDB, locale: str) -> Tuple[str, dict]:
    """ Gets the series ID and data either by title or by ID. """
    while True:
        choice = input("Do you want to input the series ID directly or search by its title? (i/t) [t]: ").strip().lower() or "t"
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


def process_series(tmdb: TMDB, series_id: str, series_data: dict, locale: str) -> Series:
    """ Processes the series data and returns a dictionary with seasons and episodes. """
    include_specials = (input("Do you want to include specials? (y/n) [y]: ").strip().lower() or "y") == "y"

    series = Series(
        title=series_data.get("name"),
        specials=include_specials,
        seasons={}
    )

    number_of_seasons = series_data.get("number_of_seasons")

    if number_of_seasons is None:
        raise Exception("Not valid series data, number_of_seasons is None.")

    print(f"\n\033[34mFound {number_of_seasons} seasons in the series.\033[0m")

    # Check if specials are included
    specials_found = False
    if include_specials:
        for season in series_data.get("seasons", []):
            if season.get("season_number") == 0:
                specials_found = True
                break
    else:
        print("")

    if include_specials and specials_found:
        print(f"\033[34mFound specials in the series.\033[0m\n")
    elif include_specials and not specials_found:
        print(f"\033[33mNo specials found for this series.\033[0m\n")

    # Process the seasons and episodes
    for season in series_data.get("seasons", []):
        season_number = season.get("season_number")
        season_name = season.get("name", f"Season {season_number}")

        if season_number == 0 and not include_specials:
            continue

        season = Season(
            name=season_name,
            episodes={}
        )

        season_data = tmdb.get_season_details(series_id, season_number, locale)

        for episode in season_data.get("episodes", []):
            episode_number = episode.get("episode_number")
            episode_name = episode.get("name", f"Episode {episode_number}")

            season.episodes[episode_number] = episode_name

        print(f"\033[34mFound {len(season_data.get('episodes', []))} episodes in season {season_number}.\033[0m")

        series.seasons[season_number] = season

    return series


def create_series() -> Series:
    """ Creates a new series by fetching data from TMDB. """
    tmdb = TMDB()
    user_locale = input("Enter your locale (use ISO 639-1 and possibly ISO 3166-1) [en-US]: ").strip().lower() or "en-US"

    # Validate the locale format
    if not (re.match(r"^[a-z]{2}$", user_locale) or re.match(r'^[a-z]{2}-[A-Z]{2}$', user_locale)):
        raise ValueError("Invalid locale format. Please enter a valid locale format consisting of 639-1 and 3166-1 values separated by a hyphen (e.g., 'en' or 'en-US').")

    series_id, series_data = get_series(tmdb, user_locale)

    return process_series(tmdb, series_id, series_data, user_locale)


def save_series(series: Series) -> None:
    """ Saves the series data to a JSON file. """
    # Ensure the title is sanitized for use in a filename
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), sanitize(f"series-{series.title.replace(" ", "_")}.json"))

    try:
        series_dict = {
            "title": series.title,
            "specials": series.specials,
            "seasons": {
                str(season_number): {
                    "name": season.name,
                    "episodes": {str(episode_number): episode_name for episode_number, episode_name in season.episodes.items()}
                }
                for season_number, season in series.seasons.items()
            }
        }

        with open(path, "w", encoding="utf-8") as file:
            json.dump(series_dict, file, ensure_ascii=False, indent=2)

        print(f"\n\033[32mSeries map successfully saved to \"{path}\"!\033[0m")
    except Exception as e:
        raise Exception(f"An error occurred while saving the series to file '{path}': {e}")


def fetch_new_series_data() -> None:
    """ Fetches new series data and saves it to a file. """
    clear_screen()

    print(f"\033[35mCreating a new series...\033[0m\n")

    series = create_series()
    save_series(series)


def load_series(file_path: str) -> Series:
    """ Loads a series from a JSON file and returns a Series object. """
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        series = Series(
            title=data.get("title", "Unknown Series"),
            specials=data.get("specials", False),
            seasons={
                int(season_number): Season(
                    name=season_data.get("name", f"Season {season_number}"),
                    episodes={int(episode_number): episode_name for episode_number, episode_name in season_data.get("episodes", {}).items()}
                )
                for season_number, season_data in data.get("seasons", {}).items()
            }
        )

        return series
    except json.JSONDecodeError as e:
        raise ValueError(f"File '{file_path}' contains invalid JSON data: {e}")
    except Exception as e:
        raise Exception(f"An error occurred while loading the series from file '{file_path}': {e}")


def print_series_tree(series: Series) -> None:
    """ Prints the series tree in a structured format. """
    print(f"\nSpecials are \033[1m{"included" if series.specials else "not included"}\033[0m in the series file.\n")
    print(f"\033[1;36m{series.title}\033[0m")

    for season_number, season in sorted(series.seasons.items()):
        # Determine if this is the last season and take into account if specials are included
        is_last_season = season_number == len(series.seasons) - 1 if series.specials else season_number == len(series.seasons)
        total_episodes = len(season.episodes)

        season_prefix = "└─ " if is_last_season else "├─ "
        print(f"\033[1;34m{season_prefix}{season_number}. {season.name} ({total_episodes} episodes)\033[0m")

        # Determine the prefix base for the episodes based on whether this is the last season
        episode_prefix_base = "   " if is_last_season else "\033[1;34m│\033[0m  "

        for episode_number, episode_name in sorted(season.episodes.items()):
            is_last_episode = episode_number == total_episodes
            # Determine the prefix color based on whether the episode number is even or odd
            prefix_color = "\033[97m" if (episode_number % 2 == 0) else "\033[0m"

            episode_prefix = "└─ " if is_last_episode else "├─ "

            print(f"{episode_prefix_base}{prefix_color}{episode_prefix}{episode_number}. {episode_name}")

    print("\n\033[32mSeries tree printed successfully!\033[0m")


def print_series_tree_from_file() -> None:
    """ Prints the series tree from a file. """
    clear_screen()

    print(f"\033[35mPrinting a series tree from a file...\033[0m\n")

    file_path = input("Enter the path to the series file [./series.json]: ").strip() or "./series.json"

    series = load_series(file_path)
    print_series_tree(series)


def print_series_tree_from_tmdb() -> None:
    """ Prints the series tree from TMDB. """
    clear_screen()

    print(f"\033[35mPrinting a series tree from TMDB...\033[0m\n")

    series = create_series()
    print_series_tree(series)

    should_save = input("Do you want to additionally save the series tree to a file? (y/n): ").strip().lower() == "y"
    if should_save:
        save_series(series)


def main() -> None:
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
                fetch_new_series_data()
            case "2":
                print_series_tree_from_file()
            case "3":
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