# camera_config.py
"""
Simple camera configuration manager for the SDB_p1 system.
"""

import json
from pathlib import Path
from typing import List, Optional
from data_models.models import CameraConfig
import logging

logger = logging.getLogger(__name__)

CAMERA_CONFIG_FILE = Path("config/cameras.json")

DEFAULT_CAMERA_VALUES = {
    "port": 554,
    "username": "admin",
    "password": "",
    "stream_path": "/cam/realmonitor?channel=1&subtype=1",
    "enabled": True,
    "codec": "h264",
    "frame_width": 896,
    "frame_height": 504,
    "latency_ms": 0,
    "target_fps": 3.0
}

def fill_missing_defaults(cam: dict) -> dict:
    """Fill missing camera configuration with default values."""
    for key, default in DEFAULT_CAMERA_VALUES.items():
        cam.setdefault(key, default)
    return cam

def load_cameras() -> List[CameraConfig]:
    """Load camera configurations from JSON file."""
    if not CAMERA_CONFIG_FILE.exists():
        logger.debug(f"No cameras file found at {CAMERA_CONFIG_FILE}")
        return []

    try:
        with CAMERA_CONFIG_FILE.open("r") as f:
            data = json.load(f)

        cameras = [CameraConfig(**fill_missing_defaults(cam)) for cam in data]
        logger.debug(f"Loaded {len(cameras)} cameras from {CAMERA_CONFIG_FILE}")
        return cameras
    except Exception as e:
        logger.error(f"Error loading cameras: {e}")
        return []

def save_cameras(cameras: List[CameraConfig]) -> None:
    """Save camera configurations to JSON file."""
    CAMERA_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CAMERA_CONFIG_FILE.open("w") as f:
        json.dump([cam.__dict__ for cam in cameras], f, indent=4)

def get_camera_by_id(camera_id: str) -> Optional[CameraConfig]:
    """Get camera by ID."""
    return next((cam for cam in load_cameras() if cam.id == camera_id), None)

# Alias for compatibility
load_camera_by_id = get_camera_by_id

def add_camera(camera: CameraConfig) -> None:
    """Add a new camera configuration."""
    cameras = load_cameras()
    if any(cam.id == camera.id for cam in cameras):
        raise ValueError(f"Camera with id '{camera.id}' already exists.")
    cameras.append(camera)
    save_cameras(cameras)

def update_camera(camera: CameraConfig) -> None:
    """Update an existing camera configuration."""
    cameras = load_cameras()
    for i, cam in enumerate(cameras):
        if cam.id == camera.id:
            cameras[i] = camera
            save_cameras(cameras)
            return
    raise ValueError(f"Camera with id '{camera.id}' not found.")

def delete_camera(camera_id: str) -> None:
    """Delete a camera configuration."""
    cameras = load_cameras()
    cameras = [cam for cam in cameras if cam.id != camera_id]
    save_cameras(cameras) 