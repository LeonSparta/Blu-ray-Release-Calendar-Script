import sys
import os
import caldav
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import SettingsManager, Config

def debug_sync_event():
    print("--- Debugging Event Sync ---")
    settings = SettingsManager.load_settings()
    username = settings.get('ICLOUD_USERNAME')
    password = settings.get('ICLOUD_PASSWORD')
    url = Config().ICLOUD_URL
    calendar_name = Config().CALENDAR_NAME
    
    if not (username and password):
        print("Error: Missing credentials.")
        return

    try:
        client = caldav.DAVClient(url=url, username=username, password=password)
        principal = client.principal()
        
        target_cal = None
        for cal in principal.calendars():
            if cal.name == calendar_name:
                target_cal = cal
                break
        
        if not target_cal:
            print(f"Calendar '{calendar_name}' not found.")
            return

        print(f"Using calendar: {target_cal}")
        print(f"URL: {target_cal.url}")
        
        print("Attempting to save test event...")
        try:
            target_cal.save_event(
                dtstart=date(2026, 1, 1),
                summary="Test Event from Debug Script",
                description="This is a test."
            )
            print("SUCCESS: Event saved.")
        except Exception as e:
            print(f"FAILED to save event: {e}")

    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    debug_sync_event()
