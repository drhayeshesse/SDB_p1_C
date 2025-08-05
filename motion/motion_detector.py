# motion/motion_detector.py
"""
Motion detection and filtering for smoke detection system.
"""

import numpy as np
import logging
from typing import Tuple, Optional

from data_models.models import ProgramSettings

logger = logging.getLogger(__name__)

class MotionDetector:
    """Motion detection and filtering for smoke detection."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings
        
    def detect_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> Tuple[bool, float]:
        """
        Detect motion between two frames.
        
        Args:
            frame1: First frame
            frame2: Second frame
            
        Returns:
            Tuple of (motion_detected, motion_score)
        """
        try:
            # Ensure frames are the same size and type
            if frame1.shape != frame2.shape:
                frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
                
            # Convert to float32 for calculations
            f1 = frame1.astype(np.float32)
            f2 = frame2.astype(np.float32)
            
            # Calculate frame difference
            diff = np.abs(f2 - f1)
            
            # Calculate motion score (mean difference)
            motion_score = np.mean(diff)
            
            # Check if motion exceeds threshold
            motion_detected = motion_score > self.settings.motion_threshold
            
            logger.debug(f"[MotionDetector] Motion score: {motion_score:.2f}, threshold: {self.settings.motion_threshold}")
            
            return motion_detected, motion_score
            
        except Exception as e:
            logger.exception(f"[MotionDetector] Error detecting motion: {e}")
            return False, 0.0
    
    def count_motion_pixels(self, frame1: np.ndarray, frame2: np.ndarray, 
                           threshold: Optional[float] = None) -> int:
        """
        Count pixels that exceed motion threshold.
        
        Args:
            frame1: First frame
            frame2: Second frame
            threshold: Motion threshold (uses settings if None)
            
        Returns:
            Number of pixels above threshold
        """
        if threshold is None:
            threshold = self.settings.motion_threshold
            
        try:
            # Ensure frames are the same size
            if frame1.shape != frame2.shape:
                frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
                
            # Calculate frame difference
            diff = np.abs(frame2.astype(np.float32) - frame1.astype(np.float32))
            
            # Count pixels above threshold
            motion_pixels = np.sum(diff > threshold)
            
            logger.debug(f"[MotionDetector] Motion pixels: {motion_pixels}")
            
            return int(motion_pixels)
            
        except Exception as e:
            logger.exception(f"[MotionDetector] Error counting motion pixels: {e}")
            return 0
    
    def is_motion_significant(self, frame1: np.ndarray, frame2: np.ndarray) -> bool:
        """
        Check if motion is significant enough to warrant smoke detection.
        
        Args:
            frame1: First frame
            frame2: Second frame
            
        Returns:
            True if motion is significant
        """
        motion_pixels = self.count_motion_pixels(frame1, frame2)
        return motion_pixels < self.settings.motion_count_threshold
    
    def filter_by_motion(self, video_array: np.ndarray) -> bool:
        """
        Filter video sequence by motion analysis.
        
        Args:
            video_array: Video sequence (Nt, Ny, Nx)
            
        Returns:
            True if motion is acceptable for smoke detection
        """
        try:
            if len(video_array) < 2:
                return False
                
            # Calculate motion between consecutive frames
            total_motion_pixels = 0
            
            for i in range(len(video_array) - 1):
                motion_pixels = self.count_motion_pixels(video_array[i], video_array[i + 1])
                total_motion_pixels += motion_pixels
                
            # Average motion pixels per frame
            avg_motion_pixels = total_motion_pixels / (len(video_array) - 1)
            
            # Check if motion is acceptable
            acceptable = avg_motion_pixels < self.settings.motion_count_threshold
            
            logger.debug(f"[MotionDetector] Average motion pixels: {avg_motion_pixels:.1f}, threshold: {self.settings.motion_count_threshold}")
            
            return acceptable
            
        except Exception as e:
            logger.exception(f"[MotionDetector] Error filtering by motion: {e}")
            return False 