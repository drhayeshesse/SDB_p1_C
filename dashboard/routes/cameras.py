# dashboard/routes/cameras.py
"""
Camera management API routes.
"""

from flask import Blueprint, jsonify, request, current_app
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('cameras', __name__)

@bp.route('/', methods=['GET'])
def get_cameras():
    """Get all cameras."""
    try:
        settings = current_app.config['SETTINGS']
        
        cameras = []
        for camera in settings.cameras:
            cameras.append({
                'id': camera.id,
                'name': camera.name,
                'ip': camera.ip,
                'port': camera.port,
                'enabled': camera.enabled,
                'stream_path': camera.stream_path,
                'frame_width': camera.frame_width,
                'frame_height': camera.frame_height,
                'target_fps': camera.target_fps
            })
        
        return jsonify({'cameras': cameras})
        
    except Exception as e:
        logger.exception(f"[Cameras] Error getting cameras: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<camera_id>', methods=['GET'])
def get_camera(camera_id: str):
    """Get specific camera details."""
    try:
        settings = current_app.config['SETTINGS']
        
        for camera in settings.cameras:
            if camera.id == camera_id:
                return jsonify({
                    'id': camera.id,
                    'name': camera.name,
                    'ip': camera.ip,
                    'port': camera.port,
                    'enabled': camera.enabled,
                    'stream_path': camera.stream_path,
                    'frame_width': camera.frame_width,
                    'frame_height': camera.frame_height,
                    'target_fps': camera.target_fps
                })
        
        return jsonify({'error': 'Camera not found'}), 404
        
    except Exception as e:
        logger.exception(f"[Cameras] Error getting camera {camera_id}: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<camera_id>/status', methods=['GET'])
def get_camera_status(camera_id: str):
    """Get camera connection status."""
    try:
        # This would typically check with the stream manager
        # For now, return a placeholder status
        return jsonify({
            'camera_id': camera_id,
            'status': 'connected',  # Placeholder
            'last_frame_time': None,  # Placeholder
            'fps': 0.0  # Placeholder
        })
        
    except Exception as e:
        logger.exception(f"[Cameras] Error getting camera status {camera_id}: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<camera_id>/enable', methods=['POST'])
def enable_camera(camera_id: str):
    """Enable a camera."""
    try:
        settings = current_app.config['SETTINGS']
        
        for camera in settings.cameras:
            if camera.id == camera_id:
                camera.enabled = True
                logger.info(f"[Cameras] Enabled camera {camera_id}")
                return jsonify({'message': f'Camera {camera_id} enabled'})
        
        return jsonify({'error': 'Camera not found'}), 404
        
    except Exception as e:
        logger.exception(f"[Cameras] Error enabling camera {camera_id}: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<camera_id>/disable', methods=['POST'])
def disable_camera(camera_id: str):
    """Disable a camera."""
    try:
        settings = current_app.config['SETTINGS']
        
        for camera in settings.cameras:
            if camera.id == camera_id:
                camera.enabled = False
                logger.info(f"[Cameras] Disabled camera {camera_id}")
                return jsonify({'message': f'Camera {camera_id} disabled'})
        
        return jsonify({'error': 'Camera not found'}), 404
        
    except Exception as e:
        logger.exception(f"[Cameras] Error disabling camera {camera_id}: {e}")
        return jsonify({'error': str(e)}), 500 