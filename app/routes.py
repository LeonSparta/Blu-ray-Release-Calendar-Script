from flask import Blueprint, render_template, jsonify, request
from app.tasks import process_watchlist_realtime
from app.config import SettingsManager
import threading

bp = Blueprint('main', __name__)

# Store global state
app_state = {
    'movies': [],
    'icloud_status': 'Unknown',
    'timestamp': None,
    'is_running': False,
    'stop_requested': False
}

@bp.route('/')
def index():
    return render_template('index.html', state=app_state, settings=SettingsManager.load_settings())

@bp.route('/status')
def get_status():
    return jsonify(app_state)

@bp.route('/run', methods=['POST'])
def run_now():
    if app_state['is_running']:
        return jsonify({'status': 'Already running'}), 400
    
    app_state['stop_requested'] = False # Reset stop flag
    
    def task_wrapper():
        app_state['is_running'] = True
        try:
            # Pass the state by reference
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
    return jsonify({'status': 'Settings saved'})
