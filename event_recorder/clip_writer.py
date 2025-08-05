# event_recorder/clip_writer.py
"""
Video clip recording functionality for smoke detection events.
"""

import os
import time
import logging
import numpy as np
import cv2
from typing import List, Optional
from datetime import datetime

from data_models.models import ProgramSettings

logger = logging.getLogger(__name__)

class ClipWriter:
    """Handles video clip recording for smoke detection events."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings
        self.output_dir = "events"
        self._ensure_output_dir()
        
    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def save_video_array(self, video_array: np.ndarray, camera_id: str, 
                        timestamp: Optional[datetime] = None) -> str:
        """
        Save a video array as a .npy file.
        
        Args:
            video_array: Video sequence (Nt, Ny, Nx)
            camera_id: Camera identifier
            timestamp: Event timestamp
            
        Returns:
            Path to saved file
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        filename = f"smoke_event_{camera_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.npy"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            np.save(filepath, video_array)
            logger.info(f"[ClipWriter] Saved video array: {filepath} (shape: {video_array.shape})")
            return filepath
        except Exception as e:
            logger.exception(f"[ClipWriter] Error saving video array: {e}")
            return ""
    
    def save_video_clip(self, frames: List[np.ndarray], camera_id: str,
                       timestamp: Optional[datetime] = None) -> str:
        """
        Save frames as a video clip.
        
        Args:
            frames: List of frames
            camera_id: Camera identifier
            timestamp: Event timestamp
            
        Returns:
            Path to saved video file
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        filename = f"smoke_event_{camera_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.mp4"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            if not frames:
                logger.warning(f"[ClipWriter] No frames to save for camera {camera_id}")
                return ""
                
            # Get frame dimensions
            height, width = frames[0].shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(filepath, fourcc, 3.0, (width, height))
            
            # Write frames
            for frame in frames:
                # Ensure frame is in BGR format for video writing
                if len(frame.shape) == 2:  # Grayscale
                    frame_bgr = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_GRAY2BGR)
                else:  # Already BGR
                    frame_bgr = frame.astype(np.uint8)
                    
                out.write(frame_bgr)
                
            out.release()
            logger.info(f"[ClipWriter] Saved video clip: {filepath} ({len(frames)} frames)")
            return filepath
            
        except Exception as e:
            logger.exception(f"[ClipWriter] Error saving video clip: {e}")
            return ""
    
    def create_event_metadata(self, camera_id: str, timestamp: datetime, 
                            detection_confidence: float = 1.0) -> dict:
        """
        Create metadata for a smoke detection event.
        
        Args:
            camera_id: Camera identifier
            timestamp: Event timestamp
            detection_confidence: Detection confidence score
            
        Returns:
            Event metadata dictionary
        """
        return {
            "camera_id": camera_id,
            "timestamp": timestamp.isoformat(),
            "detection_confidence": detection_confidence,
            "event_type": "smoke_detection",
            "system_version": "SDB_p1"
        } 