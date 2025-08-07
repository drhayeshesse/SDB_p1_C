# smoke/smoke_detector.py
"""
Core smoke detection algorithms and logic.
Contains the main smoke detection pipeline and validation functions.
"""

import numpy as np
import logging
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

# Try to use optimized version, fall back to original if not available
try:
    from .patch_utils_optimized import OptimizedPatchUtils
    PatchUtils = OptimizedPatchUtils
    logger.info("Using Numba-optimized patch utils")
except ImportError:
    from .patch_utils import PatchUtils
    logger.info("Using standard patch utils (Numba not available)")

class SmokeDetector:
    """
    Main smoke detection engine that implements the two-phase detection system:
    1. Monitoring phase: Compare current frame to baseline
    2. Validation phase: Run full smoke detection on video sequence
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.patch_utils = PatchUtils()

 #remove camera_id="TEST_CAM" just to camera_id       
        
    def check_video_for_smoke(self, video_array, camera_id="TEST_CAM"):
        """Wrapper for compatibility."""
        return self.check_video_for_smoke3b(video_array, camera_id)
    def check_video_for_smoke3b(self, video_array: np.ndarray, camera_id: str) -> Tuple[int, np.ndarray]:
        """
        Main smoke detection function for validation phase.
        Implements the original check_video_for_smoke3b logic.
        
        Args:
            video_array: 11-frame video sequence (Nt, Ny, Nx)
            camera_id: Camera identifier for logging
            
        Returns:
            Tuple of (smoke_detected_flag, wass_min_array)
        """
        logger.debug(f"[CAM:{camera_id}] Running check_video_for_smoke3b")
        
        sw = self.settings.sliding_window
        sensitivity_val = self.settings.sensitivity_val
        motion_threshold = self.settings.motion_threshold
        n_patches_validate = self.settings.n_patches_validate

        Nt, Ny, Nx = video_array.shape[0:3]
        logger.debug(f"[CAM:{camera_id}] video_array shape: {video_array.shape}")
        csw = 0

        # Compute various analysis arrays
        mean_array = self.patch_utils.compute_patches_mean(video_array, sw)
        wass_array = self.patch_utils.compute_patches_ww_diff_all(video_array, sw)
        mt = self.patch_utils.time_derivative(mean_array)
        
        logger.debug(f"[CAM:{camera_id}] mt (time difference of mean array):")
        self.patch_utils.report_movie_stats(mt, camera_id)
        
        st = self.patch_utils.time_difference(video_array)
        sxy = self.patch_utils.video_spatial_difference(video_array)
        mst = self.patch_utils.compute_patches_mean(st, sw)
        msxy = self.patch_utils.compute_patches_mean(sxy, sw)
        
        logger.debug(f"[CAM:{camera_id}] mst (mean of time difference):")
        self.patch_utils.report_movie_stats(mst, camera_id)
        logger.debug(f"[CAM:{camera_id}] msxy (mean of spatial difference):")
        self.patch_utils.report_movie_stats(msxy, camera_id)
        

        if self.settings.verbose > 0:
            logger.debug("  ")
            logger.debug(" ########### ###########")
            logger.debug(" ########### ###########")
            logger.debug(" ------ CHANGE DETECTED !!!")

        if self.settings.verbose > 1:

            ws_min = self.patch_utils.compute_min_over_time(wass_array)

            Nt2 = wass_array.shape[0]
            wass_array_a = wass_array[0:int(Nt2 / 2), :, :].copy()
            wass_array_b = wass_array[int(Nt2 / 2):, :, :].copy()

            ws_min_a = self.patch_utils.compute_min_over_time(wass_array_a)
            ws_min_b = self.patch_utils.compute_min_over_time(wass_array_b)

            aind_a = np.argwhere(ws_min_a >= sensitivity_val)
            aind_b = np.argwhere(ws_min_b >= sensitivity_val)

            if len(aind_a) > n_patches_validate and len(aind_b) > n_patches_validate:
                logger.info(f"[CAM:{camera_id}] Smoke detected")
                csw = 1
            else:
                logger.debug(f"[CAM:{camera_id}] Activation not met")

            return csw, ws_min
    
    def compare_frames_ww(self, ref_img: np.ndarray, curr_img: np.ndarray, 
                         sensitivity: int, sw: int) -> Tuple[int, np.ndarray]:
        """
        Compare frames using Wasserstein distance (monitoring phase).
        
        Args:
            ref_img: Reference frame
            curr_img: Current frame
            sensitivity: Detection threshold
            sw: Sliding window size
            
        Returns:
            Tuple of (change_detected_flag, output_panel)
        """
        logger.debug("Comparing frames with Wasserstein distance")
        Ny, Nx = ref_img.shape[0:2]
        ntot = float(sw) ** 2
        ref_gray = ref_img.astype(np.float32)
        curr_gray = curr_img.astype(np.float32)
        output_panel = np.zeros_like(ref_gray)
        csw = 0
        
        for ii in range(0, Ny - sw + 1, sw):
            for jj in range(0, Nx - sw + 1, sw):
                a = np.sort(curr_gray[ii:ii + sw, jj:jj + sw], axis=None)
                b = np.sort(ref_gray[ii:ii + sw, jj:jj + sw], axis=None)
                d = np.linalg.norm(a - b, 1) / ntot
                output_panel[ii:ii + sw, jj:jj + sw] = d
                if d > sensitivity:
                    csw = 1
        return csw, output_panel
    
    def compare_frames_mean(self, ref_img: np.ndarray, curr_img: np.ndarray, 
                           sensitivity: int, sw: int) -> Tuple[int, np.ndarray]:
        """
        Compare frames using mean differences (monitoring phase).
        
        Args:
            ref_img: Reference frame
            curr_img: Current frame
            sensitivity: Detection threshold
            sw: Sliding window size
            
        Returns:
            Tuple of (change_detected_flag, output_panel)
        """
        logger.debug("Comparing frames using mean differences")
        Ny, Nx = ref_img.shape[0:2]
        ref_gray = ref_img.astype(np.float32)
        curr_gray = curr_img.astype(np.float32)
        output_panel = np.zeros_like(ref_gray)
        csw = 0
        
        for ii in range(0, Ny - sw + 1, sw):
            for jj in range(0, Nx - sw + 1, sw):
                m1 = ref_gray[ii:ii + sw, jj:jj + sw].mean()
                m2 = curr_gray[ii:ii + sw, jj:jj + sw].mean()
                d = np.abs(m2 - m1)
                output_panel[ii:ii + sw, jj:jj + sw] = d
                if d > sensitivity:
                    csw = 1
        return csw, output_panel 
