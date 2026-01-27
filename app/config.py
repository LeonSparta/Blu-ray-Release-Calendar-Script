import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    IMDB_WATCHLIST_URL = os.environ.get('IMDB_WATCHLIST_URL') or "https://www.imdb.com/user/ur110300787/watchlist/?ref_=hm_nv_urwls_all&sort=release_date%2Cdesc"
    ICLOUD_URL = os.environ.get('ICLOUD_URL') or "https://caldav.icloud.com/"
    ICLOUD_USERNAME = os.environ.get('ICLOUD_USERNAME')
    ICLOUD_PASSWORD = os.environ.get('ICLOUD_PASSWORD') # App-specific password
    CALENDAR_NAME = os.environ.get('CALENDAR_NAME') or "Blu-ray Releases"
    SCHEDULER_API_ENABLED = True
