# Blu-ray Release Calendar Script

## Project Overview
This project is a Python-based automation tool designed to monitor an IMDb watchlist and update an iCloud calendar with confirmed Blu-ray release dates. It runs as a Dockerized web application, featuring a simple dashboard and an automated daily scheduler.

**Core Logic:**
1.  **IMDb Scraper:** Fetches movie titles from a specific user watchlist.
2.  **Blu-ray.com Search:** Searches for each title on Blu-ray.com, visiting specific movie pages to find the earliest release date (parsing multiple date formats).
3.  **CalDAV Integration:** Connects to iCloud via CalDAV to check for existing events and add new "all-day" events for confirmed releases.

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
    *   `MovieScraper` class: Handles HTTP sessions, IMDb scraping, and robust date parsing from Blu-ray.com.
    *   `update_calendar()`: Orchestrates the scraping and CalDAV syncing.
*   **`app/routes.py`**: Defines the Flask routes:
    *   `/`: Renders the dashboard (`app/templates/index.html`).
    *   `/run`: Trigger endpoint for manual execution.
*   **`app/__init__.py`**: Application factory that initializes Flask and sets up the daily background job (8:00 AM).
*   **`test_scraper.py`**: A standalone script used during development for debugging the scraping logic without the full app overhead.

## Building and Running

### Prerequisites
*   Docker & Docker Compose installed.
*   iCloud App-Specific Password (required for CalDAV authentication).

### Configuration
Edit `docker-compose.yml` to set your credentials:
```yaml
environment:
  - ICLOUD_USERNAME=your_email@icloud.com
  - ICLOUD_PASSWORD=your_app_specific_password
  - IMDB_WATCHLIST_URL=https://www.imdb.com/user/...
```

### Commands

**Build and Start:**
```bash
docker-compose up --build
```

**Access Dashboard:**
Open browser to `http://localhost:5000`.

## Development Conventions
*   **Virtual Environment**: Use `.venv` for local development. VS Code will detect this automatically.
*   **Scraping Ethics**: The scraper includes `time.sleep(1)` delays to be polite to target servers.
*   **Logging**: Uses Python's standard `logging` module to track progress and errors.
*   **Error Handling**: The scraper is designed to fail gracefully (returning `None` or empty lists) rather than crashing the entire application if a specific page structure changes.
*   **Environment**: Configuration is strictly decoupled from code using environment variables.