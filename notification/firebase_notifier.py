# notification/firebase_notifier.py
"""
Firebase Cloud Messaging notification provider.
"""

import requests
import json
import logging
from typing import Dict, Any
from .base import BaseNotifier

logger = logging.getLogger(__name__)

class FirebaseNotifier(BaseNotifier):
    """Firebase Cloud Messaging notification provider."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.server_token = config.get('token', '')
        self.user_key = config.get('user_key', '')
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        
        if not self.server_token or not self.user_key:
            logger.warning("[FirebaseNotifier] Missing Firebase configuration (token or user_key)")
    
    def send_notification(self, message: str, title: str = "Smoke Detection Alert") -> bool:
        """
        Send a Firebase notification.
        
        Args:
            message: Notification message
            title: Notification title
            
        Returns:
            True if notification sent successfully
        """
        if not self.server_token or not self.user_key:
            logger.error("[FirebaseNotifier] Cannot send notification - missing configuration")
            return False
            
        payload = {
            "to": self.user_key,
            "notification": {
                "title": title,
                "body": message,
                "sound": "default"
            },
            "data": {
                "message": message,
                "title": title
            }
        }
        
        headers = {
            "Authorization": f"key={self.server_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.fcm_url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') == 1:
                    logger.info(f"[FirebaseNotifier] Notification sent successfully: {title}")
                    self.reset_retry_count()
                    return True
                else:
                    logger.error(f"[FirebaseNotifier] Firebase API error: {result}")
                    return self._handle_retry("send_notification")
            else:
                logger.error(f"[FirebaseNotifier] HTTP error {response.status_code}: {response.text}")
                return self._handle_retry("send_notification")
                
        except Exception as e:
            logger.exception(f"[FirebaseNotifier] Error sending notification: {e}")
            return self._handle_retry("send_notification")
    
    def send_status_update(self, status: str) -> bool:
        """
        Send a status update via Firebase.
        
        Args:
            status: Status message
            
        Returns:
            True if status sent successfully
        """
        return self.send_notification(status, "System Status Update") 