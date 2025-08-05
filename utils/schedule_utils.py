# utils/schedule_utils.py
"""
Schedule utilities for smoke detection system.
"""

import logging
from datetime import datetime, time
from typing import Optional

logger = logging.getLogger(__name__)

class ScheduleUtils:
    """Utilities for handling detection schedules."""
    
    @staticmethod
    def is_within_schedule(start_time: str, end_time: str) -> bool:
        """
        Check if current time is within the detection schedule.
        
        Args:
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            
        Returns:
            True if current time is within schedule
        """
        try:
            # Parse time strings
            start = datetime.strptime(start_time, "%H:%M").time()
            end = datetime.strptime(end_time, "%H:%M").time()
            current = datetime.now().time()
            
            # Handle overnight schedules (e.g., 22:00 to 06:00)
            if start > end:
                # Overnight schedule
                return current >= start or current <= end
            else:
                # Same day schedule
                return start <= current <= end
                
        except Exception as e:
            logger.exception(f"[ScheduleUtils] Error checking schedule: {e}")
            return True  # Default to enabled if error
    
    @staticmethod
    def format_time_range(start_time: str, end_time: str) -> str:
        """
        Format time range for display.
        
        Args:
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            
        Returns:
            Formatted time range string
        """
        try:
            start = datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p")
            end = datetime.strptime(end_time, "%H:%M").strftime("%I:%M %p")
            return f"{start} - {end}"
        except Exception as e:
            logger.exception(f"[ScheduleUtils] Error formatting time range: {e}")
            return f"{start_time} - {end_time}"
    
    @staticmethod
    def get_next_schedule_change(start_time: str, end_time: str) -> Optional[datetime]:
        """
        Get the next time the schedule will change.
        
        Args:
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
            
        Returns:
            Next schedule change time or None if error
        """
        try:
            now = datetime.now()
            start = datetime.strptime(start_time, "%H:%M").time()
            end = datetime.strptime(end_time, "%H:%M").time()
            
            # Create datetime objects for today
            start_dt = datetime.combine(now.date(), start)
            end_dt = datetime.combine(now.date(), end)
            
            # Handle overnight schedules
            if start > end:
                if now.time() < start:
                    # Before start time today
                    return start_dt
                elif now.time() > end:
                    # After end time today, next start is tomorrow
                    return start_dt.replace(day=start_dt.day + 1)
                else:
                    # Currently active, next change is end time
                    return end_dt
            else:
                # Same day schedule
                if now.time() < start:
                    return start_dt
                elif now.time() < end:
                    return end_dt
                else:
                    # After end time, next start is tomorrow
                    return start_dt.replace(day=start_dt.day + 1)
                    
        except Exception as e:
            logger.exception(f"[ScheduleUtils] Error getting next schedule change: {e}")
            return None 