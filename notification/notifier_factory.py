# notification/notifier_factory.py
"""
Factory for creating notification providers.
"""

import logging
from typing import Dict, Any, Optional
from .base import BaseNotifier
from .firebase_notifier import FirebaseNotifier

logger = logging.getLogger(__name__)

class NotifierFactory:
    """Factory for creating notification providers."""
    
    @staticmethod
    def create_notifier(provider: str, config: Dict[str, Any]) -> Optional[BaseNotifier]:
        """
        Create a notification provider based on the specified type.
        
        Args:
            provider: Notification provider type (firebase, email, etc.)
            config: Configuration dictionary
            
        Returns:
            Notification provider instance or None if creation failed
        """
        try:
            if provider.lower() == "firebase":
                return FirebaseNotifier(config)
            elif provider.lower() == "email":
                # TODO: Implement email notifier
                logger.warning("[NotifierFactory] Email notifier not yet implemented")
                return None
            else:
                logger.error(f"[NotifierFactory] Unknown notification provider: {provider}")
                return None
                
        except Exception as e:
            logger.exception(f"[NotifierFactory] Error creating notifier {provider}: {e}")
            return None
    
    @staticmethod
    def create_from_settings(notification_settings) -> Optional[BaseNotifier]:
        """
        Create a notification provider from settings.
        
        Args:
            notification_settings: Notification settings object or dictionary
            
        Returns:
            Notification provider instance or None if creation failed
        """
        # Handle both dict and object types
        if hasattr(notification_settings, 'provider'):
            provider = notification_settings.provider
            config = {
                'provider': notification_settings.provider,
                'token': notification_settings.token,
                'user_key': notification_settings.user_key
            }
        else:
            provider = notification_settings.get('provider', 'firebase')
            config = notification_settings
            
        return NotifierFactory.create_notifier(provider, config) 