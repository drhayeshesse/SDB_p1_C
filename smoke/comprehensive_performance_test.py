#!/usr/bin/env python3
"""
Comprehensive performance test for all Numba optimizations.
"""

import time
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_all_optimizations():
    """Test performance of all optimized components."""
    
    logger.info("=== Comprehensive Numba Performance Test ===\n")
    
    # Create test data
    logger.info("Creating test data...")
    test_video = np.random.random((11, 504, 896)).astype(np.float32)
    test_frame = np.random.random((504, 896)).astype(np.float32)
    sw = 16
    
    results = {}
    
    # Test 1: Patch Utils
    logger.info("1. Testing Patch Utils...")
    try:
        from patch_utils import PatchUtils
        start_time = time.time()
        patch_utils = PatchUtils()
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
        results['patch_utils_standard'] = standard_time
        logger.info(f"   Standard: {standard_time:.3f} seconds")
    except Exception as e:
        logger.error(f"   Standard patch utils failed: {e}")
    
    try:
        from patch_utils_optimized import OptimizedPatchUtils
        start_time = time.time()
        patch_utils = OptimizedPatchUtils()
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
        results['patch_utils_optimized'] = optimized_time
        logger.info(f"   Optimized: {optimized_time:.3f} seconds")
        
        if 'patch_utils_standard' in results:
            speedup = results['patch_utils_standard'] / optimized_time
            logger.info(f"   Speedup: {speedup:.2f}x")
    except Exception as e:
        logger.error(f"   Optimized patch utils failed: {e}")
    
    # Test 2: Smoke Detector Frame Comparisons
    logger.info("\n2. Testing Smoke Detector Frame Comparisons...")
    try:
        import sys
        sys.path.append('..')
        from smoke.smoke_detector import SmokeDetector
        from utils.settings import load_settings
        settings = load_settings()
        
        start_time = time.time()
        smoke_detector = SmokeDetector(settings)
        csw_ww, output_panel_wass = smoke_detector.compare_frames_ww(test_frame, test_frame, 5, sw)
        csw_mm, output_panel_mean = smoke_detector.compare_frames_mean(test_frame, test_frame, 5, sw)
        standard_time = time.time() - start_time
        results['smoke_detector_standard'] = standard_time
        logger.info(f"   Standard: {standard_time:.3f} seconds")
    except Exception as e:
        logger.error(f"   Standard smoke detector failed: {e}")
    
    try:
        import sys
        sys.path.append('..')
        from smoke.smoke_detector_optimized import OptimizedSmokeDetector
        from utils.settings import load_settings
        settings = load_settings()
        
        start_time = time.time()
        smoke_detector = OptimizedSmokeDetector(settings)
        csw_ww, output_panel_wass = smoke_detector.compare_frames_ww(test_frame, test_frame, 5, sw)
        csw_mm, output_panel_mean = smoke_detector.compare_frames_mean(test_frame, test_frame, 5, sw)
        optimized_time = time.time() - start_time
        results['smoke_detector_optimized'] = optimized_time
        logger.info(f"   Optimized: {optimized_time:.3f} seconds")
        
        if 'smoke_detector_standard' in results:
            speedup = results['smoke_detector_standard'] / optimized_time
            logger.info(f"   Speedup: {speedup:.2f}x")
    except Exception as e:
        logger.error(f"   Optimized smoke detector failed: {e}")
    
    # Test 3: Grayscale Buffer
    logger.info("\n3. Testing Grayscale Buffer...")
    try:
        import sys
        sys.path.append('..')
        from processing.grayscale_buffer import GrayscaleBuffer
        start_time = time.time()
        buffer = GrayscaleBuffer(maxlen=11, frame_size=(896, 504))
        for i in range(11):
            buffer.add_frame("test", test_frame)
        sequence = buffer.get_sequence("test")
        standard_time = time.time() - start_time
        results['grayscale_buffer_standard'] = standard_time
        logger.info(f"   Standard: {standard_time:.3f} seconds")
    except Exception as e:
        logger.error(f"   Standard grayscale buffer failed: {e}")
    
    try:
        import sys
        sys.path.append('..')
        from processing.grayscale_buffer_optimized import OptimizedGrayscaleBuffer
        start_time = time.time()
        buffer = OptimizedGrayscaleBuffer(maxlen=11, frame_size=(896, 504))
        for i in range(11):
            buffer.add_frame("test", test_frame)
        sequence = buffer.get_sequence("test")
        optimized_time = time.time() - start_time
        results['grayscale_buffer_optimized'] = optimized_time
        logger.info(f"   Optimized: {optimized_time:.3f} seconds")
        
        if 'grayscale_buffer_standard' in results:
            speedup = results['grayscale_buffer_standard'] / optimized_time
            logger.info(f"   Speedup: {speedup:.2f}x")
    except Exception as e:
        logger.error(f"   Optimized grayscale buffer failed: {e}")
    
    # Summary
    logger.info("\n=== Performance Summary ===")
    total_standard = sum(v for k, v in results.items() if 'standard' in k)
    total_optimized = sum(v for k, v in results.items() if 'optimized' in k)
    
    logger.info(f"Total Standard Time: {total_standard:.3f} seconds")
    logger.info(f"Total Optimized Time: {total_optimized:.3f} seconds")
    
    if total_standard > 0 and total_optimized > 0:
        overall_speedup = total_standard / total_optimized
        cpu_reduction = ((total_standard - total_optimized) / total_standard) * 100
        logger.info(f"Overall Speedup: {overall_speedup:.2f}x")
        logger.info(f"CPU Reduction: {cpu_reduction:.1f}%")
    
    logger.info("===========================")

if __name__ == "__main__":
    test_all_optimizations() 