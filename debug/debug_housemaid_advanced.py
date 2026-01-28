import requests
from bs4 import BeautifulSoup
import re

def debug_housemaid_advanced():
    print("--- Debugging Housemaid Advanced Search ---")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    session.cookies.set('listlayout_7', 'simple', domain='.blu-ray.com')
    # Use global cookie
    session.cookies.set('country', 'all', domain='.blu-ray.com')
    
    session.get("https://www.blu-ray.com/")
    
    search_url = "https://www.blu-ray.com/movies/search.php"
    params = {
        'keyword': "The Housemaid",
        'yearfrom': '2025',
        'yearto': '2025',
        'submit': 'Search',
        'action': 'search'
    }
    
    print(f"URL: {search_url}")
    print(f"Params: {params}")
    
    r = session.get(search_url, params=params)
    print(f"Status: {r.status_code}")
    print(f"Final URL: {r.url}")
    
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('tr')
    print(f"Rows found: {len(rows)}")
    
    for i, tr in enumerate(rows):
        text = tr.get_text(separator='|', strip=True)
        if "Housemaid" in text:
            print(f"[Row {i}] {text[:100]}...")

if __name__ == "__main__":
    debug_housemaid_advanced()
