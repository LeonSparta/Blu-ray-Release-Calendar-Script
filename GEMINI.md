# Blu-ray Release Calendar Script

## Project Overview
This project is a Python-based automation tool designed to monitor an IMDb watchlist and update an iCloud calendar with confirmed Blu-ray release dates. It runs as a Dockerized web application, featuring a real-time "Poster Wall" dashboard, settings management, and an automated daily scheduler.

**Core Logic:**
1.  **IMDb Scraper:** Fetches movie titles, years, and posters. **Filters out films released >1 year ago** immediately to optimize performance.
2.  **Blu-ray.com Search:** 
    *   Uses **Advanced Search** (`/movies/search.php`) with `yearfrom`/`yearto` parameters.
    *   **Global Scope:** Sets `country=all` cookie to ensure international releases (e.g., German mediabooks) are found.
    *   **Strict Matching:** Verifies Title and Year exact matches.
3.  **CalDAV Integration (iCloud):**
    *   Uses `caldav` library with `icalendar` component manipulation.
    *   **Rescheduling:** If a release date changes, the old event is **deleted** and a new one is created.
    *   **All-Day Events:** Correctly sets `dtstart` and `dtend` (start + 1 day) to satisfy iCloud requirements.
4.  **Real-Time UI:** Flask-based polling (`/status`) with a responsive Grid layout.

## Technology Stack
*   **Language:** Python 3.11
*   **Web Framework:** Flask
*   **Scraping:** `requests`, `beautifulsoup4`
*   **Scheduling:** `APScheduler`
*   **Calendar:** `caldav`, `icalendar`
*   **Containerization:** Docker, Docker Compose

## Architecture & Key Files

*   **`app/tasks.py`**: The core logic engine.
    *   `MovieScraper`: Handles Advanced Search and Global Cookie management.
    *   `sync_to_calendar`: Robust CalDAV logic with duplicate detection and delete-replace update strategy.
    *   `process_watchlist_realtime`: Orchestrator with 1-year sanity check.
*   **`app/routes.py`**: Flask endpoints (`/run`, `/settings`, `/status`). Handles scheduler updates.
*   **`app/config.py`**: `SettingsManager` for `config.json` persistence.
*   **`utilities/reference_script.py`**: Reference logic for CalDAV (archived).
*   **`debug/`**: directory containing debug tools (`debug_toolkit.py`, etc.).

## Setup & Configuration
*   **Credentials:** Stored in `config.json` (git-ignored).
*   **Environment:** `.venv` for local, `Dockerfile` for container.

## Recent Changes (Jan 2026)
1.  **Global Search Fix:** Switched to Advanced Search + Cookies to find "No Other Choice" and "The Housemaid" (German releases).
2.  **iCloud Fixes:** Resolved `403 Forbidden` / `404` errors by correctly setting `dtend` for all-day events and using `icalendar_component` for property access.
3.  **Clean Rescheduling:** Implemented "Delete Old -> Create New" logic for date changes.
4.  **Optimization:** Added pre-fetch filtering to exclude movies >1 year old from the UI entirely.
5.  **UX:** Added Time Picker for daily scan and removed "Gear" icon from settings button.