import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import time
import subprocess
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
    try:
        s.get("https://www.blu-ray.com/", timeout=10)
    except:
        pass
    return s

def debug_imdb_watchlist(url=None):
    if not url:
        url = "https://www.imdb.com/user/ur110300787/watchlist/?ref_=hm_nv_urwls_all&sort=release_date%2Cdesc"
    
    print(f"\n--- Debugging IMDb Watchlist: {url} ---")
    try:
        r = requests.get(url, headers=HEADERS)
        print(f"Status: {r.status_code}")
        soup = BeautifulSoup(r.text, 'html.parser')
        
        items = soup.select('.ipc-metadata-list-summary-item')
        print(f"Found {len(items)} items.")
        
        for i, item in enumerate(items[:5]):
            title_el = item.select_one('.ipc-title__text')
            title = re.sub(r'^\d+\.\s+', '', title_el.text.strip()) if title_el else "Unknown"
            text_content = item.get_text()
            
            year_match = re.search(r'(19|20)\d{2}', text_content)
            year = year_match.group(0) if year_match else "N/A"
            
            is_tv = any(x in text_content for x in ["TV Series", "TV Mini Series", "TV Episode"])
            
            print(f"[{i}] {title} ({year}) | Type: {'TV' if is_tv else 'Movie'}")
    except Exception as e:
        print(f"Error: {e}")

def debug_search(title, year=None):
    print(f"\n--- Debugging Blu-ray Search: {title} ({year}) ---")
    session = get_session()
    search_url = "https://www.blu-ray.com/search/"
    params = {
        'quicksearch': '1',
        'quicksearch_country': 'all',
        'quicksearch_keyword': title,
        'section': 'bluraymovies'
    }
    
    try:
        r = session.get(search_url, params=params)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all('tr')
        
        date_patterns = [
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        candidates = []
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
                        row_date = matches[0]
            
            if row_date:
                candidates.append((row_date, is_exact, link_text))

        if not candidates:
            print("No candidates found.")
        else:
            for d, exact, full_name in candidates:
                print(f"Date: {d:15} | Exact: {str(exact):5} | Name: {full_name}")
    except Exception as e:
        print(f"Error: {e}")

def verify_flask_app():
    print("\n--- Verifying Flask App (Manual Check) ---")
    print("This will attempt to connect to http://127.0.0.1:5000/status")
    try:
        r = requests.get("http://127.0.0.1:5000/status", timeout=2)
        data = r.json()
        print(f"App is running. Movies in state: {len(data.get('movies', []))}")
        print(f"iCloud Status: {data.get('icloud_status')}")
    except:
        print("Could not connect to app. Make sure it's running in another terminal.")

def main():
    while True:
        print("\n=== Consolidated Debug Toolkit ===")
        print("1. Inspect IMDb Watchlist")
        print("2. Debug 'The Housemaid' (2025)")
        print("3. Debug 'Nuremberg' (2025)")
        print("4. Debug 'The Last Viking' (2025)")
        print("5. Custom Blu-ray Search")
        print("6. Verify Local Flask App Status")
        print("0. Exit")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1': debug_imdb_watchlist()
        elif choice == '2': debug_search("The Housemaid", 2025)
        elif choice == '3': debug_search("Nuremberg", 2025)
        elif choice == '4': debug_search("The Last Viking", 2025)
        elif choice == '5':
            t = input("Title: ")
            y = input("Year (optional): ")
            y = int(y) if y.strip() else None
            debug_search(t, y)
        elif choice == '6': verify_flask_app()
        elif choice == '0': break
        else: print("Invalid choice.")

if __name__ == "__main__":
    main()