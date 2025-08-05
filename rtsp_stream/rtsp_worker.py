# rtsp_stream/rtsp_worker.py
"""
Individual RTSP camera worker for handling single camera streams.
"""

import threading
import time
import logging
import numpy as np
import cv2
from typing import Optional

from data_models.models import CameraConfig, ProgramSettings

logger = logging.getLogger(__name__)

class RTSPWorker:
    """Individual RTSP camera worker."""
    
    def __init__(self, camera: CameraConfig, settings: ProgramSettings):
        self.camera = camera
        self.settings = settings
        self.frame: Optional[np.ndarray] = None
        self.lock = threading.Lock()
        self.running = False
        self.cap: Optional[cv2.VideoCapture] = None
        
    def run(self) -> None:
        """Main worker loop for capturing frames."""
        logger.info(f"[{self.camera.id}] Starting RTSP worker")
        
        try:
            # Build RTSP URL
            rtsp_url = self._build_rtsp_url()
            #logger.info(f"[{self.camera.id}] Connecting to {rtsp_url}")
            
            # Open video capture
            self.cap = cv2.VideoCapture(rtsp_url)
            if not self.cap.isOpened():
                raise Exception(f"Failed to open RTSP stream: {rtsp_url}")
            
            # Set capture properties
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FPS, self.camera.target_fps)
            
            self.running = True
            logger.info(f"[{self.camera.id}] RTSP stream connected successfully")
            
            # Main capture loop
            while self.running:
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        # Store raw BGR frame - let preprocessing handle conversions
                        self.frame = frame.copy()
                else:
                    logger.warning(f"[{self.camera.id}] Failed to read frame from RTSP stream")
                    time.sleep(self.settings.reconnect_delay_sec)
                    
        except Exception as e:
            logger.exception(f"[{self.camera.id}] Error in RTSP worker: {e}")
        finally:
            self._cleanup()
            logger.info(f"[{self.camera.id}] RTSP worker stopped")
    
    def _build_rtsp_url(self) -> str:
        """Build RTSP URL from camera configuration."""
        if self.camera.username and self.camera.password:
            auth = f"{self.camera.username}:{self.camera.password}@"
        else:
            auth = ""
            
        return f"rtsp://{auth}{self.camera.ip}:{self.camera.port}{self.camera.stream_path}"
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        self.running = False
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        with self.lock:
            self.frame = None
    
    def stop(self) -> None:
        """Stop the worker."""
        logger.info(f"[{self.camera.id}] Stopping RTSP worker")
        self.running = False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get the latest frame.
        
        Returns:
            Latest frame or None if not available
        """
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
            return None
    
    def is_running(self) -> bool:
        """
        Check if the worker is running.
        
        Returns:
            True if worker is running
        """
        return self.running and self.cap is not None and self.cap.isOpened() 