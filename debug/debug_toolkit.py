import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import time
import json

# Common headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.blu-ray.com/',
}

def get_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.cookies.set('listlayout_7', 'simple', domain='.blu-ray.com')
    # Use global country cookie for advanced search
    s.cookies.set('country', 'all', domain='.blu-ray.com')
    try:
        s.get("https://www.blu-ray.com/", timeout=10)
    except:
        pass
    return s

def debug_imdb_watchlist(url=None):
    if not url:
        # Try to load from ../config.json if possible, or use default
        try:
            with open('../config.json', 'r') as f:
                data = json.load(f)
                url = data.get('IMDB_WATCHLIST_URL')
        except: pass
        
    if not url:
        print("No URL found. Please enter one.")
        return

    print(f"\n--- Debugging IMDb Watchlist: {url} ---")
    try:
        r = requests.get(url, headers=HEADERS)
        print(f"Status: {r.status_code}")
        soup = BeautifulSoup(r.text, 'html.parser')
        
        items = soup.select('.ipc-metadata-list-summary-item')
        print(f"Found {len(items)} items.")
        
        for i, item in enumerate(items[:10]):
            title_el = item.select_one('.ipc-title__text')
            text_content = item.get_text()
            title = re.sub(r'^\d+\.\s+', '', title_el.text.strip()) if title_el else "Unknown"
            
            year_match = re.search(r'(19|20)\d{2}', text_content)
            year = year_match.group(0) if year_match else "N/A"
            
            is_tv = any(x in text_content for x in ["TV Series", "TV Mini Series", "TV Episode"])
            
            print(f"[{i}] {title} ({year}) | Type: {'TV' if is_tv else 'Movie'}")
    except Exception as e:
        print(f"Error: {e}")

def debug_search(title, year=None):
    print(f"\n--- Debugging Advanced Search: {title} ({year}) ---")
    session = get_session()
    search_url = "https://www.blu-ray.com/movies/search.php"
    params = {
        'keyword': title,
        'yearfrom': str(year) if year else '',
        'yearto': str(year) if year else '',
        'submit': 'Search',
        'action': 'search'
    }
    
    print(f"URL: {search_url}")
    print(f"Params: {params}")
    
    try:
        r = session.get(search_url, params=params)
        print(f"Status: {r.status_code}")
        print(f"Result URL: {r.url}")
        
        if '/movies/' in r.url and 'search.php' not in r.url:
            print("Redirected to Movie Page!")
            # Parse movie page logic could go here
            return

        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all('tr')
        print(f"Rows found: {len(rows)}")
        
        for i, tr in enumerate(rows):
            cells = tr.find_all('td')
            if not cells: continue
            
            row_text = tr.get_text()
            if year and f"({year})" not in row_text:
                continue

            link = tr.find('a', href=True)
            if not link or '/movies/' not in link['href']:
                continue
            
            link_text = link.get_text(" ", strip=True)
            norm_link = re.sub(r'\s+4K$', '', link_text, flags=re.IGNORECASE)
            
            print(f"[Row {i}] {link_text}")
            
            # Match Logic
            is_exact = False
            if norm_link.lower() == title.lower():
                is_exact = True
            else:
                no_parens = re.sub(r'\s*\(.*?\)', '', norm_link).strip()
                if no_parens.lower() == title.lower():
                    is_exact = True
            
            print(f"  > Exact Match: {is_exact}")
            
            # Check dates
            # (Simplified date regex for debug display)
            if re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', row_text):
                print(f"  > Contains potential date info.")

    except Exception as e:
        print(f"Error: {e}")

def main():
    while True:
        print("\n=== Debug Toolkit (Advanced) ===")
        print("1. Inspect IMDb Watchlist")
        print("2. Custom Search")
        print("0. Exit")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1': debug_imdb_watchlist()
        elif choice == '2':
            t = input("Title: ")
            y = input("Year (optional): ")
            y = int(y) if y.strip() else None
            debug_search(t, y)
        elif choice == '0': break
        else: print("Invalid choice.")

if __name__ == "__main__":
    main()
