import sys
import os
import caldav
from datetime import date, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import SettingsManager, Config

def debug_event_structure():
    print("--- Debugging Event Structure ---")
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
        print(f"Calendar {calendar_name} not found.")
        return

    print(f"Using calendar: {calendar.name}")
    
    # search for any event in next 365 days
    start = date.today()
    end = start + timedelta(days=365)
    
    print(f"Searching events from {start} to {end}...")
    events = calendar.date_search(start=start, end=end)
    
    if not events:
        print("No events found. Creating a dummy event...")
        try:
            calendar.save_event(
                dtstart=start,
                dtend=start + timedelta(days=1),
                summary="Debug Structure Event"
            )
            events = calendar.date_search(start=start, end=end)
        except Exception as e:
            print(f"Failed to create dummy event: {e}")
            return

    if events:
        event = events[0]
        print("\n--- Event Object Inspection ---")
        print(f"Type: {type(event)}")
        print(f"Dir: {dir(event)}")
        
        try:
            print(f"\nAttempting .vobject: {event.vobject}")
        except AttributeError:
            print("\n.vobject attribute MISSING")
            
        try:
            print(f"\nAttempting .icalendar_component: {event.icalendar_component}")
        except AttributeError:
            print("\n.icalendar_component attribute MISSING")
            
        try:
            print(f"\nAttempting .instance: {event.instance}")
        except AttributeError:
            print("\n.instance attribute MISSING")
            
        # Check how to get summary
        # If using caldav > 1.0, it might use icalendar library objects directly
        # event.icalendar_component is usually the VEVENT
        
if __name__ == "__main__":
    debug_event_structure()
