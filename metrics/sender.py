# metrics/sender.py
"""
Metrics reporting and sending functionality.
"""

import time
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import requests

from data_models.models import ProgramSettings

logger = logging.getLogger(__name__)

class MetricsSender:
    """Handles sending metrics to external systems."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings
        self.last_send_time = time.time()
        self.send_interval = 300  # 5 minutes
        self.endpoint_url = None  # Configure as needed
        
    def send_metrics(self, metrics: Dict[str, Any], endpoint: Optional[str] = None) -> bool:
        """
        Send metrics to external endpoint.
        
        Args:
            metrics: Metrics data to send
            endpoint: Optional custom endpoint URL
            
        Returns:
            True if sent successfully
        """
        try:
            if not endpoint and not self.endpoint_url:
                logger.debug("[MetricsSender] No endpoint configured, skipping send")
                return True
            
            target_endpoint = endpoint or self.endpoint_url
            
            # Prepare payload
            payload = {
                'timestamp': datetime.now().isoformat(),
                'system_id': 'smoke_detection_system',
                'version': 'SDB_p1',
                'metrics': metrics
            }
            
            # Send HTTP POST request
            response = requests.post(
                target_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"[MetricsSender] Metrics sent successfully to {target_endpoint}")
                self.last_send_time = time.time()
                return True
            else:
                logger.warning(f"[MetricsSender] Failed to send metrics: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.exception(f"[MetricsSender] Error sending metrics: {e}")
            return False
    
    def save_metrics_to_file(self, metrics: Dict[str, Any], filename: Optional[str] = None) -> bool:
        """
        Save metrics to local file.
        
        Args:
            metrics: Metrics data to save
            filename: Optional custom filename
            
        Returns:
            True if saved successfully
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"metrics/metrics_{timestamp}.json"
            
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Prepare data
            data = {
                'timestamp': datetime.now().isoformat(),
                'system_id': 'smoke_detection_system',
                'version': 'SDB_p1',
                'metrics': metrics
            }
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"[MetricsSender] Metrics saved to {filename}")
            return True
            
        except Exception as e:
            logger.exception(f"[MetricsSender] Error saving metrics to file: {e}")
            return False
    
    def should_send_metrics(self) -> bool:
        """
        Check if it's time to send metrics.
        
        Returns:
            True if metrics should be sent
        """
        return (time.time() - self.last_send_time) >= self.send_interval
    
    def set_endpoint(self, endpoint_url: str):
        """
        Set the metrics endpoint URL.
        
        Args:
            endpoint_url: Endpoint URL for sending metrics
        """
        self.endpoint_url = endpoint_url
        logger.info(f"[MetricsSender] Set metrics endpoint: {endpoint_url}")
    
    def set_send_interval(self, interval_seconds: int):
        """
        Set the metrics send interval.
        
        Args:
            interval_seconds: Send interval in seconds
        """
        self.send_interval = interval_seconds
        logger.info(f"[MetricsSender] Set send interval: {interval_seconds} seconds")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get metrics sender status.
        
        Returns:
            Status information
        """
        return {
            'endpoint_configured': bool(self.endpoint_url),
            'endpoint_url': self.endpoint_url,
            'send_interval': self.send_interval,
            'last_send_time': self.last_send_time,
            'time_since_last_send': time.time() - self.last_send_time,
            'next_send_in': max(0, self.send_interval - (time.time() - self.last_send_time))
        } 