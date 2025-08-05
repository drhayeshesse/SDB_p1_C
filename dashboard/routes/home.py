# dashboard/routes/home.py
"""
Home route for the dashboard.
"""

from flask import Blueprint, render_template, current_app, send_from_directory
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    """Main dashboard page - serves Apple-style React app."""
    try:
        return send_from_directory('react-app', 'apple-style-dashboard.html')
    except Exception as e:
        logger.exception(f"[Home] Error serving React app: {e}")
        return render_template('error.html', error=str(e))

@bp.route('/react-app/<path:filename>')
def serve_react_app(filename):
    """Serve React app static files."""
    try:
        return send_from_directory('react-app', filename)
    except Exception as e:
        logger.exception(f"[Home] Error serving React file {filename}: {e}")
        return '', 404

@bp.route('/status')
def status():
    """System status endpoint."""
    try:
        settings = current_app.config['SETTINGS']
        frame_buffer = current_app.config['FRAME_BUFFER']
        
        # Get system status
        status_data = {
            'detection_enabled': settings.detection_enabled,
            'detection_schedule_enabled': settings.detection_schedule_enabled,
            'active_cameras': len([c for c in settings.cameras if c.enabled]),
            'total_cameras': len(settings.cameras),
            'frame_buffer_status': 'active' if frame_buffer else 'inactive'
        }
        
        return status_data
        
    except Exception as e:
        logger.exception(f"[Home] Error getting status: {e}")
        return {'error': str(e)}, 500 