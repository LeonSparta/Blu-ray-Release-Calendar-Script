# Blu-ray Release Calendar Script

A Dockerized Python web application that automatically scrapes IMDb watchlists, finds confirmed Blu-ray release dates (globally), and syncs them to an iCloud calendar.

## Features

*   **🎬 IMDb Watchlist Sync**: Automatically fetches movies from a public or private IMDb watchlist.
*   **🌍 Global Blu-ray Search**: Uses Blu-ray.com's **Advanced Search** with global filters to find release dates from any region (US, UK, DE, etc.).
*   **📅 iCloud Calendar Integration**: 
    *   Creates "All Day" events for confirmed releases.
    *   **Smart Rescheduling**: Automatically detects date changes, deletes the old event, and creates a new one to ensure clean syncing.
    *   **Duplicate Prevention**: Checks for existing events on the target day before adding.
*   **🧠 Intelligent Filtering**:
    *   **1-Year Sanity Check**: Automatically filters out films released more than 1 year ago to keep the view focused on upcoming/recent titles.
    *   **Strict Matching**: Verifies Title + Year to avoid false positives with remakes.
    *   **Redirect Handling**: Handles cases where Blu-ray.com redirects directly to a movie page.
*   **🖥️ Real-Time Dashboard**:
    *   Visual "Poster Wall" of your watchlist.
    *   Live scanning progress.
    *   Settings management (iCloud credentials, Scan Time, Theme).
    *   Dark/Light/System theme support.
*   **🐳 Docker Ready**: easy deployment with Docker Compose.

## Prerequisites

*   **iCloud App-Specific Password**: Required for CalDAV access. [Generate one here](https://appleid.apple.com/).
*   **IMDb Watchlist**: Must be a public list or accessible via the provided URL.
*   **Docker** (optional, for containerized run).

## Installation & Usage

### 1. Local Development (Windows/Linux/Mac)

```bash
# Clone repository
git clone <repo-url>
cd Blu-ray-Release-Calendar-Script

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
flask run
```
Access the dashboard at `http://localhost:5000`.

### 2. Docker

```bash
docker-compose up --build -d
```

## Configuration

Settings can be managed directly via the **Web UI** (click the "Settings" button):

*   **Daily Refresh Time**: Set the time for the automated background scan.
*   **IMDb Watchlist URL**: Full URL to your watchlist (e.g., `https://www.imdb.com/user/ur.../watchlist`).
*   **iCloud Credentials**: Username and App-Specific Password.

*Note: Credentials are stored locally in `config.json` (excluded from git).*

## How It Works

1.  **Scrape**: The app fetches your IMDb watchlist using `requests` and `BeautifulSoup`.
2.  **Filter**: It discards TV shows and films released >1 year ago.
3.  **Search**: For each movie, it performs an Advanced Search on Blu-ray.com, setting cookies to ensure **Global** results are returned.
4.  **Sync**: 
    *   If a date is found, it connects to iCloud via `caldav`.
    *   It checks if the event exists.
    *   If the date changed, it **deletes** the old event and **creates** a new one.
    *   If new, it adds it.

## Troubleshooting

*   **"iCloud: Error"**: Check your App-Specific Password. Ensure the calendar name defined in `config.py` (default: "Blu-ray Releases") exists or can be created.
*   **"Released (Will Hide)"**: The movie has a release date in the past and will be removed from the active view.

## License
MIT
