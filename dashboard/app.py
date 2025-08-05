import os
import logging
from datetime import datetime
from flask import Flask, jsonify, send_from_directory

from data_models.models import ProgramSettings
from frame_buffer.frame_buffer import FrameBuffer
from .routes import api, metrics, events, settings as settings_routes, stream

logger = logging.getLogger(__name__)

def create_app(settings: ProgramSettings, frame_buffer: FrameBuffer) -> Flask:
    # Change this if using React build: e.g. os.path.join(os.path.dirname(__file__), "react-app", "dist")
    static_dir = os.path.join(os.path.dirname(__file__), "static")

    app = Flask(__name__, static_folder=static_dir, static_url_path="")

    app.config['SETTINGS'] = settings
    app.config['FRAME_BUFFER'] = frame_buffer

    logger.info("[Dashboard] Frame buffer injected into Flask app")

    # Register API blueprints
    app.register_blueprint(api.bp, url_prefix='/api')
    app.register_blueprint(metrics.bp, url_prefix='/api/metrics')
    app.register_blueprint(events.bp, url_prefix='/api/events')
    app.register_blueprint(settings_routes.bp, url_prefix='/api/settings')
    app.register_blueprint(stream.bp, url_prefix='/stream')

    # Serve dashboard page and SPA fallback
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_dashboard(path):
        full_path = os.path.join(static_dir, path)
        if path != "" and os.path.exists(full_path):
            return send_from_directory(static_dir, path)
        return send_from_directory(static_dir, 'dashboard.html')

    # Health check
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'version': 'SDB_p1',
            'timestamp': datetime.now().isoformat()
        })

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Internal server error")
        return jsonify({'error': 'Internal server error'}), 500

    logger.info("[Dashboard] Flask app created successfully")
    return app


def run_dashboard(settings: ProgramSettings, frame_buffer: FrameBuffer,
                  host: str = '0.0.0.0', port: int = 5050, debug: bool = False):
    app = create_app(settings, frame_buffer)
    logger.info(f"[Dashboard] Starting dashboard on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    from utils.settings import get_settings

    settings = get_settings()
    frame_buffer = FrameBuffer()
    run_dashboard(settings, frame_buffer)