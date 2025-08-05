# watchdog/monitor.py
"""
System monitoring and health checks for the smoke detection system.
"""

import time
import psutil
import logging
import threading
from typing import Dict, Any, List, Callable
from datetime import datetime

from data_models.models import ProgramSettings

logger = logging.getLogger(__name__)

class SystemMonitor:
    """Monitors system health and performance."""
    
    def __init__(self, settings: ProgramSettings):
        self.settings = settings
        self.running = False
        self.monitor_thread = None
        self.health_callbacks: List[Callable] = []
        self.last_check = time.time()
        self.check_interval = settings.watchdog_check_interval_sec
        
        # Health thresholds
        self.cpu_threshold = 90.0  # CPU usage threshold
        self.memory_threshold = 85.0  # Memory usage threshold
        self.disk_threshold = 90.0  # Disk usage threshold
        self.temperature_threshold = 80.0  # Temperature threshold
        
    def start_monitoring(self):
        """Start the system monitoring thread."""
        if self.running:
            logger.warning("[SystemMonitor] Monitoring already running")
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            name="SystemMonitor",
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("[SystemMonitor] System monitoring started")
    
    def stop_monitoring(self):
        """Stop the system monitoring thread."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("[SystemMonitor] System monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self._perform_health_check()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.exception(f"[SystemMonitor] Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _perform_health_check(self):
        """Perform a comprehensive health check."""
        try:
            health_status = self.get_system_health()
            
            # Check for critical issues
            if health_status['overall_status'] == 'critical':
                logger.critical(f"[SystemMonitor] Critical system health issue detected: {health_status}")
                self._trigger_health_callbacks('critical', health_status)
            elif health_status['overall_status'] == 'warning':
                logger.warning(f"[SystemMonitor] System health warning: {health_status}")
                self._trigger_health_callbacks('warning', health_status)
            else:
                logger.debug(f"[SystemMonitor] System health OK: {health_status['overall_status']}")
                self._trigger_health_callbacks('ok', health_status)
            
            self.last_check = time.time()
            
        except Exception as e:
            logger.exception(f"[SystemMonitor] Error performing health check: {e}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get comprehensive system health status.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            # Collect system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            temperature = self._get_temperature()
            
            # Determine component status
            cpu_status = self._get_component_status(cpu_percent, self.cpu_threshold, 'CPU')
            memory_status = self._get_component_status(memory.percent, self.memory_threshold, 'Memory')
            disk_status = self._get_component_status(disk.percent, self.disk_threshold, 'Disk')
            temp_status = self._get_component_status(temperature, self.temperature_threshold, 'Temperature')
            
            # Determine overall status
            statuses = [cpu_status['status'], memory_status['status'], disk_status['status'], temp_status['status']]
            overall_status = self._determine_overall_status(statuses)
            
            health_data = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': overall_status,
                'components': {
                    'cpu': cpu_status,
                    'memory': memory_status,
                    'disk': disk_status,
                    'temperature': temp_status
                },
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'disk_free_gb': disk.free / (1024**3),
                    'temperature_celsius': temperature
                }
            }
            
            return health_data
            
        except Exception as e:
            logger.exception(f"[SystemMonitor] Error getting system health: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'unknown',
                'error': str(e)
            }
    
    def _get_component_status(self, value: float, threshold: float, component_name: str) -> Dict[str, Any]:
        """
        Get status for a specific component.
        
        Args:
            value: Current value
            threshold: Warning threshold
            component_name: Name of the component
            
        Returns:
            Component status dictionary
        """
        if value >= threshold:
            status = 'critical'
            message = f"{component_name} usage is critical: {value:.1f}%"
        elif value >= threshold * 0.8:
            status = 'warning'
            message = f"{component_name} usage is high: {value:.1f}%"
        else:
            status = 'ok'
            message = f"{component_name} usage is normal: {value:.1f}%"
        
        return {
            'status': status,
            'value': value,
            'threshold': threshold,
            'message': message
        }
    
    def _determine_overall_status(self, statuses: List[str]) -> str:
        """
        Determine overall system status from component statuses.
        
        Args:
            statuses: List of component statuses
            
        Returns:
            Overall status
        """
        if 'critical' in statuses:
            return 'critical'
        elif 'warning' in statuses:
            return 'warning'
        else:
            return 'ok'
    
    def _get_temperature(self) -> float:
        """
        Get system temperature.
        
        Returns:
            Temperature in Celsius
        """
        try:
            # This would typically read from system sensors
            # For now, return a placeholder value
            return 45.0
        except Exception as e:
            logger.debug(f"[SystemMonitor] Could not get temperature: {e}")
            return 0.0
    
    def add_health_callback(self, callback: Callable):
        """
        Add a callback function to be called when health status changes.
        
        Args:
            callback: Function to call with (status, health_data) parameters
        """
        self.health_callbacks.append(callback)
        logger.debug(f"[SystemMonitor] Added health callback: {callback}")
    
    def _trigger_health_callbacks(self, status: str, health_data: Dict[str, Any]):
        """
        Trigger all registered health callbacks.
        
        Args:
            status: Health status
            health_data: Health data dictionary
        """
        for callback in self.health_callbacks:
            try:
                callback(status, health_data)
            except Exception as e:
                logger.exception(f"[SystemMonitor] Error in health callback: {e}")
    
    def set_thresholds(self, cpu: float = None, memory: float = None, 
                      disk: float = None, temperature: float = None):
        """
        Set health monitoring thresholds.
        
        Args:
            cpu: CPU usage threshold
            memory: Memory usage threshold
            disk: Disk usage threshold
            temperature: Temperature threshold
        """
        if cpu is not None:
            self.cpu_threshold = cpu
        if memory is not None:
            self.memory_threshold = memory
        if disk is not None:
            self.disk_threshold = disk
        if temperature is not None:
            self.temperature_threshold = temperature
            
        logger.info(f"[SystemMonitor] Updated thresholds: CPU={self.cpu_threshold}%, "
                   f"Memory={self.memory_threshold}%, Disk={self.disk_threshold}%, "
                   f"Temperature={self.temperature_threshold}°C")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get monitor status.
        
        Returns:
            Status information
        """
        return {
            'running': self.running,
            'check_interval': self.check_interval,
            'last_check': self.last_check,
            'time_since_last_check': time.time() - self.last_check,
            'thresholds': {
                'cpu': self.cpu_threshold,
                'memory': self.memory_threshold,
                'disk': self.disk_threshold,
                'temperature': self.temperature_threshold
            },
            'callbacks_registered': len(self.health_callbacks)
        } 