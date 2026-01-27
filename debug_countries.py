import requests
from bs4 import BeautifulSoup

def debug_countries():
    print("--- Debugging Advanced Search Countries ---")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    session.cookies.set('listlayout_7', 'simple', domain='.blu-ray.com')
    session.get("https://www.blu-ray.com/")
    
    # Try adding country=all
    search_url = "https://www.blu-ray.com/movies/search.php"
    params = {
        'keyword': "The Housemaid",
        'yearfrom': '2025',
        'yearto': '2025',
        'submit': 'Search',
        'action': 'search',
        'country': 'all' # Guessing
    }
    
    r = session.get(search_url, params=params)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('tr')
    
    found_germany = False
    for tr in rows:
        text = tr.get_text()
        if "Housemaid" in text:
            if "Leonine" in text or "Germany" in text: # Leonine is German distrib
                print(f"Found German Result: {text[:100]}...")
                found_germany = True
    
    if not found_germany:
        print("Did not find German results with country=all.")

if __name__ == "__main__":
    debug_countries()
