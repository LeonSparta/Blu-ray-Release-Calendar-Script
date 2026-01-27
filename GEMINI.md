# Blu-ray Release Calendar Script

## Project Overview
This project is a Python-based automation tool designed to monitor an IMDb watchlist and update an iCloud calendar with confirmed Blu-ray release dates. It runs as a Dockerized web application, featuring a real-time "Poster Wall" dashboard, settings management, and an automated daily scheduler.

**Core Logic:**
1.  **IMDb Scraper:** Fetches movie titles, years, and posters from a specific user watchlist, filtering out TV shows.
2.  **Blu-ray.com Search:** Searches for each title on Blu-ray.com using a global quicksearch logic that handles:
    *   **Strict Year Filtering:** Matches movie years (e.g. `(2025)`) to avoid false positives with remakes.
    *   **Exact & Partial Title Matching:** Normalizes titles (stripping regions/subtitles) to find the best match.
    *   **Redirect Handling:** Detects if Blu-ray.com redirects to a specific movie page (single result) and parses the date from there.
    *   **Table Parsing:** Efficiently extracts dates from the search results list view.
3.  **CalDAV Integration:** Connects to iCloud via CalDAV to check for existing events and add new "all-day" events for confirmed future releases.
4.  **Real-Time UI:** The frontend polls the backend to display scanning progress, posters, and release dates live.

## Technology Stack
*   **Language:** Python 3.11
*   **Web Framework:** Flask
*   **Scraping:** `requests`, `beautifulsoup4`
*   **Scheduling:** `APScheduler`
*   **Calendar:** `caldav`
*   **Containerization:** Docker, Docker Compose

## Architecture & Key Files

*   **`docker-compose.yml`**: Defines the service configuration, port mapping (5000:5000), and environment variables.
*   **`Dockerfile`**: Builds the Python environment.
*   **`app/tasks.py`**: The core logic engine. Contains:
    *   `MovieScraper` class: Handles HTTP sessions, cookies (forcing list view), and robust scraping logic.
    *   `process_watchlist_realtime()`: Orchestrates the scraping and sync process, updating a shared state object.
    *   `sync_to_calendar()`: Handles the CalDAV operations.
*   **`app/routes.py`**: Defines the Flask routes and API endpoints (`/status`, `/run`, `/stop`, `/settings`).
*   **`app/config.py`**: Manages configuration via `SettingsManager`, supporting both environment variables and a persistent `config.json` file.
*   **`app/templates/index.html`**: The single-page application frontend with poster grid, settings modal, and dark/light theme support.
*   **`debug_toolkit.py`**: A consolidated CLI tool for testing individual scraper components (IMDb parsing, specific movie search debugging).

## Building and Running

### Prerequisites
*   Docker & Docker Compose installed.
*   iCloud App-Specific Password (required for CalDAV authentication).

### Configuration
You can configure the application via:
1.  **Environment Variables**: Edit `docker-compose.yml`.
2.  **Web Interface**: Click "Settings" on the dashboard to edit credentials and theme at runtime.

### Commands

**Build and Start (Docker):**
```bash
docker-compose up --build
```

**Run Locally (Development):**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
.venv\Scripts\flask run
```

**Access Dashboard:**
Open browser to `http://localhost:5000`.

## Development Conventions
*   **Virtual Environment**: Use `.venv` for local development.
*   **Scraping Ethics**: The scraper includes `time.sleep(2)` delays and retry logic to be polite and avoid rate limits.
*   **State Management**: The Flask app uses a simple in-memory state dictionary for the progress bar, which is sufficient for a single-user tool.
*   **Debug Tools**: Use `debug_toolkit.py` to diagnose why specific movies aren't being found.
