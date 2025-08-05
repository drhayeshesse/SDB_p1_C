# processing/grayscale_buffer_optimized.py
"""
Optimized grayscale frame buffer using Numba for temporal analysis.
"""

import numpy as np
from collections import deque
from threading import Lock
from typing import Dict, Optional
import cv2
import logging
from numba import jit, prange
import warnings

# Suppress Numba warnings
warnings.filterwarnings('ignore', category=UserWarning, module='numba')

logger = logging.getLogger(__name__)

@jit(nopython=True, parallel=True, cache=False)
def _resize_frame_numba(frame, target_size):
    """
    Numba-optimized frame resizing (simplified version).
    Note: This is a basic implementation since cv2.resize is not Numba-compatible.
    """
    # For now, return the frame as-is since cv2.resize is not Numba-compatible
    # The actual resizing will be done with cv2.resize in the main function
    return frame

@jit(nopython=True, parallel=True, cache=False)
def _convert_to_float32_numba(frame):
    """
    Numba-optimized conversion to float32.
    """
    return frame.astype(np.float32)

class OptimizedGrayscaleBuffer:
    """Optimized buffer for maintaining grayscale frame sequences for temporal analysis."""
    
    def __init__(self, maxlen: int = 11, frame_size: tuple = (896, 504)):
        self.buffers: Dict[str, deque] = {}
        self.locks: Dict[str, Lock] = {}
        self.maxlen = maxlen
        self.frame_size = frame_size
        
        # Warm up the JIT compilers
        logger.info("Warming up Numba JIT compilers for grayscale buffer...")
        self._warmup()
        logger.info("Numba optimizations ready for grayscale buffer")
    
    def _warmup(self):
        """Warm up the JIT compilers with small test data."""
        try:
            # Small test arrays for warmup
            test_frame = np.random.random((32, 32)).astype(np.float32)
            _convert_to_float32_numba(test_frame)
        except Exception as e:
            logger.warning(f"Numba warmup failed for grayscale buffer: {e}")

    def add_frame(self, camera_id: str, gray_frame: np.ndarray) -> None:
        """
        Add a grayscale frame to the buffer for a specific camera (optimized).
        
        Args:
            camera_id: Camera identifier
            gray_frame: Grayscale frame data
        """
        if camera_id not in self.buffers:
            self.buffers[camera_id] = deque(maxlen=self.maxlen)
            self.locks[camera_id] = Lock()
            logger.debug(f"[grayscale_buffer] Created buffer for camera {camera_id}")

        # Ensure frame is the correct size and type (optimized)
        try:
            if gray_frame.shape[:2] != self.frame_size:
                resized = cv2.resize(gray_frame, self.frame_size, interpolation=cv2.INTER_AREA)
            else:
                resized = gray_frame
            
            # Use Numba-optimized conversion
            float_frame = _convert_to_float32_numba(resized)
        except Exception as e:
            logger.exception(f"[grayscale_buffer] Error processing grayscale frame for {camera_id}: {e}")
            return

        with self.locks[camera_id]:
            self.buffers[camera_id].append(float_frame)
            current_len = len(self.buffers[camera_id])
            logger.debug(f"[grayscale_buffer] Added frame to camera {camera_id} buffer ({current_len}/{self.maxlen}) | shape: {float_frame.shape}, dtype: {float_frame.dtype}")

    def get_sequence(self, camera_id: str) -> Optional[np.ndarray]:
        """
        Get the complete frame sequence for a camera (optimized).
        
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