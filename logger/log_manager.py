# logger/log_manager.py
"""
Structured logging manager for the smoke detection system.
"""

import os
import logging
from typing import Optional, Dict
from datetime import datetime

class SmartFormatter(logging.Formatter):
    """Smart formatter that categorizes and colors different types of logs."""
    
    def __init__(self, use_colors=True):
        super().__init__()
        self.use_colors = use_colors
        
        if use_colors:
            self.colors = {
                # Camera colors
                'camera_1': '\033[31m',  # Red
                'camera_2': '\033[32m',  # Green  
                'camera_3': '\033[33m',  # Yellow
                'camera_4': '\033[34m',  # Blue
                
                # Module colors
                'system': '\033[36m',    # Cyan
                'smoke': '\033[35m',     # Magenta
                'processing': '\033[37m', # White
                'preprocessing': '\033[37m', # White
                
                # Level colors
                'ERROR': '\033[91m',     # Bright Red
                'WARNING': '\033[93m',   # Bright Yellow
                'INFO': '\033[94m',      # Bright Blue
                'DEBUG': '\033[90m',     # Gray
                
                'reset': '\033[0m'
            }
        else:
            # No colors - use prefixes instead
            self.colors = {
                'camera_1': '[CAM1]',
                'camera_2': '[CAM2]',
                'camera_3': '[CAM3]',
                'camera_4': '[CAM4]',
                'system': '[SYS]',
                'smoke': '[SMK]',
                'processing': '[PRC]',
                'preprocessing': '[PRC]',
                'ERROR': '[ERR]',
                'WARNING': '[WARN]',
                'INFO': '[INFO]',
                'DEBUG': '[DBG]',
                'reset': ''
            }
    
    def format(self, record):
        # Extract camera ID from message if present
        camera_id = None
        if hasattr(record, 'camera_id'):
            camera_id = record.camera_id
        elif '[CAM:' in record.getMessage():
            import re
            match = re.search(r'\[CAM:(\d+)\]', record.getMessage())
            if match:
                camera_id = match.group(1)
        
        # Format the message
        formatted = super().format(record)
        
        # Add color coding for camera ID
        if camera_id and f'camera_{camera_id}' in self.colors:
            color = self.colors[f'camera_{camera_id}']
            reset = self.colors['reset']
            if self.use_colors:
                formatted = formatted.replace(f'[CAM:{camera_id}]', f'{color}[CAM:{camera_id}]{reset}')
            else:
                formatted = formatted.replace(f'[CAM:{camera_id}]', f'{color}[CAM:{camera_id}]')
        
        # Add color coding for log levels
        for level, color in self.colors.items():
            if level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
                if self.use_colors:
                    formatted = formatted.replace(f'[{level}]', f'{color}[{level}]{self.colors["reset"]}')
                else:
                    formatted = formatted.replace(f'[{level}]', f'{color}[{level}]')
        
        # Add color coding for modules
        module_name = record.name.split('.')[0] if '.' in record.name else record.name
        if module_name in ['smoke', 'processing', 'preprocessing']:
            color = self.colors.get(module_name, self.colors['system'])
            if self.use_colors:
                formatted = formatted.replace(f'{record.name}:', f'{color}{record.name}:{self.colors["reset"]}')
            else:
                formatted = formatted.replace(f'{record.name}:', f'{color}{record.name}:')
        
        return formatted

class LogManager:
    """Centralized logging manager for the smoke detection system."""
    
    _camera_loggers: Dict[str, logging.Logger] = {}
    
    @staticmethod
    def initialize_logger(log_to_file: bool = True, log_level: str = "DEBUG", use_colors: bool = False) -> logging.Logger:
        """
        Initialize the logging system.
        
        Args:
            log_to_file: Whether to log to file
            log_level: Logging level
            
        Returns:
            Configured logger instance
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))

        # Clear duplicate handlers
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # Use smart formatter for better categorization
        formatter = SmartFormatter(use_colors=use_colors)
        formatter._fmt = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

        # Console handler with color coding
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # File handler (optional) - no colors in file
        if log_to_file:
            os.makedirs("logs", exist_ok=True)
            file_handler = logging.FileHandler("logs/system.log")
            file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

        # Ensure dashboard logs also show up
        for name in [
            "dashboard", "dashboard.routes", "dashboard.routes.home",
            "dashboard.routes.metrics", "dashboard.routes.cameras"
        ]:
            logging.getLogger(name).setLevel(logging.DEBUG)

        return logging.getLogger("Main")
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Logger instance
        """
        return logging.getLogger(name)
    
    @staticmethod
    def get_camera_logger(camera_id: str) -> logging.Logger:
        """
        Get a camera-specific logger that automatically prefixes messages with camera ID.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Camera-specific logger instance
        """
        if camera_id not in LogManager._camera_loggers:
            logger = logging.getLogger(f"camera.{camera_id}")
            LogManager._camera_loggers[camera_id] = logger
        return LogManager._camera_loggers[camera_id]
    
    @staticmethod
    def log_camera_event(camera_id: str, level: str, message: str, **kwargs):
        """
        Log a camera-specific event with automatic camera ID prefixing.
        
        Args:
            camera_id: Camera identifier
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            message: Log message
            **kwargs: Additional context
        """
        logger = LogManager.get_camera_logger(camera_id)
        
        # Add camera_id to record for formatter
        record = logger.makeRecord(
            logger.name, getattr(logging, level.upper()), 
            "", 0, f"[CAM:{camera_id}] {message}", (), None
        )
        record.camera_id = camera_id
        
        # Add additional context
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        logger.handle(record)
    
    @staticmethod
    def create_camera_summary():
        """
        Create a summary of recent camera activity.
        """
        try:
            with open("logs/system.log", "r") as f:
                lines = f.readlines()
            
            camera_stats = {}
            for line in lines[-1000:]:  # Last 1000 lines
                if '[CAM:' in line:
                    import re
                    match = re.search(r'\[CAM:(\d+)\]', line)
                    if match:
                        cam_id = match.group(1)
                        if cam_id not in camera_stats:
                            camera_stats[cam_id] = {'count': 0, 'last_seen': None}
                        camera_stats[cam_id]['count'] += 1
                        camera_stats[cam_id]['last_seen'] = line.split()[0] + ' ' + line.split()[1]
            
            print("\n=== Camera Activity Summary ===")
            for cam_id, stats in sorted(camera_stats.items()):
                print(f"Camera {cam_id}: {stats['count']} logs, last seen: {stats['last_seen']}")
            print("===============================\n")
            
        except Exception as e:
            print(f"Error creating camera summary: {e}")
    
    @staticmethod
    def create_log_summary():
        """
        Create a comprehensive summary of all log types.
        """
        try:
            with open("logs/system.log", "r") as f:
                lines = f.readlines()
            
            # Analyze last 1000 lines
            recent_lines = lines[-1000:]
            
            # Count by module
            module_stats = {}
            level_stats = {}
            camera_stats = {}
            
            for line in recent_lines:
                parts = line.split()
                if len(parts) >= 4:
                    # Level stats
                    level = parts[2].strip('[]')
                    level_stats[level] = level_stats.get(level, 0) + 1
                    
                    # Module stats
                    module = parts[3].rstrip(':')
                    module_stats[module] = module_stats.get(module, 0) + 1
                    
                    # Camera stats
                    if '[CAM:' in line:
                        import re
                        match = re.search(r'\[CAM:(\d+)\]', line)
                        if match:
                            cam_id = match.group(1)
                            camera_stats[cam_id] = camera_stats.get(cam_id, 0) + 1
            
            print("\n=== Log Summary (Last 1000 lines) ===")
            print(f"Total logs: {len(recent_lines)}")
            
            print("\n--- By Level ---")
            for level, count in sorted(level_stats.items()):
                print(f"{level}: {count}")
            
            print("\n--- By Module ---")
            for module, count in sorted(module_stats.items()):
                print(f"{module}: {count}")
            
            print("\n--- By Camera ---")
            for cam_id, count in sorted(camera_stats.items()):
                print(f"Camera {cam_id}: {count}")
            
            print("=====================================\n")
            
        except Exception as e:
            print(f"Error creating log summary: {e}")
    
    @staticmethod
    def filter_logs_by_type(log_type: str, lines: int = 50):
        """
        Filter and display logs by type.
        
        Args:
            log_type: Type to filter ('camera', 'smoke', 'processing', 'system', 'all')
            lines: Number of lines to show
        """
        try:
            with open("logs/system.log", "r") as f:
                all_lines = f.readlines()
            
            recent_lines = all_lines[-lines*10:]  # Get more lines to filter from
            
            if log_type == 'camera':
                filtered = [line for line in recent_lines if '[CAM:' in line]
            elif log_type == 'smoke':
                filtered = [line for line in recent_lines if 'smoke.' in line]
            elif log_type == 'processing':
                filtered = [line for line in recent_lines if 'processing.' in line or 'preprocessing.' in line]
            elif log_type == 'system':
                filtered = [line for line in recent_lines if 'Main:' in line or 'dashboard.' in line]
            elif log_type == 'error':
                filtered = [line for line in recent_lines if '[ERROR]' in line]
            elif log_type == 'warning':
                filtered = [line for line in recent_lines if '[WARNING]' in line]
            else:
                filtered = recent_lines
            
            print(f"\n=== {log_type.upper()} Logs (Last {len(filtered)} lines) ===")
            for line in filtered[-lines:]:
                print(line.rstrip())
            print("=" * 50 + "\n")
            
        except Exception as e:
            print(f"Error filtering logs: {e}") 