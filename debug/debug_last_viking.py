import sys
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Add parent to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.tasks import MovieScraper

def debug_last_viking():
    print("--- Debugging 'The Last Viking' ---")
    scraper = MovieScraper()
    
    title = "The Last Viking"
    year = 2025 # As per user report
    
    print(f"Searching for: {title} ({year})")
    
    # 1. Manually Run Search Logic (Advanced Search)
    search_url = "https://www.blu-ray.com/movies/search.php"
    params = {
        'keyword': title,
        'yearfrom': str(year),
        'yearto': str(year),
        'submit': 'Search',
        'action': 'search'
    }
    
    print(f"URL: {search_url}")
    r = scraper.session.get(search_url, params=params)
    print(f"Status: {r.status_code}")
    print(f"Result URL: {r.url}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('tr')
    print(f"Rows found: {len(rows)}")
    
    date_patterns = [
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}',
        r'\d{4}-\d{2}-\d{2}'
    ]
    
    candidates = []
    
    for i, tr in enumerate(rows):
        cells = tr.find_all('td')
        if not cells: continue
        
        row_text = tr.get_text(separator=' ', strip=True)
        link = tr.find('a', href=True)
        if not link or '/movies/' not in link['href']: continue
        
        link_text = link.get_text(strip=True)
        
        # Check matching
        # ... (logic from tasks.py) ...
        norm_link = re.sub(r'\s+4K$', '', link_text, flags=re.IGNORECASE)
        match = (norm_link.lower() == title.lower()) or (title.lower() in norm_link.lower())
        
        if not match: continue
        
        print(f"\n[Row {i}] {link_text}")
        print(f"  > Content: {row_text}")
        
        # Extract dates
        for td in cells:
            td_text = td.get_text(strip=True)
            for pattern in date_patterns:
                matches = re.findall(pattern, td_text)
                if matches:
                    print(f"  > Found Date String: {matches[0]}")
                    try:
                        from dateutil import parser
                        dt = parser.parse(matches[0])
                        print(f"  > Parsed: {dt.date()}")
                        candidates.append(dt)
                    except: pass

    if candidates:
        print(f"\nMin Candidate: {min(candidates)}")
    else:
        print("\nNo candidates found.")

if __name__ == "__main__":
    debug_last_viking()
