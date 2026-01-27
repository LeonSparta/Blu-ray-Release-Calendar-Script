from flask import Blueprint, render_template, jsonify
from app.tasks import update_calendar
import threading

bp = Blueprint('main', __name__)

last_results = []
is_running = False

@bp.route('/')
def index():
    return render_template('index.html', results=last_results, is_running=is_running)

@bp.route('/run', methods=['POST'])
def run_now():
    global is_running, last_results
    if is_running:
        return jsonify({'status': 'Already running'}), 400
    
    def task_wrapper():
        global is_running, last_results
        is_running = True
        try:
            last_results = update_calendar()
        except Exception as e:
            last_results = [{'title': 'Error', 'status': str(e)}]
        finally:
            is_running = False

    thread = threading.Thread(target=task_wrapper)
    thread.start()
    
    return jsonify({'status': 'Started'})
