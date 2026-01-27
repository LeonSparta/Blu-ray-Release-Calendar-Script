import requests
from bs4 import BeautifulSoup
import re

def test_scrape():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.blu-ray.com/',
        'Connection': 'keep-alive'
    }

    # 2. Test Blu-ray.com
    print("Testing Blu-ray.com with Session...")
    session = requests.Session()
    session.headers.update(headers)

    try:
        # Visit homepage first
        print("Visiting homepage...")
        session.get("https://www.blu-ray.com/")
        
        # 3. Test Specific Movie Page
        print("\nTesting Specific Movie Page...")
        movie_url = "https://www.blu-ray.com/movies/Sentimental-Value-4K-Blu-ray/404996/"
        
        r = session.get(movie_url)
        print(f"Movie Page Status: {r.status_code}")
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Debug: Find "Release date"
        print(f"Page Title: {soup.title.text.strip() if soup.title else 'No Title'}")
        
        labels = soup.find_all(string=re.compile("Release date", re.IGNORECASE))
        if labels:
            print(f"Found {len(labels)} 'Release date' labels.")
            for label in labels:
                parent = label.parent
                # traverse up a bit to get the row
                row = parent.parent
                print(f"--- Label Context ---\n{row.prettify()[:500]}")
        else:
            print("'Release date' label NOT FOUND.")
            
        # Search for any 2026
        years = soup.find_all(string=re.compile("2026"))
        print(f"Found {len(years)} matches for '2026'.")
        for y in years:
             print(f"Year match: {y.strip()}")


    except Exception as e:
        print(f"Blu-ray Error: {e}")

if __name__ == "__main__":
    test_scrape()