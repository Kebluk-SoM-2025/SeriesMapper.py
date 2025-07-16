# SeriesMapper.py

This Python script fetches series metadata from The Movie Database (TMDB) API and maps it into a structured JSON format,
as shown in the example below:

```json
{
  "title": "Friends",
  "specials": false,
  "seasons": {
    "1": {
      "name": "Season 1",
      "episodes": {
        "1": "Pilot",
        "2": "The One with the Sonogram at the End"
      }
    }
  }
}
```

Data is provided by [The Movie Database (TMDB)](https://www.themoviedb.org/).

## Requirements

- Python 3.13.5 or higher
- `requests` package (version 2.32.4)
- TMDB API key

## Installation

1. Install Python 3.13.5 or higher from [python.org](https://www.python.org/).
2. Install the required package:
   ```bash
   pip install requests>=2.32.4
   ```
3. Get a TMDB API key from [TMDB's API settings](https://www.themoviedb.org/settings/api). You will probably need it
   later

## Usage

Run the script from the command line:

```bash
python SeriesMapper.py
```

The script prompts for a TMDB API key, a locale (e.g., `en-US`), and a series selection (by ID or title search). It then
fetches series data, including seasons and episodes, and saves it to a JSON file.

## Features

- Search for a series by title or provide a TMDB series ID directly.
- Include or exclude special episodes (e.g., season 0).
- Save series metadata (title, seasons, and episode names) to a JSON file with the series name.
- Interactive terminal interface with clickable links to TMDB pages (where supported).

## License

SeriesMapper.py is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE.txt) or
visit https://www.gnu.org/licenses/gpl-3.0.txt for details.

### Dependencies

- `requests`: Licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0.txt)
- TMDB API: Used under the [TMDB Terms of Use](https://www.themoviedb.org/terms-of-use)

## Notes

- Ensure compliance with TMDB’s Terms of Use when using their API, including non-commercial use and proper attribution.
- For consistent behavior, use `requests` version 2.x.x (install via `pip install requests>=2.32.4`).
- Source code is available for modification and redistribution under the GPL v3 license.