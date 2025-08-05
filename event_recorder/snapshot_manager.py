# event_recorder/snapshot_manager.py
"""
Snapshot management for smoke detection events.
"""

import os
import logging
import numpy as np
import cv2
from typing import Optional
from datetime import datetime

from data_models.models import ProgramSettings

logger = logging.getLogger(__name__)

class SnapshotManager:
    """Manages image snapshots for smoke detection events."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings
        self.output_dir = "events"
        self._ensure_output_dir()
        
    def _ensure_output_dir(self) -> None:
        """Ensure the output directory exists."""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def save_snapshot(self, frame: np.ndarray, camera_id: str, 
                     timestamp: Optional[datetime] = None) -> str:
        """
        Save a frame as a snapshot image.
        
        Args:
            frame: Frame to save
            camera_id: Camera identifier
            timestamp: Event timestamp
            
        Returns:
            Path to saved image file
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        filename = f"snapshot_{camera_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Ensure frame is in uint8 format for saving
            if frame.dtype != np.uint8:
                frame = np.clip(frame, 0, 255).astype(np.uint8)
                
            # Convert grayscale to BGR if needed
            if len(frame.shape) == 2:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            else:
                frame_bgr = frame
                
            # Save image
            success = cv2.imwrite(filepath, frame_bgr)
            
            if success:
                logger.info(f"[SnapshotManager] Saved snapshot: {filepath}")
                return filepath
            else:
                logger.error(f"[SnapshotManager] Failed to save snapshot: {filepath}")
                return ""
                
        except Exception as e:
            logger.exception(f"[SnapshotManager] Error saving snapshot: {e}")
            return ""
    
    def save_processed_snapshot(self, frame: np.ndarray, camera_id: str, 
                              stage: str, timestamp: Optional[datetime] = None) -> str:
        """
        Save a processed frame (gray, mean, difference, etc.) as a snapshot.
        
        Args:
            frame: Processed frame to save
            camera_id: Camera identifier
            stage: Processing stage (gray, mean, difference, etc.)
            timestamp: Event timestamp
            
        Returns:
            Path to saved image file
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        filename = f"snapshot_{camera_id}_{stage}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Ensure frame is in uint8 format for saving
            if frame.dtype != np.uint8:
                frame = np.clip(frame, 0, 255).astype(np.uint8)
                
            # Convert grayscale to BGR if needed
            if len(frame.shape) == 2:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            else:
                frame_bgr = frame
                
            # Save image
            success = cv2.imwrite(filepath, frame_bgr)
            
            if success:
                logger.info(f"[SnapshotManager] Saved {stage} snapshot: {filepath}")
                return filepath
            else:
                logger.error(f"[SnapshotManager] Failed to save {stage} snapshot: {filepath}")
                return ""
                
        except Exception as e:
            logger.exception(f"[SnapshotManager] Error saving {stage} snapshot: {e}")
            return "" 