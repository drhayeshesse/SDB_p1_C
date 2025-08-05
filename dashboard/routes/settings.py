# dashboard/routes/settings.py
"""
Settings management API routes.
"""

from flask import Blueprint, jsonify, request, current_app
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

bp = Blueprint('settings', __name__)

@bp.route('/', methods=['GET'])
def get_settings():
    """Get current system settings."""
    try:
        settings = current_app.config['SETTINGS']
        
        # Convert settings to dictionary, excluding sensitive information
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
            },
            'notification': {
                'provider': settings.notification.provider,
                'configured': bool(settings.notification.token and settings.notification.user_key)
            }
        }
        
        return jsonify(settings_dict)
        
    except Exception as e:
        logger.exception(f"[Settings] Error getting settings: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/detection', methods=['PUT'])
def update_detection_settings():
    """Update detection settings."""
    try:
        settings = current_app.config['SETTINGS']
        data = request.get_json()
        
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
        
        logger.info(f"[Settings] Updated detection settings: {data}")
        return jsonify({'message': 'Detection settings updated successfully'})
        
    except Exception as e:
        logger.exception(f"[Settings] Error updating detection settings: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/processing', methods=['PUT'])
def update_processing_settings():
    """Update processing settings."""
    try:
        settings = current_app.config['SETTINGS']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update processing settings
        if 'sleep_time' in data:
            settings.sleep_time = float(data['sleep_time'])
        if 'frame_width' in data:
            settings.frame_width = int(data['frame_width'])
        if 'frame_height' in data:
            settings.frame_height = int(data['frame_height'])
        if 'surveillance_counter_threshold' in data:
            settings.surveillance_counter_threshold = int(data['surveillance_counter_threshold'])
        if 'email_counter_threshold' in data:
            settings.email_counter_threshold = int(data['email_counter_threshold'])
        
        logger.info(f"[Settings] Updated processing settings: {data}")
        return jsonify({'message': 'Processing settings updated successfully'})
        
    except Exception as e:
        logger.exception(f"[Settings] Error updating processing settings: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/system', methods=['PUT'])
def update_system_settings():
    """Update system settings."""
    try:
        settings = current_app.config['SETTINGS']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update system settings
        if 'log_level' in data:
            settings.log_level = str(data['log_level'])
        if 'log_to_file' in data:
            settings.log_to_file = bool(data['log_to_file'])
        if 'verbose' in data:
            settings.verbose = int(data['verbose'])
        if 'with_sound' in data:
            settings.with_sound = bool(data['with_sound'])
        if 'text_email' in data:
            settings.text_email = bool(data['text_email'])
        if 'notification_retry_limit' in data:
            settings.notification_retry_limit = int(data['notification_retry_limit'])
        if 'metrics_queue_len' in data:
            settings.metrics_queue_len = int(data['metrics_queue_len'])
        if 'reconnect_delay_sec' in data:
            settings.reconnect_delay_sec = int(data['reconnect_delay_sec'])
        if 'watchdog_check_interval_sec' in data:
            settings.watchdog_check_interval_sec = int(data['watchdog_check_interval_sec'])
        
        logger.info(f"[Settings] Updated system settings: {data}")
        return jsonify({'message': 'System settings updated successfully'})
        
    except Exception as e:
        logger.exception(f"[Settings] Error updating system settings: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/notification', methods=['PUT'])
def update_notification_settings():
    """Update notification settings."""
    try:
        settings = current_app.config['SETTINGS']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update notification settings
        if 'provider' in data:
            settings.notification.provider = str(data['provider'])
        if 'token' in data:
            settings.notification.token = str(data['token'])
        if 'user_key' in data:
            settings.notification.user_key = str(data['user_key'])
        
        logger.info(f"[Settings] Updated notification settings")
        return jsonify({'message': 'Notification settings updated successfully'})
        
    except Exception as e:
        logger.exception(f"[Settings] Error updating notification settings: {e}")
        return jsonify({'error': str(e)}), 500 