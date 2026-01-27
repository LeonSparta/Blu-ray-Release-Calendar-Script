import requests
from bs4 import BeautifulSoup
import caldav
from datetime import datetime, date
import time
import re
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.blu-ray.com/',
            'Connection': 'keep-alive'
        })
        # Visit homepage to set cookies
        try:
            self.session.get("https://www.blu-ray.com/")
        except Exception as e:
            logger.error(f"Failed to init session: {e}")

    def get_imdb_watchlist(self, url):
        logger.info(f"Fetching IMDb watchlist: {url}")
        try:
            r = requests.get(url, headers={'User-Agent': self.session.headers['User-Agent']})
            if r.status_code != 200:
                logger.error(f"IMDb failed: {r.status_code}")
                return []
            
            soup = BeautifulSoup(r.text, 'html.parser')
            titles = []
            
            # Selector for modern IMDb lists
            elements = soup.select('.ipc-title__text')
            for el in elements:
                text = el.text.strip()
                # Remove leading numbers (e.g. "1. Movie Title")
                clean_text = re.sub(r'^\d+\.\s+', '', text)
                if clean_text and clean_text not in ["Recently viewed", "Menu", "Watchlist"]:
                    titles.append(clean_text)
            
            # Fallback for older lists
            if not titles:
                elements = soup.select('.lister-item-header a')
                for el in elements:
                    titles.append(el.text.strip())
                    
            logger.info(f"Found {len(titles)} movies on IMDb.")
            return list(set(titles)) # Deduplicate
        except Exception as e:
            logger.error(f"Error fetching IMDb: {e}")
            return []

    def search_bluray_date(self, title):
        logger.info(f"Searching Blu-ray.com for: {title}")
        base_url = "https://www.blu-ray.com/search/"
        params = {
            'quicksearch': '1',
            'quicksearch_country': 'all',
            'quicksearch_keyword': title,
            'section': 'bluraymovies'
        }
        
        try:
            time.sleep(1) # Be polite
            r = self.session.get(base_url, params=params)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Strategy:
            # 1. Look for date in search results directly (if we can find the pattern)
            # 2. If not found, visit the first few movie links.
            
            # Regex for date: Feb 03 2026, Feb 3, 2026, 2026-02-03, Feb 03, 2026
            date_patterns = [
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}',
                r'\d{4}-\d{2}-\d{2}'
            ]
            
            # Check full text first (fastest)
            # But we need to be careful not to pick up unrelated dates.
            # Let's try to find movie links first.
            
            movie_links = []
            # Find links that look like movie pages
            # href="/movies/Title..."
            for a in soup.find_all('a', href=True):
                if '/movies/' in a['href'] and title.lower() in a.text.lower():
                    full_url = a['href'] if a['href'].startswith('http') else f"https://www.blu-ray.com{a['href']}"
                    movie_links.append(full_url)
            
            # Unique links, keeping order
            movie_links = list(dict.fromkeys(movie_links))
            
            if not movie_links:
                logger.info("No movie links found in search.")
                return None

            earliest_date = None
            
            # check up to 3 results
            for link in movie_links[:3]:
                logger.info(f"Checking movie page: {link}")
                try:
                    time.sleep(1)
                    r_movie = self.session.get(link)
                    soup_movie = BeautifulSoup(r_movie.text, 'html.parser')
                    
                    # Look for "Release Date" or just the date patterns
                    text_content = soup_movie.get_text()
                    
                    found_date = None
                    for pattern in date_patterns:
                        matches = re.findall(pattern, text_content)
                        for match in matches:
                            # Normalize match to date object
                            try:
                                # parser handles many formats
                                from dateutil import parser
                                dt = parser.parse(match if isinstance(match, str) else match[0]) # regex might return tuple
                                # Filter out past dates? No, user might want to know about recent releases.
                                # Filter out way future/past (sanity check)?
                                if 2024 < dt.year < 2030:
                                    if found_date is None or dt < found_date:
                                        found_date = dt
                            except:
                                continue
                    
                    if found_date:
                        logger.info(f"Found date {found_date.date()} for {title}")
                        if earliest_date is None or found_date < earliest_date:
                            earliest_date = found_date
                            
                except Exception as e:
                    logger.error(f"Error checking link {link}: {e}")
            
            return earliest_date

        except Exception as e:
            logger.error(f"Error searching Blu-ray: {e}")
            return None

def update_calendar():
    scraper = MovieScraper()
    titles = scraper.get_imdb_watchlist(Config.IMDB_WATCHLIST_URL)
    
    if not titles:
        return "No titles found or error fetching IMDb."

    results = []
    
    # Connect to iCloud
    client = None
    calendar = None
    if Config.ICLOUD_USERNAME and Config.ICLOUD_PASSWORD:
        try:
            client = caldav.DAVClient(
                url=Config.ICLOUD_URL,
                username=Config.ICLOUD_USERNAME,
                password=Config.ICLOUD_PASSWORD
            )
            principal = client.principal()
            calendars = principal.calendars()
            for cal in calendars:
                if cal.name == Config.CALENDAR_NAME:
                    calendar = cal
                    break
            if not calendar:
                logger.info(f"Calendar {Config.CALENDAR_NAME} not found, creating it.")
                calendar = principal.make_calendar(name=Config.CALENDAR_NAME)
        except Exception as e:
            logger.error(f"Calendar Connection Error: {e}")
            return f"Calendar Error: {e}"
    else:
        logger.warning("No iCloud credentials provided. Skipping calendar update.")

    for title in titles:
        # Check if we already have this event (optimization)
        # This is tricky without date, so we might skip optimization or check all events
        # simpler: just scrape and check if event exists on that date
        
        release_date = scraper.search_bluray_date(title)
        
        if release_date:
            status = "Found: " + str(release_date.date())
            if calendar:
                # Check for existing event
                try:
                    # search events
                    events = calendar.date_search(start=release_date, end=release_date)
                    exists = False
                    for event in events:
                        # event.instance.vevent.summary.value
                        # Accessing icalendar object
                        vevent = event.instance.vevent
                        if vevent.summary.value == title:
                            exists = True
                            break
                    
                    if not exists:
                        calendar.save_event(
                            dtstart=release_date.date(),
                            summary=title,
                            description=f"Blu-ray release for {title}. Found via script."
                        )
                        status += " (Added to Calendar)"
                    else:
                        status += " (Already in Calendar)"
                except Exception as e:
                    logger.error(f"Error adding to calendar: {e}")
                    status += f" (Calendar Error: {e})"
        else:
            status = "No date found"
            
        results.append({'title': title, 'status': status})
        
    return results
