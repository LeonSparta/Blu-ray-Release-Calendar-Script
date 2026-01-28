import sys
import os
import caldav
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import SettingsManager, Config

def debug_reference_logic():
    print("--- Debugging Reference Logic (Exact) ---")
    settings = SettingsManager.load_settings()
    username = settings.get('ICLOUD_USERNAME')
    password = settings.get('ICLOUD_PASSWORD')
    url = 'https://caldav.icloud.com' # Exactly as reference
    calendar_name = Config().CALENDAR_NAME
    
    if not (username and password):
        print("Credentials missing.")
        return

    try:
        client = caldav.DAVClient(url=url, username=username, password=password)
        principal = client.principal()
        calendars = principal.calendars()
        
        calendar = next((cal for cal in calendars if cal.name == calendar_name), None)
        if not calendar:
            print(f"Calendar '{calendar_name}' not found.")
            return

        print(f"Targeting: {calendar.name}")
        
        # Test All-Day Event
        from datetime import date
        start_date = date(2026, 5, 1)
        end_date = start_date + timedelta(days=1)
        summary = "Test All Day Event"
        
        print(f"Saving ALL-DAY event {start_date} to {end_date}...")
        try:
            calendar.save_event(
                dtstart=start_date,
                dtend=end_date,
                summary=summary
            )
            print("SUCCESS: All-Day Event saved.")
        except Exception as e:
            print(f"FAILED All-Day: {e}")

    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    debug_reference_logic()
