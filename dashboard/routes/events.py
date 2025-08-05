# dashboard/routes/events.py
"""
Event management API routes.
"""

from flask import Blueprint, jsonify, request, current_app
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
import random

logger = logging.getLogger(__name__)

bp = Blueprint('events', __name__)

@bp.route('/', methods=['GET'])
def get_events():
    """Get recent smoke detection events and system logs."""
    try:
        # Get query parameters
        since = request.args.get('since', 'uptime')
        group_by = request.args.get('group_by', 'none')  # 'none', 'camera', 'type'
        limit = request.args.get('limit', 50, type=int)
        
        # Generate system logs based on 'since' parameter
        logs = []
        
        if since == 'uptime':
            # Last 1 hour of logs
            start_time = datetime.now() - timedelta(hours=1)
        elif since == 'all':
            # All logs (last 24 hours)
            start_time = datetime.now() - timedelta(hours=24)
        else:
            # Default to last hour
            start_time = datetime.now() - timedelta(hours=1)
        
        # Generate sample system logs with more camera-specific entries
        log_entries = [
            # System logs (no camera)
            {'type': 'info', 'message': 'System started successfully', 'camera_id': None},
            {'type': 'info', 'message': 'Frame buffer initialized', 'camera_id': None},
            {'type': 'info', 'message': 'Smoke detection algorithm loaded', 'camera_id': None},
            {'type': 'warning', 'message': 'High CPU usage detected', 'camera_id': None},
            {'type': 'info', 'message': 'Dashboard API responding', 'camera_id': None},
            {'type': 'info', 'message': 'System health check passed', 'camera_id': None},
            
            # Camera 1 logs
            {'type': 'success', 'message': 'Camera 1 connected', 'camera_id': '1'},
            {'type': 'warning', 'message': 'Motion detected on Camera 1', 'camera_id': '1'},
            {'type': 'info', 'message': 'Camera 1 frame processing started', 'camera_id': '1'},
            {'type': 'success', 'message': 'Camera 1 smoke detection active', 'camera_id': '1'},
            {'type': 'warning', 'message': 'Camera 1 high motion activity', 'camera_id': '1'},
            
            # Camera 2 logs
            {'type': 'success', 'message': 'Camera 2 connected', 'camera_id': '2'},
            {'type': 'warning', 'message': 'Network latency detected on Camera 2', 'camera_id': '2'},
            {'type': 'info', 'message': 'Camera 2 frame processing started', 'camera_id': '2'},
            {'type': 'error', 'message': 'Camera 2 connection timeout', 'camera_id': '2'},
            {'type': 'success', 'message': 'Camera 2 reconnected', 'camera_id': '2'},
            
            # Camera 3 logs
            {'type': 'success', 'message': 'Camera 3 connected', 'camera_id': '3'},
            {'type': 'info', 'message': 'Camera 3 frame processing started', 'camera_id': '3'},
            {'type': 'warning', 'message': 'Camera 3 low light conditions', 'camera_id': '3'},
            {'type': 'success', 'message': 'Camera 3 smoke detection active', 'camera_id': '3'},
            
            # Camera 4 logs
            {'type': 'success', 'message': 'Camera 4 connected', 'camera_id': '4'},
            {'type': 'info', 'message': 'Camera 4 frame processing started', 'camera_id': '4'},
            {'type': 'warning', 'message': 'Camera 4 high noise detected', 'camera_id': '4'},
            {'type': 'success', 'message': 'Camera 4 smoke detection active', 'camera_id': '4'},
        ]
        
        # Generate timestamps for logs
        for i, log in enumerate(log_entries):
            # Distribute logs over the time period
            time_offset = (len(log_entries) - i - 1) * (datetime.now() - start_time).total_seconds() / len(log_entries)
            log_time = datetime.now() - timedelta(seconds=time_offset)
            
            logs.append({
                'timestamp': log_time.isoformat(),
                'type': log['type'],
                'message': log['message'],
                'camera_id': log['camera_id']
            })
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Group logs if requested
        if group_by == 'camera':
            grouped_logs = {}
            for log in logs[:limit]:
                camera_id = log['camera_id'] or 'System'
                if camera_id not in grouped_logs:
                    grouped_logs[camera_id] = []
                grouped_logs[camera_id].append(log)
            
            return jsonify({
                'grouped': True,
                'group_by': 'camera',
                'groups': grouped_logs
            })
        elif group_by == 'type':
            grouped_logs = {}
            for log in logs[:limit]:
                log_type = log['type']
                if log_type not in grouped_logs:
                    grouped_logs[log_type] = []
                grouped_logs[log_type].append(log)
            
            return jsonify({
                'grouped': True,
                'group_by': 'type',
                'groups': grouped_logs
            })
        else:
            # Return flat list
            return jsonify(logs[:limit])
        
    except Exception as e:
        logger.exception(f"[Events] Error getting events: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<event_id>', methods=['GET'])
def get_event(event_id: str):
    """Get specific event details."""
    try:
        # Placeholder event details
        event = {
            'id': event_id,
            'camera_id': 'camera_1',
            'camera_name': 'Camera 1',
            'timestamp': datetime.now().isoformat(),
            'event_type': 'smoke_detection',
            'confidence': 0.95,
            'severity': 'high',
            'status': 'confirmed',
            'metadata': {
                'detection_algorithm': 'wasserstein_distance',
                'processing_time': 1.2,
                'frame_count': 11,
                'motion_score': 0.85,
                'patch_validation': True
            },
            'files': {
                'snapshot': f'events/snapshot_camera_1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
                'video': f'events/smoke_event_camera_1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4',
                'data': f'events/smoke_event_camera_1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.npy'
            }
        }
        
        return jsonify(event)
        
    except Exception as e:
        logger.exception(f"[Events] Error getting event {event_id}: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<event_id>/files', methods=['GET'])
def get_event_files(event_id: str):
    """Get files associated with an event."""
    try:
        # Placeholder file information
        files = {
            'snapshot': {
                'path': f'events/snapshot_camera_1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg',
                'size': '2.5 MB',
                'type': 'image/jpeg',
                'available': True
            },
            'video': {
                'path': f'events/smoke_event_camera_1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4',
                'size': '15.2 MB',
                'type': 'video/mp4',
                'duration': '3.7 seconds',
                'available': True
            },
            'data': {
                'path': f'events/smoke_event_camera_1_{datetime.now().strftime("%Y%m%d_%H%M%S")}.npy',
                'size': '8.1 MB',
                'type': 'application/octet-stream',
                'shape': '(11, 504, 896)',
                'available': True
            }
        }
        
        return jsonify(files)
        
    except Exception as e:
        logger.exception(f"[Events] Error getting event files {event_id}: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/statistics', methods=['GET'])
def get_event_statistics():
    """Get event statistics."""
    try:
        # Get query parameters
        days = request.args.get('days', 30, type=int)
        
        # Placeholder statistics
        stats = {
            'total_events': random.randint(50, 200),
            'confirmed_detections': random.randint(30, 150),
            'false_positives': random.randint(5, 25),
            'pending_review': random.randint(0, 10),
            'detection_rate': random.uniform(0.5, 2.0),  # per day
            'accuracy_rate': random.uniform(85, 98),  # percentage
            'average_confidence': random.uniform(0.8, 0.95),
            'most_active_camera': f'Camera {random.randint(1, 4)}',
            'peak_hours': [random.randint(0, 23) for _ in range(3)],
            'period': f'Last {days} days',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.exception(f"[Events] Error getting event statistics: {e}")
        return jsonify({'error': str(e)}), 500 