# rtsp_stream/stream_manager.py
"""
Multi-camera stream manager for RTSP connections.
Handles camera discovery, connection management, and frame distribution.
"""

import threading
import time
import logging
from typing import Dict, Optional, List
import numpy as np

from data_models.models import CameraConfig, ProgramSettings
from .rtsp_worker import RTSPWorker

logger = logging.getLogger(__name__)

class StreamManager:
    """Manages multiple RTSP camera streams."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings
        self.workers: Dict[str, RTSPWorker] = {}
        self.worker_threads: Dict[str, threading.Thread] = {}
        self.running = False
        self.lock = threading.Lock()
        
    def start_all_streams(self, cameras: List[CameraConfig]) -> None:
        """
        Start RTSP streams for all enabled cameras.
        
        Args:
            cameras: List of camera configurations
        """
        logger.info(f"[StreamManager] Starting streams for {len(cameras)} cameras")
        
        for camera in cameras:
            if camera.enabled:
                self.start_stream(camera)
                
        self.running = True
        logger.info(f"[StreamManager] All streams started successfully")
    
    def start_stream(self, camera: CameraConfig) -> bool:
        """
        Start a single camera stream.
        
        Args:
            camera: Camera configuration
            
        Returns:
            True if stream started successfully
        """
        try:
            with self.lock:
                if camera.id in self.workers:
                    logger.warning(f"[StreamManager] Stream for camera {camera.id} already exists")
                    return False
                
                # Create RTSP worker
                worker = RTSPWorker(camera, self.settings)
                self.workers[camera.id] = worker
                
                # Start worker thread
                thread = threading.Thread(
                    target=worker.run,
                    name=f"RTSP-{camera.id}",
                    daemon=True
                )
                self.worker_threads[camera.id] = thread
                thread.start()
                
                logger.info(f"[StreamManager] Started stream for camera {camera.id}")
                return True
                
        except Exception as e:
            logger.exception(f"[StreamManager] Failed to start stream for camera {camera.id}: {e}")
            return False
    
    def stop_stream(self, camera_id: str) -> bool:
        """
        Stop a single camera stream.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            True if stream stopped successfully
        """
        try:
            with self.lock:
                if camera_id not in self.workers:
                    logger.warning(f"[StreamManager] Stream for camera {camera_id} not found")
                    return False
                
                # Stop worker
                worker = self.workers[camera_id]
                worker.stop()
                
                # Wait for thread to finish
                if camera_id in self.worker_threads:
                    thread = self.worker_threads[camera_id]
                    thread.join(timeout=5.0)
                    
                # Clean up
                del self.workers[camera_id]
                if camera_id in self.worker_threads:
                    del self.worker_threads[camera_id]
                
                logger.info(f"[StreamManager] Stopped stream for camera {camera_id}")
                return True
                
        except Exception as e:
            logger.exception(f"[StreamManager] Failed to stop stream for camera {camera_id}: {e}")
            return False
    
    def stop_all_streams(self) -> None:
        """Stop all camera streams."""
        logger.info("[StreamManager] Stopping all streams")
        
        with self.lock:
            camera_ids = list(self.workers.keys())
            
        for camera_id in camera_ids:
            self.stop_stream(camera_id)
            
        self.running = False
        logger.info("[StreamManager] All streams stopped")
    
    def get_frame(self, camera_id: str) -> Optional[np.ndarray]:
        """
        Get the latest frame from a camera.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Latest frame or None if not available
        """
        try:
            with self.lock:
                if camera_id not in self.workers:
                    return None
                    
                worker = self.workers[camera_id]
                return worker.get_frame()
                
        except Exception as e:
            logger.exception(f"[StreamManager] Error getting frame from camera {camera_id}: {e}")
            return None
    
    def get_all_frames(self) -> Dict[str, np.ndarray]:
        """
        Get latest frames from all cameras.
        
        Returns:
            Dictionary mapping camera_id to frame
        """
        frames = {}
        
        with self.lock:
            for camera_id in self.workers:
                frame = self.workers[camera_id].get_frame()
                if frame is not None:
                    frames[camera_id] = frame
                    
        return frames
    
    def is_stream_active(self, camera_id: str) -> bool:
        """
        Check if a camera stream is active.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            True if stream is active
        """
        with self.lock:
            if camera_id not in self.workers:
                return False
            return self.workers[camera_id].is_running()
    
    def get_active_cameras(self) -> List[str]:
        """
        Get list of active camera IDs.
        
        Returns:
            List of active camera identifiers
        """
        with self.lock:
            return [cam_id for cam_id, worker in self.workers.items() if worker.is_running()] 