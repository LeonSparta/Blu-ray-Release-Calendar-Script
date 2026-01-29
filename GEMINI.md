# Blu-ray Release Calendar Script

## Project Overview
This project is a Python-based automation tool designed to monitor an IMDb watchlist and update an iCloud calendar with confirmed Blu-ray release dates. It runs as a Dockerized web application, featuring a real-time "Poster Wall" dashboard, settings management, and an automated daily scheduler.

**Core Logic:**
1.  **IMDb Scraper:** Fetches movie titles, years, and posters. **Filters out films released >1 year ago** immediately to optimize performance.
2.  **Blu-ray.com Search:** 
    *   Uses **Advanced Search** (`/movies/search.php`) with `yearfrom`/`yearto` parameters.
    *   **Global Scope:** Sets `country=all` cookie to ensure international releases (e.g., German mediabooks) are found.
    *   **Strict Matching:** Verifies Title and Year. Also checks for titles appearing exactly within parentheses (e.g. "Foreign Title (English Title)").
3.  **CalDAV Integration (iCloud):**
    *   Uses `caldav` library with `icalendar` component manipulation.
    *   **Robust De-Duplication:** Before adding/updating, it performs a **Wide Range Search** (Current Year + Next Year) to find *any* existing events with the same title, even if they are on the wrong date.
    *   **Clean Rescheduling:** If an event is found on the wrong date, it is explicitly **deleted** before the new one is created.
    *   **All-Day Events:** Correctly sets `dtstart` and `dtend` (start + 1 day) to satisfy iCloud requirements.
4.  **Real-Time UI:** Flask-based polling (`/status`) with a responsive Grid layout. Features **Differential DOM Updates** to prevent UI flickering/jumping during scans.

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
    *   `sync_to_calendar`: Robust CalDAV logic with aggressive de-duplication (Wide Range Search fallback).
    *   `process_watchlist_realtime`: Orchestrator with 1-year sanity check and UI state management.
*   **`app/routes.py`**: Flask endpoints (`/run`, `/settings`, `/status`). Handles scheduler updates.
*   **`app/config.py`**: `SettingsManager` for `data/config.json` persistence.
*   **`utilities/reference_script.py`**: Reference logic for CalDAV (archived).
*   **`debug/`**: directory containing debug tools.

## Setup & Configuration
*   **Credentials:** Stored in `data/config.json` (git-ignored, volume-mounted).
*   **Environment:** `.venv` for local, `Dockerfile` for container.

## Recent Changes (Jan 2026)
1.  **Global Search Fix:** Switched to Advanced Search + Cookies to find "No Other Choice" and "The Housemaid" (German releases).
2.  **iCloud Fixes:** Resolved `403 Forbidden` / `404` errors by correctly setting `dtend` for all-day events.
3.  **Aggressive De-Duplication:** Implemented a Wide Range Search (Current + Next Year) to detect and delete duplicate events on wrong dates, fixing the "Orphaned Event" issue.
4.  **UI Polish:** Implemented differential DOM updates to stop the movie cards from jumping/flickering during scans.
5.  **Config Relocation:** Moved `config.json` to `data/` folder for easier Docker volume management.
