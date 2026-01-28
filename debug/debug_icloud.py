import sys
import os
import caldav

# Add parent directory to path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import SettingsManager, Config

def debug_icloud():
    print("--- Debugging iCloud Connection ---")
    
    settings = SettingsManager.load_settings()
    username = settings.get('ICLOUD_USERNAME')
    password = settings.get('ICLOUD_PASSWORD')
    url = Config().ICLOUD_URL
    
    print(f"URL: {url}")
    print(f"Username: {username}")
    
    if not (username and password):
        print("Error: Missing credentials in config.json")
        return

    try:
        print("\nAttempting connection...")
        client = caldav.DAVClient(
            url=url,
            username=username,
            password=password
        )
        
        print("Fetching principal...")
        principal = client.principal()
        print(f"Principal found: {principal}")
        
        print("Fetching calendars...")
        calendars = principal.calendars()
        
        if calendars:
            print(f"Success! Found {len(calendars)} calendars:")
            for cal in calendars:
                print(f" - {cal.name}")
        else:
            print("Success! Connected but no calendars found.")
            
    except Exception as e:
        print(f"\nCONNECTION FAILED: {e}")

if __name__ == "__main__":
    debug_icloud()
