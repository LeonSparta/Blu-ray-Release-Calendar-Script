from flask import Blueprint, render_template, jsonify, request
from app.tasks import process_watchlist_realtime, update_calendar
from app.config import SettingsManager, Config
from app import scheduler
import threading
import caldav

bp = Blueprint('main', __name__)

# Store global state
app_state = {
    'movies': [],
    'icloud_status': 'Unknown',
    'timestamp': None,
    'is_running': False,
    'stop_requested': False
}

def check_icloud_connection():
    settings = SettingsManager.load_settings()
    username = settings.get('ICLOUD_USERNAME')
    password = settings.get('ICLOUD_PASSWORD')
    if username and password:
        try:
            client = caldav.DAVClient(
                url=Config().ICLOUD_URL, 
                username=username, 
                password=password
            )
            client.principal().calendars()
            return "Connected"
        except Exception as e:
            return f"Error: {str(e)}"
    return "Not Configured"

@bp.route('/')
def index():
    # Update status on load if unknown
    if app_state['icloud_status'] == 'Unknown':
        app_state['icloud_status'] = check_icloud_connection()
    return render_template('index.html', state=app_state, settings=SettingsManager.load_settings())

@bp.route('/status')
def get_status():
    return jsonify(app_state)

@bp.route('/run', methods=['POST'])
def run_now():
    if app_state['is_running']:
        return jsonify({'status': 'Already running'}), 400
    
    app_state['stop_requested'] = False
    
    def task_wrapper():
        app_state['is_running'] = True
        try:
            process_watchlist_realtime(app_state)
        except Exception as e:
            app_state['icloud_status'] = f"Error: {str(e)}"
        finally:
            app_state['is_running'] = False
            app_state['stop_requested'] = False

    thread = threading.Thread(target=task_wrapper)
    thread.start()
    
    return jsonify({'status': 'Started'})

@bp.route('/stop', methods=['POST'])
def stop_scan():
    if app_state['is_running']:
        app_state['stop_requested'] = True
        return jsonify({'status': 'Stopping...'})
    return jsonify({'status': 'Not running'}), 400

@bp.route('/settings', methods=['POST'])
def save_settings():
    data = request.json
    SettingsManager.save_settings(data)
    
    # Update iCloud Status immediately
    app_state['icloud_status'] = check_icloud_connection()
    
    # Reschedule if time changed
    new_time = data.get('REFRESH_TIME', '08:00')
    try:
        h, m = map(int, new_time.split(':'))
        if scheduler.get_job('daily_scan'):
            scheduler.reschedule_job('daily_scan', trigger='cron', hour=h, minute=m)
        else:
            scheduler.add_job(func=update_calendar, trigger="cron", hour=h, minute=m, id="daily_scan")
    except Exception as e:
        print(f"Failed to reschedule: {e}")
        
    return jsonify({'status': 'Settings saved'})
