from debug_toolkit import get_session
from bs4 import BeautifulSoup
import re

def deep_debug(title, year):
    print(f"\n--- Deep Debug: {title} ({year}) ---")
    session = get_session()
    search_url = "https://www.blu-ray.com/search/"
    params = {
        'quicksearch': '1',
        'quicksearch_country': 'all',
        'quicksearch_keyword': title,
        'section': 'bluraymovies'
    }
    
    r = session.get(search_url, params=params)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('tr')
    
    print(f"Scanning {len(rows)} rows...")
    
    for i, tr in enumerate(rows):
        cells = tr.find_all('td')
        if not cells: continue
        
        row_text = tr.get_text()
        # Loose check to see if we are even looking at the right area
        # We assume the title might be part of the row
        
        # Check Link
        link = tr.find('a', href=True)
        if not link or '/movies/' not in link['href']:
            continue
            
        link_text = link.get_text(" ", strip=True)
        
        # Check similarity
        print(f"\n[Row {i}] Link: '{link_text}'")
        print(f"  > Raw Row: {row_text[:100]}...")
        
        # Year Check Debug
        if year:
            has_year = f"({year})" in row_text
            print(f"  > Year '{year}' found: {has_year}")
        
        # Title Check Debug
        norm_link = re.sub(r'\s+4K$', '', link_text, flags=re.IGNORECASE)
        print(f"  > Norm Link: '{norm_link}'")
        
        is_exact = norm_link.lower() == title.lower()
        is_partial = title.lower() in norm_link.lower()
        print(f"  > Exact: {is_exact} | Partial: {is_partial}")

        # Normalize special chars test
        if "Tár" in title:
            print(f"  > Hex Link: {[hex(ord(c)) for c in norm_link]}")
            print(f"  > Hex Title: {[hex(ord(c)) for c in title]}")

def run():
    deep_debug("No Other Choice", 2025)
    deep_debug("Tár", 2022)

if __name__ == "__main__":
    run()