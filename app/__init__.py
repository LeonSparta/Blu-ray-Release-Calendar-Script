from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import Config, SettingsManager
import logging

scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app import routes
    app.register_blueprint(routes.bp)

    # Scheduler configuration
    if app.config.get('SCHEDULER_API_ENABLED'):
        from app.tasks import update_calendar
        
        settings = SettingsManager.load_settings()
        time_str = settings.get('REFRESH_TIME', '08:00')
        try:
            h, m = map(int, time_str.split(':'))
        except:
            h, m = 8, 0
            
        if not scheduler.get_jobs():
             scheduler.add_job(func=update_calendar, trigger="cron", hour=h, minute=m, id="daily_scan")
        
        # Check if already running (reloader)
        if not scheduler.running:
            scheduler.start()

    return app