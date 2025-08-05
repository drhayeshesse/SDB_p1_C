# preprocessing/frame_normalizer.py
"""
Frame normalization and preprocessing module.
Handles all video processing operations: BGR→Grayscale→Resize→Buffer Management
"""

import cv2
import numpy as np
import logging
from typing import Dict, Optional, Tuple
from data_models.models import CameraConfig, ProgramSettings
from frame_buffer.frame_buffer import FrameBuffer
from processing.grayscale_buffer import GrayscaleBuffer

logger = logging.getLogger(__name__)

class FrameNormalizer:
    """
    Centralized frame normalizer that handles all video processing in one place.
    Eliminates redundant BGR→Grayscale→Resize operations across multiple modules.
    """
    
    def __init__(self, settings: ProgramSettings, frame_buffer: FrameBuffer = None):
        self.settings = settings
        self.frame_size = (settings.frame_width, settings.frame_height)
        
        # Use provided frame buffer or create new one
        self.frame_buffer = frame_buffer if frame_buffer is not None else FrameBuffer(self.frame_size)
        
        # Try to use optimized grayscale buffer, fall back to standard if not available
        try:
            from processing.grayscale_buffer_optimized import OptimizedGrayscaleBuffer
            self.grayscale_buffer = OptimizedGrayscaleBuffer(maxlen=11, frame_size=self.frame_size)
            logger.info("[FrameNormalizer] Using Numba-optimized grayscale buffer")
        except ImportError:
            from processing.grayscale_buffer import GrayscaleBuffer
            self.grayscale_buffer = GrayscaleBuffer(maxlen=11, frame_size=self.frame_size)
            logger.info("[FrameNormalizer] Using standard grayscale buffer")
        
        # Create smoke detector once and reuse it (try optimized version first)
        try:
            from smoke.smoke_detector_optimized import OptimizedSmokeDetector
            self.smoke_detector = OptimizedSmokeDetector(self.settings)
            logger.info("[FrameNormalizer] Using Numba-optimized smoke detector")
        except ImportError:
            from smoke.smoke_detector import SmokeDetector
            self.smoke_detector = SmokeDetector(self.settings)
            logger.info("[FrameNormalizer] Using standard smoke detector")
        
        # Store last processed frame hash to avoid processing identical frames
        self.last_frame_hashes = {}
        
        logger.info(f"[FrameNormalizer] Initialized with frame size: {self.frame_size}")
    
    def process_frame(self, 
                     camera_id: str, 
                     bgr_frame: np.ndarray, 
                     camera: CameraConfig) -> Tuple[bool, Dict[str, np.ndarray]]:
        """
        Single point of video processing. Handles all conversions and buffer management.
        
        Args:
            camera_id: Camera identifier
            bgr_frame: Raw BGR frame from camera
            camera: Camera configuration
            
        Returns:
            Tuple of (smoke_detected, processed_frames_dict)
        """
        try:
            # Step 1: Single BGR→Grayscale conversion
            if len(bgr_frame.shape) == 3 and bgr_frame.shape[2] == 3:
                gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
            else:
                gray = bgr_frame.astype(np.float32)
            
            # Step 2: Single resize operation
            gray_resized = cv2.resize(gray, self.frame_size, interpolation=cv2.INTER_AREA)
            
            # Step 2.5: Check if frame has changed significantly (simple optimization)
            frame_hash = hash(gray_resized.tobytes())
            if camera_id in self.last_frame_hashes and self.last_frame_hashes[camera_id] == frame_hash:
                logger.debug(f"[CAM:{camera_id}] Frame unchanged, skipping processing")
                return False, {}
            self.last_frame_hashes[camera_id] = frame_hash
            logger.info(f"[CAM:{camera_id}] Processing new frame | shape: {gray_resized.shape}")
            

            
            # Step 3: Add to grayscale buffer for temporal analysis
            self.grayscale_buffer.add_frame(camera_id, gray_resized)
            
            # Step 4: Get temporal sequence for detection
            sequence = self.grayscale_buffer.get_sequence(camera_id)
            if sequence is None:
                logger.debug(f"[CAM:{camera_id}] Waiting for full frame sequence")
                return False, {}
            
            logger.info(f"[CAM:{camera_id}] Sequence ready | frames: {len(sequence)}")
            
            # Step 5: Run smoke detection using the pre-initialized detector
            logger.info(f"[CAM:{camera_id}] Running smoke detection...")
            smoke_detected, wass_min = self.smoke_detector.check_video_for_smoke3b(sequence, camera_id)
            logger.info(f"[CAM:{camera_id}] Smoke detection complete | detected: {smoke_detected}")
            
            # Step 6: Calculate frame comparison panels (like in main_24_v2.py)
            # Get base frame (first frame in sequence) for comparison
            base_frame = sequence[0]
            current_frame = sequence[-1]  # Most recent frame
            
            # Calculate difference frame (optimized)
            if hasattr(self.smoke_detector, 'compute_frame_difference'):
                diff_frame = self.smoke_detector.compute_frame_difference(current_frame, base_frame)
            else:
                diff_frame = current_frame - base_frame
            
            # Calculate Wasserstein distance panel
            logger.debug(f"[CAM:{camera_id}] Calculating Wasserstein distance...")
            csw_ww, output_panel_wass = self.smoke_detector.compare_frames_ww(
                base_frame, current_frame, self.settings.sensitivity, self.settings.sliding_window
            )
            
            # Calculate mean distance panel  
            logger.debug(f"[CAM:{camera_id}] Calculating mean distance...")
            csw_mm, output_panel_mean = self.smoke_detector.compare_frames_mean(
                base_frame, current_frame, self.settings.sensitivity, self.settings.sliding_window
            )
            
            # Create processed frames dictionary for dashboard
            processed_frames = {
                "current": current_frame,
                "base": base_frame,
                "difference": diff_frame,
                "wasserstein": wass_min,
                "mean": output_panel_mean,
                "difference_wass": output_panel_wass,
                "heatmap": wass_min,  # The validation heatmap is the wass_min array
            }
            
            logger.info(f"[CAM:{camera_id}] Frame processing complete | stages: {len(processed_frames)}")
            
            # Step 6: Update frame buffer for dashboard visualization
            logger.debug(f"[CAM:{camera_id}] About to update frame buffer")
            self._update_frame_buffer(camera_id, bgr_frame, gray_resized, processed_frames)
            logger.debug(f"[CAM:{camera_id}] Frame buffer update completed")
            
            logger.info(f"[CAM:{camera_id}] Processing cycle complete | smoke_detected: {smoke_detected}")
            return bool(smoke_detected), processed_frames
            
        except Exception as e:
            logger.exception(f"[CAM:{camera_id}] Error in frame processing: {e}")
            return False, {}
    
    def _update_frame_buffer(self, 
                           camera_id: str, 
                           bgr_frame: np.ndarray, 
                           gray_frame: np.ndarray,
                           processed_frames: Dict[str, np.ndarray]):
        """
        Update frame buffer with all processing stages for dashboard visualization.
        """
        try:
            logger.debug(f"[CAM:{camera_id}] Starting frame buffer update")
            
            # Resize BGR frame for dashboard
            resized_bgr = cv2.resize(bgr_frame, self.frame_size, interpolation=cv2.INTER_AREA)
            logger.debug(f"[CAM:{camera_id}] Resized BGR frame: {resized_bgr.shape}")
            
            # Update frame buffer with all stages
            self.frame_buffer.set_frame(camera_id, "original", resized_bgr)
            logger.debug(f"[CAM:{camera_id}] Set original frame")
            
            # Update processed frames if available
            if "current" in processed_frames:
                self.frame_buffer.set_frame(camera_id, "current", self._resize_for_dashboard(processed_frames["current"]))
                logger.debug(f"[CAM:{camera_id}] Set current frame")
            if "base" in processed_frames:
                self.frame_buffer.set_frame(camera_id, "base", self._resize_for_dashboard(processed_frames["base"]))
                logger.debug(f"[CAM:{camera_id}] Set base frame")
            if "difference" in processed_frames:
                self.frame_buffer.set_frame(camera_id, "difference", self._resize_for_dashboard(processed_frames["difference"]))
                logger.debug(f"[CAM:{camera_id}] Set difference frame")
            if "wasserstein" in processed_frames:
                self.frame_buffer.set_frame(camera_id, "wasserstein", self._resize_for_dashboard(processed_frames["wasserstein"]))
                logger.debug(f"[CAM:{camera_id}] Set wasserstein frame")
            if "mean" in processed_frames:
                self.frame_buffer.set_frame(camera_id, "mean", self._resize_for_dashboard(processed_frames["mean"]))
                logger.debug(f"[CAM:{camera_id}] Set mean frame")
            if "difference_wass" in processed_frames:
                self.frame_buffer.set_frame(camera_id, "difference_wass", self._resize_for_dashboard(processed_frames["difference_wass"]))
                logger.debug(f"[CAM:{camera_id}] Set difference_wass frame")
            if "heatmap" in processed_frames:
                self.frame_buffer.set_frame(camera_id, "heatmap", self._resize_for_dashboard(processed_frames["heatmap"]))
                logger.debug(f"[CAM:{camera_id}] Set heatmap frame")
                
            logger.debug(f"[CAM:{camera_id}] Frame buffer updated for all stages")
            
        except Exception as e:
            logger.exception(f"[CAM:{camera_id}] Error updating frame buffer: {e}")
    
    def _resize_for_dashboard(self, frame: np.ndarray) -> np.ndarray:
        """
        Resize frame for dashboard visualization, ensuring uint8 format.
        """
        try:
            resized = cv2.resize(frame, self.frame_size, interpolation=cv2.INTER_AREA)
            resized = np.clip(resized, 0, 255).astype(np.uint8)
            return resized
        except Exception as e:
            logger.exception(f"Error resizing frame for dashboard: {e}")
            return np.zeros(self.frame_size, dtype=np.uint8)
    
    def normalize_frame(self, frame: np.ndarray, target_size: tuple = None) -> np.ndarray:
        """
        Normalize a single frame to standard format.
        
        Args:
            frame: Input frame
            target_size: Target size (width, height)
            
        Returns:
            Normalized frame
        """
        if target_size is None:
            target_size = self.frame_size
            
        # Convert to grayscale if needed
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame
            
        # Resize to target size
        resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA)
        
        return resized.astype(np.float32) 