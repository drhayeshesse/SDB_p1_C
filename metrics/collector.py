# metrics/collector.py
"""
Performance metrics collection for the smoke detection system.
"""

import time
import psutil
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque

from data_models.models import ProgramSettings

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects and manages system performance metrics."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings
        self.metrics_queue = deque(maxlen=settings.metrics_queue_len)
        self.start_time = time.time()
        self.detection_count = 0
        self.false_positive_count = 0
        self.last_collection = time.time()
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """
        Collect system performance metrics.
        
        Returns:
            Dictionary of system metrics
        """
        try:
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network statistics
            network = psutil.net_io_counters()
            
            # System uptime
            uptime = time.time() - self.start_time
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available / (1024**3),  # GB
                'disk_usage': disk.percent,
                'disk_free': disk.free / (1024**3),  # GB
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'uptime': uptime,
                'temperature': self._get_temperature(),
                'power_consumption': self._estimate_power_consumption(cpu_percent)
            }
            
            return metrics
            
        except Exception as e:
            logger.exception(f"[MetricsCollector] Error collecting system metrics: {e}")
            return {}
    
    def collect_detection_metrics(self) -> Dict[str, Any]:
        """
        Collect smoke detection performance metrics.
        
        Returns:
            Dictionary of detection metrics
        """
        try:
            current_time = time.time()
            time_since_start = current_time - self.start_time
            
            # Calculate rates
            detection_rate = self.detection_count / (time_since_start / 3600) if time_since_start > 0 else 0
            false_positive_rate = self.false_positive_count / (time_since_start / 3600) if time_since_start > 0 else 0
            
            # Calculate accuracy
            total_detections = self.detection_count + self.false_positive_count
            accuracy = ((self.detection_count - self.false_positive_count) / total_detections * 100) if total_detections > 0 else 0
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'total_detections': self.detection_count,
                'false_positives': self.false_positive_count,
                'detection_rate': detection_rate,  # per hour
                'false_positive_rate': false_positive_rate,  # per hour
                'accuracy': accuracy,
                'uptime': time_since_start
            }
            
            return metrics
            
        except Exception as e:
            logger.exception(f"[MetricsCollector] Error collecting detection metrics: {e}")
            return {}
    
    def collect_camera_metrics(self, active_cameras: List[str]) -> Dict[str, Any]:
        """
        Collect camera-specific metrics.
        
        Args:
            active_cameras: List of active camera IDs
            
        Returns:
            Dictionary of camera metrics
        """
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'active_cameras': len(active_cameras),
                'total_cameras': len(self.settings.cameras),
                'camera_status': {}
            }
            
            # Add individual camera metrics (placeholder)
            for camera in self.settings.cameras:
                metrics['camera_status'][camera.id] = {
                    'enabled': camera.enabled,
                    'active': camera.id in active_cameras,
                    'fps': 3.0,  # Placeholder
                    'latency': 0.2,  # Placeholder
                    'connection_quality': 95.0  # Placeholder
                }
            
            return metrics
            
        except Exception as e:
            logger.exception(f"[MetricsCollector] Error collecting camera metrics: {e}")
            return {}
    
    def record_detection(self, confidence: float, is_false_positive: bool = False):
        """
        Record a smoke detection event.
        
        Args:
            confidence: Detection confidence score
            is_false_positive: Whether this was a false positive
        """
        try:
            if is_false_positive:
                self.false_positive_count += 1
            else:
                self.detection_count += 1
                
            # Add to metrics queue
            detection_metric = {
                'timestamp': datetime.now().isoformat(),
                'type': 'detection',
                'confidence': confidence,
                'false_positive': is_false_positive
            }
            
            self.metrics_queue.append(detection_metric)
            logger.debug(f"[MetricsCollector] Recorded detection: confidence={confidence}, false_positive={is_false_positive}")
            
        except Exception as e:
            logger.exception(f"[MetricsCollector] Error recording detection: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all collected metrics.
        
        Returns:
            Dictionary containing all metrics
        """
        try:
            summary = {
                'system': self.collect_system_metrics(),
                'detection': self.collect_detection_metrics(),
                'cameras': self.collect_camera_metrics([]),  # Empty list for now
                'queue_size': len(self.metrics_queue),
                'collection_interval': time.time() - self.last_collection
            }
            
            self.last_collection = time.time()
            return summary
            
        except Exception as e:
            logger.exception(f"[MetricsCollector] Error getting metrics summary: {e}")
            return {}
    
    def _get_temperature(self) -> float:
        """
        Get system temperature (placeholder implementation).
        
        Returns:
            Temperature in Celsius
        """
        try:
            # This would typically read from system sensors
            # For now, return a placeholder value
            return 45.0
        except Exception as e:
            logger.debug(f"[MetricsCollector] Could not get temperature: {e}")
            return 0.0
    
    def _estimate_power_consumption(self, cpu_percent: float) -> float:
        """
        Estimate power consumption based on CPU usage.
        
        Args:
            cpu_percent: CPU usage percentage
            
        Returns:
            Estimated power consumption in Watts
        """
        try:
            # Simple estimation: base power + CPU-dependent power
            base_power = 30.0  # Base system power
            cpu_power = (cpu_percent / 100.0) * 70.0  # CPU-dependent power
            return base_power + cpu_power
        except Exception as e:
            logger.debug(f"[MetricsCollector] Could not estimate power consumption: {e}")
            return 0.0 