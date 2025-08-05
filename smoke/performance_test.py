#!/usr/bin/env python3
"""
Performance test script to compare optimized vs standard patch utils.
"""

import time
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_performance():
    """Test performance of optimized vs standard patch utils."""
    
    # Create test data
    logger.info("Creating test data...")
    test_video = np.random.random((11, 504, 896)).astype(np.float32)
    sw = 16
    
    # Test standard patch utils
    try:
        from patch_utils import PatchUtils
        logger.info("Testing standard patch utils...")
        
        start_time = time.time()
        patch_utils = PatchUtils()
        
        # Test each function
        mean_array = patch_utils.compute_patches_mean(test_video, sw)
        wass_array = patch_utils.compute_patches_ww_diff_all(test_video, sw)
        mt = patch_utils.time_derivative(mean_array)
        st = patch_utils.time_difference(test_video)
        sxy = patch_utils.video_spatial_difference(test_video)
        mst = patch_utils.compute_patches_mean(st, sw)
        msxy = patch_utils.compute_patches_mean(sxy, sw)
        motion_count = patch_utils.check_max_pix(st, 0.5)
        ws_min = patch_utils.compute_min_over_time(wass_array)
        
        standard_time = time.time() - start_time
        logger.info(f"Standard patch utils time: {standard_time:.3f} seconds")
        
    except Exception as e:
        logger.error(f"Standard patch utils test failed: {e}")
        standard_time = None
    
    # Test optimized patch utils
    try:
        from patch_utils_optimized import OptimizedPatchUtils
        logger.info("Testing optimized patch utils...")
        
        start_time = time.time()
        patch_utils = OptimizedPatchUtils()
        
        # Test each function
        mean_array = patch_utils.compute_patches_mean(test_video, sw)
        wass_array = patch_utils.compute_patches_ww_diff_all(test_video, sw)
        mt = patch_utils.time_derivative(mean_array)
        st = patch_utils.time_difference(test_video)
        sxy = patch_utils.video_spatial_difference(test_video)
        mst = patch_utils.compute_patches_mean(st, sw)
        msxy = patch_utils.compute_patches_mean(sxy, sw)
        motion_count = patch_utils.check_max_pix(st, 0.5)
        ws_min = patch_utils.compute_min_over_time(wass_array)
        
        optimized_time = time.time() - start_time
        logger.info(f"Optimized patch utils time: {optimized_time:.3f} seconds")
        
    except Exception as e:
        logger.error(f"Optimized patch utils test failed: {e}")
        optimized_time = None
    
    # Compare results
    if standard_time and optimized_time:
        speedup = standard_time / optimized_time
        logger.info(f"Speedup: {speedup:.2f}x faster with Numba")
        logger.info(f"CPU time reduction: {((standard_time - optimized_time) / standard_time * 100):.1f}%")
    else:
        logger.warning("Could not complete performance comparison")

if __name__ == "__main__":
    test_performance() 