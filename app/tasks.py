import requests
from bs4 import BeautifulSoup
import caldav
from datetime import datetime, date
import time
import re
from app.config import Config, SettingsManager
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
        })
        self.session.cookies.set('listlayout_7', 'simple', domain='.blu-ray.com')
        try:
            self.session.get("https://www.blu-ray.com/", timeout=10)
        except Exception as e:
            logger.error(f"Failed to init session: {e}")

    def get_imdb_watchlist(self, url):
        logger.info(f"Fetching IMDb watchlist: {url}")
        try:
            r = requests.get(url, headers={'User-Agent': self.session.headers['User-Agent']})
            if r.status_code != 200:
                return []
            
            soup = BeautifulSoup(r.text, 'html.parser')
            movies = []
            
            items = soup.select('.ipc-metadata-list-summary-item')
            if items:
                for item in items:
                    text_content = item.get_text()
                    if any(x in text_content for x in ["TV Series", "TV Mini Series", "TV Episode"]):
                        continue
                    
                    title_el = item.select_one('.ipc-title__text')
                    if title_el:
                        text = title_el.text.strip()
                        title = re.sub(r'^\d+\.\s+', '', text)
                        if title in ["Recently viewed", "Menu", "Watchlist"]:
                            continue
                        
                        year = None
                        year_match = re.search(r'(19|20)\d{2}', text_content)
                        if year_match:
                            year = int(year_match.group(0))

                        imdb_url = None
                        link_parent = title_el.find_parent('a')
                        if link_parent:
                            href = link_parent.get('href')
                            if href:
                                imdb_url = f"https://www.imdb.com{href.split('?')[0]}"

                        poster_url = None
                        img_el = item.select_one('img.ipc-image')
                        if img_el and img_el.get('src'):
                            src = img_el.get('src')
                            if "@" in src:
                                base = src.split("@")[0]
                                poster_url = f"{base}@._V1_QL75_UX380_.jpg"
                            else:
                                poster_url = src
                        
                        movies.append({
                            'title': title,
                            'year': year,
                            'poster_url': poster_url,
                            'imdb_url': imdb_url
                        })
            
            unique_movies = {m['title']: m for m in movies}.values()
            return list(unique_movies)
        except Exception as e:
            logger.error(f"Error fetching IMDb: {e}")
            return []

    def _parse_movie_page(self, soup):
        """Helper to extract date from a specific movie page."""
        date_patterns = [
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        # Strategy 1: "Release date" label
        release_label = soup.find(string=re.compile("Release date", re.IGNORECASE))
        if release_label:
            container = release_label.parent.parent
            if container:
                container_text = container.get_text()
                for pattern in date_patterns:
                    matches = re.findall(pattern, container_text)
                    if matches:
                        try:
                            from dateutil import parser
                            dt = parser.parse(matches[0])
                            if 2020 <= dt.year < 2030:
                                return dt
                        except: pass
        
        # Strategy 2: Fallback text search
        text_content = soup.get_text()
        for pattern in date_patterns:
            matches = re.findall(pattern, text_content)
            for match in matches:
                try:
                    from dateutil import parser
                    dt = parser.parse(match)
                    if 2024 <= dt.year < 2030:
                        return dt
                except: continue
        return None

    def search_bluray_date(self, title, year=None):
        logger.info(f"Searching Blu-ray.com for: {title} ({year})")
        
        # Use Quicksearch for ALL countries
        search_url = "https://www.blu-ray.com/search/"
        params = {
            'quicksearch': '1',
            'quicksearch_country': 'all',
            'quicksearch_keyword': title,
            'section': 'bluraymovies'
        }
        
        try:
            time.sleep(2)
            
            r = None
            for attempt in range(3):
                try:
                    r = self.session.get(search_url, params=params, timeout=15)
                    if r.status_code == 200:
                        break
                except requests.RequestException:
                    pass
                time.sleep(2 * (attempt + 1))
            
            if not r or r.status_code != 200:
                return None

            # Detect Redirect to Movie Page
            if '/movies/' in r.url and 'search/' not in r.url:
                logger.info(f"Redirected to movie page: {r.url}")
                soup = BeautifulSoup(r.text, 'html.parser')
                return self._parse_movie_page(soup)

            # Process Search Results List
            soup = BeautifulSoup(r.text, 'html.parser')
            
            date_patterns = [
                r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}',
                r'\d{4}-\d{2}-\d{2}'
            ]
            
            candidates = []
            rows = soup.find_all('tr')
            for tr in rows:
                cells = tr.find_all('td')
                if not cells: continue
                
                row_text = tr.get_text()
                
                # STRICT Year Check
                if year and f"({year})" not in row_text:
                    continue

                link = tr.find('a', href=True)
                if not link or '/movies/' not in link['href']:
                    continue
                
                link_text = link.get_text(" ", strip=True)
                norm_link_text = re.sub(r'\s+4K$', '', link_text, flags=re.IGNORECASE)
                
                is_exact = False
                is_partial = False
                
                if norm_link_text.lower() == title.lower():
                    is_exact = True
                else:
                    no_parens = re.sub(r'\s*\(.*?\)', '', norm_link_text).strip()
                    if no_parens.lower() == title.lower():
                        is_exact = True
                    elif title.lower() in norm_link_text.lower():
                        is_partial = True
                
                if not (is_exact or is_partial):
                    continue
                
                row_date = None
                for td in cells:
                    td_text = td.get_text(strip=True)
                    for pattern in date_patterns:
                        matches = re.findall(pattern, td_text)
                        if matches:
                            try:
                                from dateutil import parser
                                dt = parser.parse(matches[0])
                                # Widen sanity check to allow detecting past releases (e.g. 2022)
                                if 2020 <= dt.year < 2030:
                                    if row_date is None or dt < row_date:
                                        row_date = dt
                            except: pass
                
                if row_date:
                    candidates.append((row_date, is_exact))

            if candidates:
                exact_matches = [c[0] for c in candidates if c[1]]
                if exact_matches:
                    return min(exact_matches)
                else:
                    return min([c[0] for c in candidates])

            # Fallback (Manual link check if list parsing failed but no redirect happened)
            return None

        except Exception as e:
            logger.error(f"Error searching Blu-ray: {e}")
            return None

def sync_to_calendar(movie_data, settings):
    username = settings.get('ICLOUD_USERNAME')
    password = settings.get('ICLOUD_PASSWORD')
    calendar_name = Config().CALENDAR_NAME
    icloud_url = Config().ICLOUD_URL

    if not (username and password): return "Skipped"

    try:
        client = caldav.DAVClient(url=icloud_url, username=username, password=password)
        principal = client.principal()
        calendar = next((cal for cal in principal.calendars() if cal.name == calendar_name), None)
        if not calendar: calendar = principal.make_calendar(name=calendar_name)
        
        title, release_date = movie_data['title'], movie_data['release_date']
        found_events = calendar.search(summary=title, event=True, expand=False)
        existing_event = next((e for e in found_events if hasattr(e.vobject.instance.vevent, 'summary') and e.vobject.instance.vevent.summary.value == title), None)
        
        if existing_event:
            cur = existing_event.vobject.instance.vevent.dtstart.value
            if isinstance(cur, datetime): cur = cur.date()
            if cur != release_date.date():
                existing_event.vobject.instance.vevent.dtstart.value = release_date.date()
                existing_event.save()
                return "Updated"
            return "Synced"
        else:
            calendar.save_event(dtstart=release_date.date(), summary=title, description=f"Blu-ray release for {title}.")
            return "Added"
    except Exception as e:
        return f"Error"

def process_watchlist_realtime(state_ref):
    settings = SettingsManager.load_settings()
    watchlist_url = settings.get('IMDB_WATCHLIST_URL') or Config().IMDB_WATCHLIST_URL
    scraper = MovieScraper()
    
    if state_ref.get('stop_requested'): return

    movies_raw = scraper.get_imdb_watchlist(watchlist_url)
    state_ref['movies'] = [{'title': m['title'], 'poster_url': m['poster_url'], 'imdb_url': m.get('imdb_url', '#'), 'release_date': 'Searching...', 'sync_status': 'Pending', 'year': m.get('year')} for m in movies_raw]
    state_ref['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if state_ref.get('stop_requested'): return

    icloud_connected = False
    if settings.get('ICLOUD_USERNAME') and settings.get('ICLOUD_PASSWORD'):
        try:
            client = caldav.DAVClient(url=Config().ICLOUD_URL, username=settings.get('ICLOUD_USERNAME'), password=settings.get('ICLOUD_PASSWORD'))
            client.principal().calendars()
            icloud_connected = True
            state_ref['icloud_status'] = "Connected"
        except Exception as e:
            state_ref['icloud_status'] = f"Error: {str(e)}"
    else:
        state_ref['icloud_status'] = "Not Configured"

    indices_to_remove = []
    
    for i, m in enumerate(state_ref['movies']):
        if state_ref.get('stop_requested'):
            m['release_date'] = "Stopped"
            return 

        date_obj = scraper.search_bluray_date(m['title'], m.get('year'))
        if date_obj:
            m['release_date'] = date_obj.strftime("%Y-%m-%d")
            
            if date_obj.date() < date.today():
                indices_to_remove.append(i)
                m['sync_status'] = "Released (Will Hide)"
            else:
                m_data_for_sync = m.copy()
                m_data_for_sync['release_date'] = date_obj
                m['sync_status'] = sync_to_calendar(m_data_for_sync, settings) if icloud_connected else "N/A"
        else:
            m['release_date'] = "TBA"
            m['sync_status'] = "N/A"
            
        state_ref['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for index in sorted(indices_to_remove, reverse=True):
        state_ref['movies'].pop(index)
    
    state_ref['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def update_calendar():
    dummy_state = {}
    process_watchlist_realtime(dummy_state)
    return dummy_state.get('movies', [])
