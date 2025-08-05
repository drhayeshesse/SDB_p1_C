# processing/grayscale_buffer.py
"""
Grayscale frame buffer for temporal analysis.
Maintains sequences of grayscale frames for smoke detection algorithms.
"""

import numpy as np
from collections import deque
from threading import Lock
from typing import Dict, Optional
import cv2
import logging

logger = logging.getLogger(__name__)

class GrayscaleBuffer:
    """Buffer for maintaining grayscale frame sequences for temporal analysis."""
    
    def __init__(self, maxlen: int = 11, frame_size: tuple = (896, 504)):
        self.buffers: Dict[str, deque] = {}
        self.locks: Dict[str, Lock] = {}
        self.maxlen = maxlen
        self.frame_size = frame_size

    def add_frame(self, camera_id: str, gray_frame: np.ndarray) -> None:
        """
        Add a grayscale frame to the buffer for a specific camera.
        
        Args:
            camera_id: Camera identifier
            gray_frame: Grayscale frame data
        """
        if camera_id not in self.buffers:
            self.buffers[camera_id] = deque(maxlen=self.maxlen)
            self.locks[camera_id] = Lock()
            logger.debug(f"[grayscale_buffer] Created buffer for camera {camera_id}")

        # Ensure frame is the correct size and type
        try:
            if gray_frame.shape[:2] != self.frame_size:
                resized = cv2.resize(gray_frame, self.frame_size)
            else:
                resized = gray_frame
            float_frame = resized.astype(np.float32)
        except Exception as e:
            logger.exception(f"[grayscale_buffer] Error processing grayscale frame for {camera_id}: {e}")
            return

        with self.locks[camera_id]:
            self.buffers[camera_id].append(float_frame)
            current_len = len(self.buffers[camera_id])
            logger.debug(f"[grayscale_buffer] Added frame to camera {camera_id} buffer ({current_len}/{self.maxlen}) | shape: {float_frame.shape}, dtype: {float_frame.dtype}")

    def get_sequence(self, camera_id: str) -> Optional[np.ndarray]:
        """
        Get the complete frame sequence for a camera.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Frame sequence as numpy array or None if not complete
        """
        if camera_id not in self.buffers:
            return None
            
        with self.locks[camera_id]:
            if len(self.buffers[camera_id]) == self.maxlen:
                sequence = np.stack(self.buffers[camera_id])
                logger.debug(f"[grayscale_buffer] Sequence ready for camera {camera_id} | shape: {sequence.shape}, dtype: {sequence.dtype}")
                return sequence
            else:
                logger.debug(f"[grayscale_buffer] Waiting for full sequence for camera {camera_id} ({len(self.buffers[camera_id])}/{self.maxlen})")
                return None 