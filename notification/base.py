# notification/base.py
"""
Base notification interface for the smoke detection system.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseNotifier(ABC):
    """Base class for all notification providers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.retry_count = 0
        self.max_retries = config.get('notification_retry_limit', 3)
        
    @abstractmethod
    def send_notification(self, message: str, title: str = "Smoke Detection Alert") -> bool:
        """
        Send a notification.
        
        Args:
            message: Notification message
            title: Notification title
            
        Returns:
            True if notification sent successfully
        """
        pass
    
    @abstractmethod
    def send_status_update(self, status: str) -> bool:
        """
        Send a status update.
        
        Args:
            status: Status message
            
        Returns:
            True if status sent successfully
        """
        pass
    
    def _handle_retry(self, operation_name: str) -> bool:
        """
        Handle retry logic for failed operations.
        
        Args:
            operation_name: Name of the operation for logging
            
        Returns:
            True if retry should be attempted
        """
        self.retry_count += 1
        
        if self.retry_count <= self.max_retries:
            logger.warning(f"[{self.__class__.__name__}] {operation_name} failed, retry {self.retry_count}/{self.max_retries}")
            return True
        else:
            logger.error(f"[{self.__class__.__name__}] {operation_name} failed after {self.max_retries} retries")
            self.retry_count = 0  # Reset for next operation
            return False
    
    def reset_retry_count(self) -> None:
        """Reset the retry counter."""
        self.retry_count = 0 