import os
import json

class SettingsManager:
    FILE_PATH = 'config.json'
    
    @staticmethod
    def load_settings():
        # defaults from environment or hardcoded fallback
        defaults = {
            'ICLOUD_USERNAME': os.environ.get('ICLOUD_USERNAME', ''),
            'ICLOUD_PASSWORD': os.environ.get('ICLOUD_PASSWORD', ''),
            'IMDB_WATCHLIST_URL': os.environ.get('IMDB_WATCHLIST_URL', '') or "https://www.imdb.com/user/ur110300787/watchlist/?ref_=hm_nv_urwls_all&sort=release_date%2Cdesc",
            'THEME': 'system'
        }
        
        if os.path.exists(SettingsManager.FILE_PATH):
            try:
                with open(SettingsManager.FILE_PATH, 'r') as f:
                    data = json.load(f)
                    # Update only if key exists in json to allow partial overrides
                    # actually we want json to win, but defaults to fill gaps
                    for k, v in data.items():
                        if v: # Only override if not empty? User might want to clear it. 
                            # Let's say JSON wins.
                            defaults[k] = v
            except Exception:
                pass
        return defaults

    @staticmethod
    def save_settings(data):
        current = SettingsManager.load_settings()
        current.update(data)
        with open(SettingsManager.FILE_PATH, 'w') as f:
            json.dump(current, f, indent=4)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    @property
    def ICLOUD_USERNAME(self):
        return SettingsManager.load_settings().get('ICLOUD_USERNAME')
        
    @property
    def ICLOUD_PASSWORD(self):
        return SettingsManager.load_settings().get('ICLOUD_PASSWORD')

    @property
    def IMDB_WATCHLIST_URL(self):
        return SettingsManager.load_settings().get('IMDB_WATCHLIST_URL')
    
    @property
    def CALENDAR_NAME(self):
        return os.environ.get('CALENDAR_NAME') or "Blu-ray Releases"
    
    @property
    def ICLOUD_URL(self):
        return os.environ.get('ICLOUD_URL') or "https://caldav.icloud.com/"

    SCHEDULER_API_ENABLED = True
