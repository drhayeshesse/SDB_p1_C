# benchmark/benchmark.py
"""
Performance benchmarking for the smoke detection system.
"""

import time
import logging
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime

from data_models.models import ProgramSettings
from smoke.smoke_detector import SmokeDetector

logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Performance benchmarking for smoke detection algorithms."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings
        self.smoke_detector = SmokeDetector(settings)
        self.results = {}
        
    def benchmark_smoke_detection(self, test_videos: List[np.ndarray]) -> Dict[str, Any]:
        """
        Benchmark smoke detection performance.
        
        Args:
            test_videos: List of test video arrays
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"[Benchmark] Starting smoke detection benchmark with {len(test_videos)} test videos")
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'test_videos': len(test_videos),
                'processing_times': [],
                'detection_results': [],
                'memory_usage': [],
                'accuracy': 0.0
            }
            
            for i, video in enumerate(test_videos):
                logger.debug(f"[Benchmark] Processing test video {i+1}/{len(test_videos)}")
                
                # Measure processing time
                start_time = time.time()
                detection_result, wass_min = self.smoke_detector.check_video_for_smoke3b(video, f"test_{i}")
                processing_time = time.time() - start_time
                
                # Record results
                results['processing_times'].append(processing_time)
                results['detection_results'].append(detection_result)
                
                logger.debug(f"[Benchmark] Video {i+1}: detection={detection_result}, time={processing_time:.3f}s")
            
            # Calculate statistics
            results['avg_processing_time'] = np.mean(results['processing_times'])
            results['min_processing_time'] = np.min(results['processing_times'])
            results['max_processing_time'] = np.max(results['processing_times'])
            results['std_processing_time'] = np.std(results['processing_times'])
            results['fps'] = 1.0 / results['avg_processing_time'] if results['avg_processing_time'] > 0 else 0
            
            logger.info(f"[Benchmark] Smoke detection benchmark completed: "
                       f"avg_time={results['avg_processing_time']:.3f}s, "
                       f"fps={results['fps']:.2f}")
            
            self.results['smoke_detection'] = results
            return results
            
        except Exception as e:
            logger.exception(f"[Benchmark] Error in smoke detection benchmark: {e}")
            return {'error': str(e)}
    
    def benchmark_frame_processing(self, test_frames: List[np.ndarray]) -> Dict[str, Any]:
        """
        Benchmark frame processing performance.
        
        Args:
            test_frames: List of test frames
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"[Benchmark] Starting frame processing benchmark with {len(test_frames)} test frames")
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'test_frames': len(test_frames),
                'processing_times': [],
                'frame_sizes': []
            }
            
            for i, frame in enumerate(test_frames):
                logger.debug(f"[Benchmark] Processing test frame {i+1}/{len(test_frames)}")
                
                # Measure processing time for different operations
                start_time = time.time()
                
                # BGR to Grayscale conversion
                if len(frame.shape) == 3:
                    gray = self._convert_to_grayscale(frame)
                else:
                    gray = frame
                
                # Resize operation
                resized = self._resize_frame(gray)
                
                processing_time = time.time() - start_time
                
                # Record results
                results['processing_times'].append(processing_time)
                results['frame_sizes'].append(frame.shape)
                
                logger.debug(f"[Benchmark] Frame {i+1}: time={processing_time:.3f}s, size={frame.shape}")
            
            # Calculate statistics
            results['avg_processing_time'] = np.mean(results['processing_times'])
            results['min_processing_time'] = np.min(results['processing_times'])
            results['max_processing_time'] = np.max(results['processing_times'])
            results['std_processing_time'] = np.std(results['processing_times'])
            results['fps'] = 1.0 / results['avg_processing_time'] if results['avg_processing_time'] > 0 else 0
            
            logger.info(f"[Benchmark] Frame processing benchmark completed: "
                       f"avg_time={results['avg_processing_time']:.3f}s, "
                       f"fps={results['fps']:.2f}")
            
            self.results['frame_processing'] = results
            return results
            
        except Exception as e:
            logger.exception(f"[Benchmark] Error in frame processing benchmark: {e}")
            return {'error': str(e)}
    
    def benchmark_memory_usage(self, test_data: List[np.ndarray]) -> Dict[str, Any]:
        """
        Benchmark memory usage patterns.
        
        Args:
            test_data: List of test data arrays
            
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"[Benchmark] Starting memory usage benchmark")
            
            import psutil
            process = psutil.Process()
            
            results = {
                'timestamp': datetime.now().isoformat(),
                'initial_memory': process.memory_info().rss / (1024**2),  # MB
                'peak_memory': 0,
                'memory_usage': []
            }
            
            for i, data in enumerate(test_data):
                logger.debug(f"[Benchmark] Processing memory test {i+1}/{len(test_data)}")
                
                # Record memory before processing
                memory_before = process.memory_info().rss / (1024**2)
                
                # Simulate processing
                processed_data = self._process_data(data)
                
                # Record memory after processing
                memory_after = process.memory_info().rss / (1024**2)
                memory_used = memory_after - memory_before
                
                results['memory_usage'].append({
                    'test_id': i,
                    'memory_before_mb': memory_before,
                    'memory_after_mb': memory_after,
                    'memory_used_mb': memory_used,
                    'data_size_mb': data.nbytes / (1024**2)
                })
                
                results['peak_memory'] = max(results['peak_memory'], memory_after)
                
                # Clean up
                del processed_data
                
            # Calculate statistics
            memory_used_list = [m['memory_used_mb'] for m in results['memory_usage']]
            results['avg_memory_used'] = np.mean(memory_used_list)
            results['max_memory_used'] = np.max(memory_used_list)
            results['total_memory_increase'] = results['peak_memory'] - results['initial_memory']
            
            logger.info(f"[Benchmark] Memory usage benchmark completed: "
                       f"peak_memory={results['peak_memory']:.1f}MB, "
                       f"avg_usage={results['avg_memory_used']:.1f}MB")
            
            self.results['memory_usage'] = results
            return results
            
        except Exception as e:
            logger.exception(f"[Benchmark] Error in memory usage benchmark: {e}")
            return {'error': str(e)}
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """
        Run a complete performance benchmark suite.
        
        Returns:
            Complete benchmark results
        """
        try:
            logger.info("[Benchmark] Starting full benchmark suite")
            
            # Generate test data
            test_videos = self._generate_test_videos()
            test_frames = self._generate_test_frames()
            
            # Run benchmarks
            smoke_results = self.benchmark_smoke_detection(test_videos)
            frame_results = self.benchmark_frame_processing(test_frames)
            memory_results = self.benchmark_memory_usage(test_videos)
            
            # Compile summary
            summary = {
                'timestamp': datetime.now().isoformat(),
                'smoke_detection': smoke_results,
                'frame_processing': frame_results,
                'memory_usage': memory_results,
                'overall_performance': {
                    'smoke_detection_fps': smoke_results.get('fps', 0),
                    'frame_processing_fps': frame_results.get('fps', 0),
                    'peak_memory_mb': memory_results.get('peak_memory', 0),
                    'avg_memory_usage_mb': memory_results.get('avg_memory_used', 0)
                }
            }
            
            logger.info(f"[Benchmark] Full benchmark completed: "
                       f"smoke_fps={summary['overall_performance']['smoke_detection_fps']:.2f}, "
                       f"frame_fps={summary['overall_performance']['frame_processing_fps']:.2f}, "
                       f"peak_memory={summary['overall_performance']['peak_memory_mb']:.1f}MB")
            
            self.results['full_benchmark'] = summary
            return summary
            
        except Exception as e:
            logger.exception(f"[Benchmark] Error in full benchmark: {e}")
            return {'error': str(e)}
    
    def _generate_test_videos(self) -> List[np.ndarray]:
        """Generate test video arrays."""
        videos = []
        for i in range(5):  # Generate 5 test videos
            # Create random video array (11 frames, 504x896)
            video = np.random.randint(0, 256, (11, 504, 896), dtype=np.uint8)
            videos.append(video)
        return videos
    
    def _generate_test_frames(self) -> List[np.ndarray]:
        """Generate test frame arrays."""
        frames = []
        for i in range(20):  # Generate 20 test frames
            # Create random frame (504x896)
            frame = np.random.randint(0, 256, (504, 896), dtype=np.uint8)
            frames.append(frame)
        return frames
    
    def _convert_to_grayscale(self, frame: np.ndarray) -> np.ndarray:
        """Convert BGR frame to grayscale."""
        import cv2
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame
    
    def _resize_frame(self, frame: np.ndarray) -> np.ndarray:
        """Resize frame to target size."""
        import cv2
        target_size = (self.settings.frame_width, self.settings.frame_height)
        return cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
    
    def _process_data(self, data: np.ndarray) -> np.ndarray:
        """Simulate data processing."""
        # Simulate some processing
        processed = data.copy()
        processed = processed.astype(np.float32)
        processed = processed / 255.0
        return processed
    
    def get_results(self) -> Dict[str, Any]:
        """Get all benchmark results."""
        return self.results
    
    def save_results(self, filename: str = None) -> bool:
        """
        Save benchmark results to file.
        
        Args:
            filename: Optional filename
            
        Returns:
            True if saved successfully
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"benchmark/results_{timestamp}.json"
            
            import json
            import os
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save results
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            logger.info(f"[Benchmark] Results saved to {filename}")
            return True
            
        except Exception as e:
            logger.exception(f"[Benchmark] Error saving results: {e}")
            return False 