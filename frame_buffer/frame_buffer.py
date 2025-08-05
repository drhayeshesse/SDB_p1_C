# frame_buffer/frame_buffer.py
"""
Frame buffer for storing intermediate processing stages.
Used for dashboard visualization and MJPEG streaming.
"""

import threading
import logging
import numpy as np
import cv2
from typing import Optional

logger = logging.getLogger(__name__)

class FrameBuffer:
    """Frame buffer for storing intermediate processing stages."""
    
    def __init__(self, frame_size: tuple = (896, 504)):
        self.buffer = {}
        self.lock = threading.Lock()
        self.frame_size = frame_size

    def set_frame(self, camera_id: str, stage: str, frame: np.ndarray) -> None:
        """
        Set a frame for a specific camera and processing stage.
        
        Args:
            camera_id: Camera identifier
            stage: Processing stage (original, gray, mean, difference, wasserstein_logic)
            frame: Frame data
        """
        with self.lock:
            if camera_id not in self.buffer:
                self.buffer[camera_id] = {}
                logger.info(f"[frame_buffer] Created new entry for camera {camera_id}")

            # Resize frames to consistent size (only if needed)
            try:
                if frame.shape[:2] != self.frame_size:
                    frame = cv2.resize(frame, self.frame_size, interpolation=cv2.INTER_AREA)
            except Exception as e:
                logger.exception(f"[frame_buffer] Failed to resize frame for camera {camera_id}: {e}")

            # Ensure float32 for all internal stages except MJPEG (only if needed)
            if stage != "original" and frame.dtype != np.float32:
                try:
                    frame = frame.astype(np.float32, copy=False)  # Avoid copy if possible
                except Exception as e:
                    logger.warning(f"[frame_buffer] Failed to convert frame to float32 for stage '{stage}', camera {camera_id}: {e}")

            self.buffer[camera_id][stage] = frame

    def get_frame(self, camera_id: str, stage: str) -> Optional[np.ndarray]:
        """
        Get a frame for a specific camera and processing stage.
        
        Args:
            camera_id: Camera identifier
            stage: Processing stage
            
        Returns:
            Frame data or None if not available
        """
        with self.lock:
            try:
                frame = self.buffer.get(camera_id, {}).get(stage)
                if frame is None:
                    logger.debug(f"[frame_buffer] No frame found for camera {camera_id}, stage '{stage}'")
                return frame
            except Exception as e:
                logger.exception(f"[frame_buffer] Error retrieving frame for camera {camera_id}, stage '{stage}': {e}")
                return None

    def has_all_stages(self, camera_id: str, stages: list) -> bool:
        """
        Check if all specified stages are available for a camera.
        
        Args:
            camera_id: Camera identifier
            stages: List of required stages
            
        Returns:
            True if all stages are available
        """
        with self.lock:
            stages_available = list(self.buffer.get(camera_id, {}).keys())
            missing = [s for s in stages if s not in stages_available]
            if missing:
                logger.debug(f"[frame_buffer] Camera {camera_id} missing stages: {missing}")
            return all(stage in stages_available for stage in stages) 