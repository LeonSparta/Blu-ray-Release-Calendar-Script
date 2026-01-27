from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import Config
import logging

scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app import routes
    app.register_blueprint(routes.bp)

    # Scheduler configuration
    if app.config['SCHEDULER_API_ENABLED']:
        from app.tasks import update_calendar
        # Run every day at 8 AM
        if not scheduler.get_jobs():
             scheduler.add_job(func=update_calendar, trigger="cron", hour=8, id="daily_scan")
        scheduler.start()

    return app
