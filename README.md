# Blu-ray Release Calendar Sync

An automated tool to sync your IMDb watchlist with Blu-ray.com release dates and add them to your iCloud calendar.

## Features

- **IMDb Watchlist Sync**: Automatically fetches movies from your public IMDb watchlist, filtering out TV shows.
- **Smart Date Finding**: Scrapes Blu-ray.com using advanced matching logic (Year filtering, Redirect handling, Global search) to find the earliest confirmed release date.
- **Real-Time "Poster Wall"**: A beautiful, dark-mode web interface that displays movie posters and updates their status live as they are scanned.
- **iCloud Integration**: Automatically adds all-day events to a dedicated "Blu-ray Releases" calendar via CalDAV.
- **In-App Settings**: Configure your IMDb URL, iCloud credentials, and UI Theme directly from the web interface.
- **Daily Automation**: Runs automatically every day at 8:00 AM using a background scheduler.
- **Dockerized**: Easy deployment using Docker and Docker Compose.

## Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- An **iCloud App-Specific Password** (Required for security; your main Apple ID password will not work for CalDAV).
    - Generate one at [appleid.apple.com](https://appleid.apple.com/) under the "App-Specific Passwords" section.

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Blu-ray-Release-Calendar-Script.git
   cd Blu-ray-Release-Calendar-Script
   ```

2. **Configure Environment Variables**:
   Open `docker-compose.yml` and update the `environment` section:
   ```yaml
   environment:
     - ICLOUD_USERNAME=your_apple_id@icloud.com
     - ICLOUD_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Your App-Specific Password
     - IMDB_WATCHLIST_URL=https://www.imdb.com/user/ur110300787/watchlist/
     - CALENDAR_NAME=Blu-ray Releases      # Optional: Name of the sub-calendar
   ```

3. **Start the application**:
   ```bash
   docker-compose up -d --build
   ```

## Usage

### Web Interface
Once the container is running, access the dashboard at:
**`http://localhost:5000`**

From the dashboard, you can:
- **Scan Now**: Triggers an immediate scrape. You will see posters appear and update in real-time.
- **Stop Scanning**: Interrupts the process at any time.
- **Settings**: Update your credentials, change the theme (Light/Dark/System), or change the monitored watchlist URL without restarting the container.
- **Click Posters**: Opens the movie's IMDb page in a new tab.

### Automation
The script is configured to run automatically every day at **08:00 AM** (container time). You don't need to keep the browser open for the scheduled tasks to run.

## How it Works

1. **Scraping**: Fetches your watchlist from IMDb, extracting titles and years.
2. **Matching**: Queries Blu-ray.com using a global search. It prioritizes exact title matches and strictly filters by year to avoid confusing remakes (e.g., *The Housemaid* 2010 vs 2025). It handles redirects for single results and parses list tables for multiple results.
3. **Calendar Sync**: Connects to iCloud via `caldav`. It adds future releases to your calendar and updates existing events if release dates change.

## Development & Debugging

If you want to test the scraper logic without running the full web app/docker:
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Run the debug toolkit: `python debug_toolkit.py` - This interactive tool allows you to test the scraper against specific movies to diagnose missing dates.

## License
MIT