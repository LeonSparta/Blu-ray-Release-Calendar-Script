import sys
import os
import caldav
from datetime import date, timedelta, datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import SettingsManager, Config

def debug_find_event():
    print("--- Debugging Event Search ---")
    settings = SettingsManager.load_settings()
    username = settings.get('ICLOUD_USERNAME')
    password = settings.get('ICLOUD_PASSWORD')
    url = Config().ICLOUD_URL
    calendar_name = Config().CALENDAR_NAME
    
    if not (username and password):
        print("Credentials missing.")
        return

    client = caldav.DAVClient(url=url, username=username, password=password)
    principal = client.principal()
    calendar = next((cal for cal in principal.calendars() if cal.name == calendar_name), None)
    
    if not calendar:
        print("Calendar not found.")
        return

    target_title = "The Last Viking"
    print(f"Searching for: '{target_title}'")

    # 1. Standard Search
    print("\n[Method 1] calendar.search(summary=...)")
    try:
        events = calendar.search(summary=target_title, event=True, expand=False)
        print(f"Found {len(events)} events.")
        for e in events:
            comp = e.icalendar_component
            print(f" - {comp.get('SUMMARY')} @ {comp.get('DTSTART').dt}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Wide Range Date Search (e.g. Jan 1 2026 to Dec 31 2026)
    print("\n[Method 2] calendar.date_search(2026-01-01 to 2026-12-31)")
    start = date(2026, 1, 1)
    end = date(2026, 12, 31)
    try:
        events = calendar.date_search(start=start, end=end)
        matches = []
        for e in events:
            comp = e.icalendar_component
            summary = str(comp.get('SUMMARY'))
            if target_title.lower() in summary.lower():
                matches.append(e)
                print(f" - {summary} @ {comp.get('DTSTART').dt}")
        
        print(f"Found {len(matches)} matches via date scan.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_find_event()
