# Blu-ray Release Calendar Sync

An automated tool to sync your IMDb watchlist with Blu-ray.com release dates and add them to your iCloud calendar.

## Features

- **IMDb Watchlist Sync**: Automatically fetches movies from your public IMDb watchlist.
- **Smart Date Finding**: Searches Blu-ray.com for the earliest confirmed release date for each film.
- **iCloud Integration**: Automatically adds all-day events to a dedicated "Blu-ray Releases" calendar via CalDAV.
- **Web Dashboard**: A simple Flask-based UI to monitor status and manually trigger syncs.
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
- View the results of the last sync.
- Check the current status (Idle or Running).
- Click **"Run Now"** to start a manual sync immediately.

### Automation
The script is configured to run automatically every day at **08:00 AM** (container time). You don't need to keep the browser open for the scheduled tasks to run.

## How it Works

1. **Scraping**: It uses `BeautifulSoup4` to parse your IMDb watchlist.
2. **Matching**: It queries Blu-ray.com for each title. To ensure accuracy, it visits individual movie pages to extract dates from the "Release Date" labels or text content.
3. **Calendar Sync**: It uses the `caldav` library to connect to iCloud. It checks if an event with the movie title already exists on the release date to prevent duplicates.

## Development & Debugging

If you want to test the scraper logic without running the full web app/docker:
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Run the test script: `python test_scraper.py`

## License
MIT
