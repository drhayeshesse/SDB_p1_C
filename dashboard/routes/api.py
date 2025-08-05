# dashboard/routes/api.py
"""
API routes for the dashboard.
"""

from flask import Blueprint, jsonify, request, current_app, send_file
import logging
import os
from datetime import datetime
import cv2
import io
from PIL import Image  # type: ignore

logger = logging.getLogger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/status', methods=['GET'])
def get_status():
    """Get system status."""
    try:
        import json
        import os
        import time
        

        
        # Read camera configuration to get real camera count
        camera_config_path = os.path.join(os.getcwd(), 'config', 'cameras.json')
        logger.info(f"[API] Status: Looking for camera config at: {camera_config_path}")
        logger.info(f"[API] Status: Current working directory: {os.getcwd()}")
        logger.info(f"[API] Status: File exists: {os.path.exists(camera_config_path)}")
        active_cameras = 0
        total_cameras = 0
        camera_ids = []

        if os.path.exists(camera_config_path):
            with open(camera_config_path, 'r') as f:
                camera_config = json.load(f)
            
            total_cameras = len(camera_config)
            active_cameras = len([camera for camera in camera_config 
                                if camera.get('enabled', True)])
            camera_ids = [str(camera["id"]) for camera in camera_config]


        # Get stream manager
        stream_manager = current_app.config.get('STREAM_MANAGER')

        # ✅ Check if frame buffer actually has frames (cached check)
        frame_buffer = current_app.config.get('FRAME_BUFFER')
        buffer_ok = False
        if frame_buffer and camera_ids:
            # Only check first camera to reduce CPU load
            buffer_ok = frame_buffer.get_frame(camera_ids[0], "original") is not None

        # Decide status
        frame_buffer_status = "active" if buffer_ok else "inactive"

        # Build status payload
        status_data = {
            'detectionEnabled': True,  # Default to True
            'schedulerEnabled': False,  # Default to False
            'activeCameras': active_cameras,
            'totalCameras': total_cameras,
            'frame_buffer_status': frame_buffer_status,
            'fps': 15,  # From camera config
            'uptime': '00:00:00'  # Will be calculated by frontend
        }
        
        logger.debug(f"[API] Status: {status_data}")
        return jsonify(status_data)
        
    except Exception as e:
        logger.exception(f"[API] Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/toggle-detection', methods=['POST'])
def toggle_detection():
    """Toggle detection on/off."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        settings = current_app.config['SETTINGS']
        settings.detection_enabled = enabled
        
        logger.info(f"[API] Detection toggled to: {enabled}")
        
        return jsonify({
            'success': True,
            'detection_enabled': enabled
        })
        
    except Exception as e:
        logger.exception(f"[API] Error toggling detection: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/update', methods=['POST'])
def update_settings():
    """Update system settings."""
    try:
        data = request.get_json()
        
        settings = current_app.config['SETTINGS']
        
        # Update settings based on data
        if 'sensitivity' in data:
            settings.sensitivity = data['sensitivity']
        if 'motion_threshold' in data:
            settings.motion_threshold = data['motion_threshold']
        
        logger.info(f"[API] Settings updated: {data}")
        
        return jsonify({
            'success': True,
            'settings': {
                'sensitivity': settings.sensitivity,
                'motion_threshold': settings.motion_threshold
            }
        })
        
    except Exception as e:
        logger.exception(f"[API] Error updating settings: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/cameras', methods=['GET'])
def get_cameras():
    """Get camera information from camera configuration."""
    try:
        import json
        import os
        
        # Read camera configuration directly from JSON file
        camera_config_path = os.path.join(os.getcwd(), 'config', 'cameras.json')
        logger.debug(f"[API] Cameras: Looking for camera config at: {camera_config_path}")
        
        if os.path.exists(camera_config_path):
            with open(camera_config_path, 'r') as f:
                camera_config = json.load(f)
            
            cameras = []
            for camera in camera_config:
                cameras.append({
                    'id': int(camera['id']),
                    'name': camera.get('name', f'Camera {camera["id"]}'),
                    'ip': camera.get('ip', 'N/A'),
                    'enabled': camera.get('enabled', True),
                    'status': 'Active' if camera.get('enabled', True) else 'Inactive',
                    'resolution': f"{camera.get('frame_width', 896)}x{camera.get('frame_height', 504)}",
                    'fps': camera.get('target_fps', 3.0)
                })
            
            logger.info(f"[API] Loaded {len(cameras)} cameras from configuration")
            return jsonify(cameras)
        else:
            logger.error(f"[API] Camera configuration file not found: {camera_config_path}")
            return jsonify({'error': 'Camera configuration not found'}), 404
        
    except Exception as e:
        logger.exception(f"[API] Error getting cameras: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/settings', methods=['GET'])
def get_settings():
    """Get system settings."""
    try:
        settings = current_app.config.get('SETTINGS')
        
        if settings:
            settings_dict = {
                'detection': {
                    'enabled': settings.detection_enabled,
                    'schedule_enabled': settings.detection_schedule_enabled,
                    'start_time': settings.detection_start,
                    'end_time': settings.detection_end,
                    'sensitivity': settings.sensitivity,
                    'sensitivity_val': settings.sensitivity_val,
                    'motion_threshold': settings.motion_threshold,
                    'motion_count_threshold': settings.motion_count_threshold,
                    'n_patches_validate': settings.n_patches_validate,
                    'n_frames_validation': settings.n_frames_validation,
                    'sliding_window': settings.sliding_window
                },
                'processing': {
                    'sleep_time': settings.sleep_time,
                    'frame_width': settings.frame_width,
                    'frame_height': settings.frame_height,
                    'surveillance_counter_threshold': settings.surveillance_counter_threshold,
                    'email_counter_threshold': settings.email_counter_threshold
                },
                'system': {
                    'log_level': settings.log_level,
                    'log_to_file': settings.log_to_file,
                    'verbose': settings.verbose,
                    'with_sound': settings.with_sound,
                    'text_email': settings.text_email,
                    'notification_retry_limit': settings.notification_retry_limit,
                    'metrics_queue_len': settings.metrics_queue_len,
                    'reconnect_delay_sec': settings.reconnect_delay_sec,
                    'watchdog_check_interval_sec': settings.watchdog_check_interval_sec
                }
            }
            return jsonify(settings_dict)
        else:
            return jsonify({'error': 'Settings not available'}), 404
            
    except Exception as e:
        logger.exception(f"[API] Error getting settings: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/settings/detection', methods=['PUT'])
def update_detection_settings():
    """Update detection settings."""
    try:
        settings = current_app.config.get('SETTINGS')
        data = request.get_json()
        
        if not settings:
            return jsonify({'error': 'Settings not available'}), 404
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update detection settings
        if 'enabled' in data:
            settings.detection_enabled = bool(data['enabled'])
        if 'schedule_enabled' in data:
            settings.detection_schedule_enabled = bool(data['schedule_enabled'])
        if 'start_time' in data:
            settings.detection_start = str(data['start_time'])
        if 'end_time' in data:
            settings.detection_end = str(data['end_time'])
        if 'sensitivity' in data:
            settings.sensitivity = int(data['sensitivity'])
        if 'sensitivity_val' in data:
            settings.sensitivity_val = int(data['sensitivity_val'])
        if 'motion_threshold' in data:
            settings.motion_threshold = int(data['motion_threshold'])
        if 'motion_count_threshold' in data:
            settings.motion_count_threshold = int(data['motion_count_threshold'])
        if 'n_patches_validate' in data:
            settings.n_patches_validate = int(data['n_patches_validate'])
        if 'n_frames_validation' in data:
            settings.n_frames_validation = int(data['n_frames_validation'])
        if 'sliding_window' in data:
            settings.sliding_window = int(data['sliding_window'])
        
        logger.info(f"[API] Updated detection settings: {data}")
        return jsonify({'message': 'Detection settings updated successfully'})
        
    except Exception as e:
        logger.exception(f"[API] Error updating detection settings: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/events', methods=['GET'])
def get_events():
    """Get recent system events."""
    try:
        # Mock events - in a real system, these would come from a database
        events = [
            {
                'id': 1,
                'timestamp': datetime.now().isoformat(),
                'type': 'info',
                'message': 'System started successfully',
                'camera_id': None
            },
            {
                'id': 2,
                'timestamp': datetime.now().isoformat(),
                'type': 'success',
                'message': 'Camera 1 connected',
                'camera_id': 1
            },
            {
                'id': 3,
                'timestamp': datetime.now().isoformat(),
                'type': 'warning',
                'message': 'Motion detected',
                'camera_id': 1
            }
        ]
        
        return jsonify(events)
        
    except Exception as e:
        logger.exception(f"[API] Error getting events: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/video_feed/<int:camera_id>/<stage>', methods=['GET'])
def get_video_feed(camera_id, stage):
    """Get video feed for a specific camera and stage."""
    try:
        # Get the frame buffer from the app context
        frame_buffer = current_app.config.get('FRAME_BUFFER')
        
        if frame_buffer:
            # Get the frame from the frame buffer for the specified stage
            # For now, use 'original' stage as default, or the requested stage if available
            available_stages = ['original', 'current', 'base', 'heatmap', 'difference', 'mean', 'wasserstein', 'difference_wass']
            
            # Try the requested stage first, then fall back to 'original'
            frame = None
            if stage in available_stages:
                frame = frame_buffer.get_frame(str(camera_id), stage)
            
            # If the requested stage is not available, try 'original'
            if frame is None:
                frame = frame_buffer.get_frame(str(camera_id), 'original')
            
            if frame is not None:
                # Convert frame to image and serve (with reduced quality for performance)
                
                # Handle different frame formats
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    # BGR frame (3 channels) - convert to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                elif len(frame.shape) == 2:
                    # Grayscale frame (1 channel) - convert to RGB
                    pil_image = Image.fromarray(frame).convert('RGB')
                else:
                    # Unknown format - try to convert anyway
                    pil_image = Image.fromarray(frame)
                
                # Save to bytes with lower quality for better performance
                img_io = io.BytesIO()
                pil_image.save(img_io, 'JPEG', quality=70)  # Reduced from 85 to 70
                img_io.seek(0)
                
                logger.debug(f"[API] Serving frame for camera {camera_id}, stage {stage}")
                return send_file(img_io, mimetype='image/jpeg')
            else:
                logger.warning(f"[API] No frame available for camera {camera_id}")
        else:
            logger.warning("[API] Frame buffer not available")
        
        # Return a placeholder image or error
        return jsonify({
            'error': 'No video feed available',
            'camera_id': camera_id,
            'stage': stage
        }), 404
        
    except Exception as e:
        logger.exception(f"[API] Error getting video feed: {e}")
        return jsonify({'error': str(e)}), 500 