"""
Optimized smoke detector using Numba for frame comparison methods.
"""

import numpy as np
import logging
from typing import Tuple
from numba import jit, prange
import warnings

# Suppress Numba warnings
warnings.filterwarnings('ignore', category=UserWarning, module='numba')

# Try to use optimized version, fall back to original if not available
try:
    from .patch_utils_optimized import OptimizedPatchUtils
    PatchUtils = OptimizedPatchUtils
    logger = logging.getLogger(__name__)
    logger.info("Using Numba-optimized patch utils")
except ImportError:
    from .patch_utils import PatchUtils
    logger = logging.getLogger(__name__)
    logger.info("Using standard patch utils (Numba not available)")


@jit(nopython=True, parallel=True, cache=False)
def _compare_frames_ww_numba(ref_img, curr_img, sensitivity, sw):
    Ny, Nx = ref_img.shape[0:2]
    ntot = float(sw) ** 2
    output_panel = np.zeros_like(ref_img)
    csw = 0
    for ii in range(0, Ny - sw + 1, sw):
        for jj in range(0, Nx - sw + 1, sw):
            a = np.sort(curr_img[ii:ii + sw, jj:jj + sw].ravel())
            b = np.sort(ref_img[ii:ii + sw, jj:jj + sw].ravel())
            d = np.sum(np.abs(a - b)) / ntot
            output_panel[ii:ii + sw, jj:jj + sw] = d
            if d > sensitivity:
                csw = 1
    return csw, output_panel


@jit(nopython=True, parallel=True, cache=False)
def _compare_frames_mean_numba(ref_img, curr_img, sensitivity, sw):
    Ny, Nx = ref_img.shape[0:2]
    output_panel = np.zeros_like(ref_img)
    csw = 0
    for ii in range(0, Ny - sw + 1, sw):
        for jj in range(0, Nx - sw + 1, sw):
            m1 = np.mean(ref_img[ii:ii + sw, jj:jj + sw])
            m2 = np.mean(curr_img[ii:ii + sw, jj:jj + sw])
            d = np.abs(m2 - m1)
            output_panel[ii:ii + sw, jj:jj + sw] = d
            if d > sensitivity:
                csw = 1
    return csw, output_panel


@jit(nopython=True, parallel=True, cache=False)
def _compute_frame_difference_numba(current_frame, base_frame):
    return current_frame - base_frame


class OptimizedSmokeDetector:
    """Optimized smoke detector with Numba-accelerated frame comparisons."""

    def __init__(self, settings):
        self.settings = settings
        self.patch_utils = PatchUtils()
        logger.info("Warming up Numba JIT compilers for smoke detector...")
        self._warmup()
        logger.info("Numba optimizations ready for smoke detector")

    def _warmup(self):
        try:
            test_frame = np.random.random((64, 64)).astype(np.float32)
            _compare_frames_ww_numba(test_frame, test_frame, 0.5, 8)
            _compare_frames_mean_numba(test_frame, test_frame, 0.5, 8)
            _compute_frame_difference_numba(test_frame, test_frame)
        except Exception as e:
            logger.warning(f"Numba warmup failed for smoke detector: {e}")


            
#remove camera_id="TEST_CAM" just to camera_id
    def check_video_for_smoke(self, video_array, camera_id="TEST_CAM"):
        """Wrapper for compatibility with external calls."""
        return self.check_video_for_smoke3b(video_array, camera_id)

    def check_video_for_smoke3b(self, video_array: np.ndarray, camera_id: str) -> Tuple[int, np.ndarray]:
        logger.debug(f"[CAM:{camera_id}] Running check_video_for_smoke3b (optimized)")

        sw = self.settings.sliding_window
        sensitivity_val = self.settings.sensitivity_val
        n_patches_validate = self.settings.n_patches_validate

        Nt, Ny, Nx = video_array.shape[0:3]
        csw = 0

        # Compute analysis arrays
        mean_array = self.patch_utils.compute_patches_mean(video_array, sw)
        wass_array = self.patch_utils.compute_patches_ww_diff_all(video_array, sw)
        mt = self.patch_utils.time_derivative(mean_array)
        self.patch_utils.report_movie_stats(mt, camera_id)

        st = self.patch_utils.time_difference(video_array)
        sxy = self.patch_utils.video_spatial_difference(video_array)
        mst = self.patch_utils.compute_patches_mean(st, sw)
        msxy = self.patch_utils.compute_patches_mean(sxy, sw)
        self.patch_utils.report_movie_stats(mst, camera_id)
        self.patch_utils.report_movie_stats(msxy, camera_id)

        if self.settings.verbose > 0:
            logger.debug("  ")
            logger.debug(" ########### ###########")
            logger.debug(" ########### ###########")
            logger.debug(" ------ CHANGE DETECTED !!!")

        ws_min = self.patch_utils.compute_min_over_time(wass_array)

        # Always run smoke detection (motion gating handled externally)
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

    def compare_frames_ww(self, ref_img: np.ndarray, curr_img: np.ndarray, sensitivity: int, sw: int):
        logger.debug("Comparing frames with Wasserstein distance (optimized)")
        return _compare_frames_ww_numba(ref_img.astype(np.float32), curr_img.astype(np.float32), sensitivity, sw)

    def compare_frames_mean(self, ref_img: np.ndarray, curr_img: np.ndarray, sensitivity: int, sw: int):
        logger.debug("Comparing frames using mean differences (optimized)")
        return _compare_frames_mean_numba(ref_img.astype(np.float32), curr_img.astype(np.float32), sensitivity, sw)

    def compute_frame_difference(self, current_frame: np.ndarray, base_frame: np.ndarray):
        return _compute_frame_difference_numba(current_frame, base_frame)


# Alias so other code/tests expecting SmokeDetector still work
SmokeDetector = OptimizedSmokeDetector