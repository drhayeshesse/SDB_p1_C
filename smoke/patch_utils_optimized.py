# smoke/patch_utils_optimized.py
"""
Optimized patch-wise computation utilities using Numba for smoke detection.
"""

import numpy as np
import logging
from numba import jit, prange
import warnings

# Suppress Numba warnings
warnings.filterwarnings('ignore', category=UserWarning, module='numba')

logger = logging.getLogger(__name__)

@jit(nopython=True, parallel=True, cache=False)
def _compute_patches_ww_diff_all_numba(video_array, sw):
    """
    Numba-optimized Wasserstein patch-wise difference computation.
    """
    Nt, Ny, Nx = video_array.shape[0:3]
    ntot = float(sw) ** 2
    ny_patches = len(range(0, Ny - sw + 1, sw))
    nx_patches = len(range(0, Nx - sw + 1, sw))
    output_array = np.zeros((Nt - 1, ny_patches, nx_patches), dtype=np.float32)
    
    for t in prange(0, Nt - 1):
        for i in range(ny_patches):
            ii = i * sw
            for j in range(nx_patches):
                jj = j * sw
                w_min = 100000000.0
                for tt in range(t + 1, Nt):
                    curr_patch = video_array[t, ii:ii + sw, jj:jj + sw]
                    next_patch = video_array[tt, ii:ii + sw, jj:jj + sw]
                    a = np.sort(next_patch.ravel())
                    b = np.sort(curr_patch.ravel())
                    v = a - b
                    d = np.sum(np.abs(v))  # L1 norm
                    d = d / ntot
                    w_min = min(d, w_min)
                output_array[t, i, j] = w_min
    return output_array

@jit(nopython=True, parallel=True, cache=False)
def _compute_patches_mean_numba(video_array, sw):
    """
    Numba-optimized patch-wise mean computation.
    """
    Nt, Ny, Nx = video_array.shape[0:3]
    ny_patches = len(range(0, Ny - sw + 1, sw))
    nx_patches = len(range(0, Nx - sw + 1, sw))
    output_array = np.zeros((Nt, ny_patches, nx_patches), dtype=np.float32)
    
    for t in prange(Nt):
        for i in range(ny_patches):
            ii = i * sw
            for j in range(nx_patches):
                jj = j * sw
                curr_patch = video_array[t, ii:ii + sw, jj:jj + sw]
                output_array[t, i, j] = np.mean(curr_patch)
    return output_array

@jit(nopython=True, parallel=True, cache=False)
def _compute_min_over_time_numba(vt):
    """
    Numba-optimized minimum over time computation.
    """
    Nt, Ny, Nx = vt.shape[0:3]
    return_array = np.zeros((Ny, Nx), dtype=np.float32)
    
    for i in prange(Ny):
        for j in range(Nx):
            time_trace = vt[:, i, j]
            return_array[i, j] = np.min(time_trace)
    return return_array

@jit(nopython=True, parallel=True, cache=False)
def _time_derivative_numba(sf):
    """
    Numba-optimized time derivative computation.
    """
    Nt, Ny, Nx = sf.shape[0:3]
    output_array = np.zeros((Nt - 1, Ny, Nx), dtype=np.float32)
    
    for t in prange(Nt - 1):
        for i in range(Ny):
            for j in range(Nx):
                output_array[t, i, j] = sf[t + 1, i, j] - sf[t, i, j]
    return output_array

@jit(nopython=True, parallel=True, cache=False)
def _time_difference_numba(sf):
    """
    Numba-optimized time difference computation.
    """
    Nt, Ny, Nx = sf.shape[0:3]
    output_array = np.zeros((Nt - 1, Ny, Nx), dtype=np.float32)
    
    for t in prange(Nt - 1):
        for i in range(Ny):
            for j in range(Nx):
                output_array[t, i, j] = sf[t + 1, i, j] - sf[t, i, j]
    return output_array

@jit(nopython=True, parallel=True, cache=False)
def _video_spatial_difference_numba(sf):
    """
    Numba-optimized spatial difference computation.
    """
    Nt, Ny, Nx = sf.shape[0:3]
    output_array = np.zeros((Nt, Ny, Nx), dtype=np.float32)
    
    for t in prange(Nt):
        for i in range(1, Ny - 1):
            for j in range(1, Nx - 1):
                # Compute spatial gradient
                dx = sf[t, i, j + 1] - sf[t, i, j - 1]
                dy = sf[t, i + 1, j] - sf[t, i - 1, j]
                output_array[t, i, j] = np.sqrt(dx * dx + dy * dy)
    return output_array

@jit(nopython=True, parallel=True, cache=False)
def _check_max_pix_numba(f, trsh):
    """
    Numba-optimized pixel threshold checking.
    """
    count = 0
    for i in prange(f.shape[0]):
        for j in range(f.shape[1]):
            for k in range(f.shape[2]):
                if f[i, j, k] > trsh:
                    count += 1
    return count

class OptimizedPatchUtils:
    """
    Optimized utility class for patch-wise computations using Numba.
    """
    
    def __init__(self):
        # Warm up the JIT compilers
        logger.info("Warming up Numba JIT compilers...")
        self._warmup()
        logger.info("Numba optimizations ready")
    
    def _warmup(self):
        """Warm up the JIT compilers with small test data."""
        try:
            # Small test arrays for warmup
            test_video = np.random.random((5, 32, 32)).astype(np.float32)
            test_array = np.random.random((5, 16, 16)).astype(np.float32)
            
            _compute_patches_ww_diff_all_numba(test_video, 8)
            _compute_patches_mean_numba(test_video, 8)
            _compute_min_over_time_numba(test_array)
            _time_derivative_numba(test_array)
            _time_difference_numba(test_array)
            _video_spatial_difference_numba(test_video)
            _check_max_pix_numba(test_array, 0.5)
        except Exception as e:
            logger.warning(f"Numba warmup failed: {e}")
    
    def compute_patches_ww_diff_all(self, video_array: np.ndarray, sw: int) -> np.ndarray:
        """
        Compute Wasserstein patch-wise difference between all pairs of frames (optimized).
        """
        logger.debug("Computing Wasserstein patch-wise difference (optimized)")
        return _compute_patches_ww_diff_all_numba(video_array, sw)
    
    def compute_patches_mean(self, video_array: np.ndarray, sw: int) -> np.ndarray:
        """
        Compute patch-wise mean for each frame (optimized).
        """
        logger.debug("Computing patch-wise mean (optimized)")
        return _compute_patches_mean_numba(video_array, sw)
    
    def compute_min_over_time(self, vt: np.ndarray) -> np.ndarray:
        """
        Compute minimum over time for each pixel/patch (optimized).
        """
        logger.debug("Computing minimum over time (optimized)")
        return _compute_min_over_time_numba(vt)
    
    def time_derivative(self, sf: np.ndarray) -> np.ndarray:
        """
        Compute time derivative of a signal (optimized).
        """
        logger.debug("Computing time derivative (optimized)")
        return _time_derivative_numba(sf)
    
    def time_difference(self, sf: np.ndarray) -> np.ndarray:
        """
        Compute time difference (optimized).
        """
        logger.debug("Computing time difference (optimized)")
        return _time_difference_numba(sf)
    
    def video_spatial_difference(self, sf: np.ndarray) -> np.ndarray:
        """
        Compute spatial difference (optimized).
        """
        logger.debug("Computing spatial difference (optimized)")
        return _video_spatial_difference_numba(sf)
    
    def check_max_pix(self, f: np.ndarray, trsh: float) -> int:
        """
        Check maximum pixels above threshold (optimized).
        """
        logger.debug("Checking max pixels above threshold (optimized)")
        return _check_max_pix_numba(f, trsh)
    
    def report_movie_stats(self, f: np.ndarray, camera_id: str) -> None:
        """
        Report movie statistics (unchanged).
        """
        logger.debug(f"[CAM:{camera_id}] STATS → mean: {f.mean():.4f}, min: {f.min():.4f}, max: {f.max():.4f}, shape: {f.shape}") 