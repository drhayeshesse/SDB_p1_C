# smoke/patch_utils.py
"""
Patch-wise computation utilities for smoke detection.
Contains all the low-level patch processing functions.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

class PatchUtils:
    """
    Utility class for patch-wise computations used in smoke detection.
    """
    
    def compute_patches_ww_diff_all(self, video_array: np.ndarray, sw: int) -> np.ndarray:
        """
        Compute Wasserstein patch-wise difference between all pairs of frames.
        
        Args:
            video_array: Video sequence (Nt, Ny, Nx)
            sw: Sliding window size
            
        Returns:
            Wasserstein difference array (Nt-1, Ny_patches, Nx_patches)
        """
        logger.debug("Computing Wasserstein patch-wise difference (all pairs)")
        Nt, Ny, Nx = video_array.shape[0:3]
        ntot = float(sw) ** 2
        output_array = np.zeros((Nt - 1, len(range(0, Ny - sw + 1, sw)), len(range(0, Nx - sw + 1, sw))), dtype=np.float32)
        
        for t in range(0, Nt - 1):
            for i, ii in enumerate(range(0, Ny - sw + 1, sw)):
                for j, jj in enumerate(range(0, Nx - sw + 1, sw)):
                    w_min = 100000000.0
                    for tt in range(t + 1, Nt):
                        curr_patch = video_array[t, ii:ii + sw, jj:jj + sw]
                        next_patch = video_array[tt, ii:ii + sw, jj:jj + sw]
                        a = np.sort(next_patch, axis=None)
                        b = np.sort(curr_patch, axis=None)
                        v = a - b
                        d = np.linalg.norm(v, 1)
                        d = d / ntot
                        w_min = min(d, w_min)
                    output_array[t, i, j] = w_min
        return output_array
    
    def compute_patches_mean(self, video_array: np.ndarray, sw: int) -> np.ndarray:
        """
        Compute patch-wise mean for each frame.
        
        Args:
            video_array: Video sequence (Nt, Ny, Nx)
            sw: Sliding window size
            
        Returns:
            Mean array (Nt, Ny_patches, Nx_patches)
        """
        logger.debug("Computing patch-wise mean")
        Nt, Ny, Nx = video_array.shape[0:3]
        output_array = np.zeros((Nt, len(range(0, Ny - sw + 1, sw)), len(range(0, Nx - sw + 1, sw))), dtype=np.float32)
        
        for t in range(Nt):
            for i, ii in enumerate(range(0, Ny - sw + 1, sw)):
                for j, jj in enumerate(range(0, Nx - sw + 1, sw)):
                    curr_patch = video_array[t, ii:ii + sw, jj:jj + sw]
                    output_array[t, i, j] = curr_patch.mean()
        return output_array
    
    def compute_min_over_time(self, vt: np.ndarray) -> np.ndarray:
        """
        Compute minimum over time for each pixel/patch.
        
        Args:
            vt: Time-varying array (Nt, Ny, Nx)
            
        Returns:
            Minimum array (Ny, Nx)
        """
        logger.debug("Computing minimum over time")
        Nt, Ny, Nx = vt.shape[0:3]
        return_array = np.zeros((Ny, Nx), dtype=np.float32)
        
        for i in range(Ny):
            for j in range(Nx):
                time_trace = vt[:, i, j]
                return_array[i, j] = np.min(time_trace)
        return return_array
    
    def time_derivative(self, sf: np.ndarray) -> np.ndarray:
        """
        Compute time derivative of a signal.
        
        Args:
            sf: Input signal (Nt, Ny, Nx)
            
        Returns:
            Time derivative (Nt-1, Ny, Nx)
        """
        logger.debug("Computing time derivative")
        Nt, Ny, Nx = sf.shape[0:3]
        st = np.zeros((Nt - 1, Ny, Nx), dtype=np.float32)
        ws = 1
        
        for k in range(0, Nt - ws):
            st[k, :, :] = np.abs(sf[k + ws, :, :] - sf[k, :, :])
        return st
    
    def time_difference(self, sf: np.ndarray) -> np.ndarray:
        """
        Compute time difference between consecutive frames.
        
        Args:
            sf: Video sequence (Nt, Ny, Nx)
            
        Returns:
            Time difference array (Nt-1, Ny, Nx)
        """
        logger.debug("Computing time difference")
        Nt, Ny, Nx = sf.shape[0:3]
        st = np.zeros((Nt - 1, Ny, Nx), dtype=np.float32)
        
        for k in range(Nt - 1):
            st[k, :, :] = np.abs(sf[k + 1, :, :] - sf[k, :, :])
        return st
    
    def video_spatial_difference(self, sf: np.ndarray) -> np.ndarray:
        """
        Compute spatial differences in video frames.
        
        Args:
            sf: Video sequence (Nt, Ny, Nx)
            
        Returns:
            Spatial difference array (Nt, Ny, Nx)
        """
        logger.debug("Computing spatial difference")
        Nt, Ny, Nx = sf.shape[0:3]
        sxy = np.zeros_like(sf)
        sx = np.zeros((Ny, Nx))
        sy = np.zeros((Ny, Nx))
        
        for k in range(Nt):
            sx[1:Ny - 2, :] = (sf[k, 2:Ny - 1, :] - sf[k, 0:Ny - 3, :]) / 2.0
            sy[:, 1:Nx - 2] = (sf[k, :, 2:Nx - 1] - sf[k, :, 0:Nx - 3]) / 2.0
            sxy[k, :, :] = 0.5 * (np.abs(sx) + np.abs(sy))
        return sxy
    
    def check_max_pix(self, f: np.ndarray, trsh: float) -> int:
        """
        Count pixels above threshold.
        
        Args:
            f: Input array
            trsh: Threshold value
            
        Returns:
            Number of pixels above threshold
        """
        logger.debug("Checking max pixels above threshold")
        indices = np.abs(f) > trsh
        cum_sum = np.sum(indices)
        return cum_sum
    
    def report_movie_stats(self, f: np.ndarray, camera_id: str) -> None:
        """
        Report statistics for a movie array.
        
        Args:
            f: Input array
            camera_id: Camera identifier for logging
        """
        tmp = f[:, 1:-2, 1:-2]
        cum_sum = np.mean(tmp)
        c_min = np.min(tmp)
        c_max = np.max(tmp)
        logger.debug(f"[CAM:{camera_id}] STATS → mean: {cum_sum:.4f}, min: {c_min:.4f}, max: {c_max:.4f}, shape: {f.shape}") 