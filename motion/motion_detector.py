# motion/motion_detector.py
"""
Motion detection and filtering for smoke detection system.
"""

import numpy as np
import logging
import cv2
from typing import Tuple, Optional

from data_models.models import ProgramSettings

logger = logging.getLogger(__name__)

class MotionDetector:
    """Motion detection and filtering for smoke detection."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings

    # === MONOLITHIC-PARITY MODE ===
    def detect_motion_monolithic(self, video_array: np.ndarray) -> bool:
        """
        Monolithic-style motion detection:
        Compare last two frames, return True if max pixel difference exceeds threshold.
        Matches sd_utils_23.py logic (time_difference + check_max_pix).
        """
        if len(video_array) < 2:
            return False
        
        # Last two frames
        frame1 = video_array[-2].astype(np.float32)
        frame2 = video_array[-1].astype(np.float32)
        
        # Difference
        diff = np.abs(frame2 - frame1)
        max_pix = np.max(diff)
        
        logger.debug(
            f"[MotionDetector-Mono] Max pixel diff: {max_pix:.2f}, "
            f"threshold: {self.settings.motion_threshold}"
        )
        
        return max_pix > self.settings.motion_threshold

    # === CURRENT METHODS (KEPT FOR FUTURE USE) ===
    def detect_motion(self, frame1: np.ndarray, frame2: np.ndarray) -> Tuple[bool, float]:
        """Mean-difference based motion detection."""
        try:
            if frame1.shape != frame2.shape:
                frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
                
            f1 = frame1.astype(np.float32)
            f2 = frame2.astype(np.float32)
            diff = np.abs(f2 - f1)
            motion_score = np.mean(diff)
            motion_detected = motion_score > self.settings.motion_threshold
            
            logger.debug(
                f"[MotionDetector] Motion score: {motion_score:.2f}, "
                f"threshold: {self.settings.motion_threshold}"
            )
            return motion_detected, motion_score
            
        except Exception as e:
            logger.exception(f"[MotionDetector] Error detecting motion: {e}")
            return False, 0.0
    
    def count_motion_pixels(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray,
        threshold: Optional[float] = None
    ) -> int:
        """Count pixels above threshold."""
        if threshold is None:
            threshold = self.settings.motion_threshold
            
        try:
            if frame1.shape != frame2.shape:
                frame2 = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
                
            diff = np.abs(frame2.astype(np.float32) - frame1.astype(np.float32))
            motion_pixels = np.sum(diff > threshold)
            
            logger.debug(f"[MotionDetector] Motion pixels: {motion_pixels}")
            return int(motion_pixels)
            
        except Exception as e:
            logger.exception(f"[MotionDetector] Error counting motion pixels: {e}")
            return 0
    
    def is_motion_significant(self, frame1: np.ndarray, frame2: np.ndarray) -> bool:
        """True if motion is below count threshold."""
        motion_pixels = self.count_motion_pixels(frame1, frame2)
        return motion_pixels < self.settings.motion_count_threshold
    
    def filter_by_motion(self, video_array: np.ndarray) -> bool:
        """Average motion pixel method (current modular logic)."""
        try:
            if len(video_array) < 2:
                return False
                
            total_motion_pixels = 0
            for i in range(len(video_array) - 1):
                motion_pixels = self.count_motion_pixels(video_array[i], video_array[i + 1])
                total_motion_pixels += motion_pixels
                
            avg_motion_pixels = total_motion_pixels / (len(video_array) - 1)
            acceptable = avg_motion_pixels < self.settings.motion_count_threshold
            
            logger.debug(
                f"[MotionDetector] Avg motion pixels: {avg_motion_pixels:.1f}, "
                f"threshold: {self.settings.motion_count_threshold}"
            )
            return acceptable
            
        except Exception as e:
            logger.exception(f"[MotionDetector] Error filtering by motion: {e}")
            return False