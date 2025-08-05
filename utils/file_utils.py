# utils/file_utils.py
"""
File utility functions for the smoke detection system.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def load_json_config(filepath: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to JSON configuration file
            
        Returns:
            Configuration dictionary or None if error
        """
        try:
            if not os.path.exists(filepath):
                logger.warning(f"[FileUtils] Configuration file not found: {filepath}")
                return None
                
            with open(filepath, 'r') as f:
                config = json.load(f)
                
            logger.info(f"[FileUtils] Loaded configuration from: {filepath}")
            return config
            
        except Exception as e:
            logger.exception(f"[FileUtils] Error loading configuration from {filepath}: {e}")
            return None
    
    @staticmethod
    def save_json_config(config: Dict[str, Any], filepath: str) -> bool:
        """
        Save configuration to JSON file.
        
        Args:
            config: Configuration dictionary
            filepath: Path to save configuration
            
        Returns:
            True if saved successfully
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"[FileUtils] Saved configuration to: {filepath}")
            return True
            
        except Exception as e:
            logger.exception(f"[FileUtils] Error saving configuration to {filepath}: {e}")
            return False
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """
        Ensure a directory exists, create if it doesn't.
        
        Args:
            directory: Directory path
            
        Returns:
            True if directory exists or was created
        """
        try:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"[FileUtils] Ensured directory exists: {directory}")
            return True
        except Exception as e:
            logger.exception(f"[FileUtils] Error creating directory {directory}: {e}")
            return False
    
    @staticmethod
    def get_file_size(filepath: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            filepath: Path to file
            
        Returns:
            File size in bytes or None if error
        """
        try:
            if os.path.exists(filepath):
                return os.path.getsize(filepath)
            return None
        except Exception as e:
            logger.exception(f"[FileUtils] Error getting file size for {filepath}: {e}")
            return None
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def list_files(directory: str, extension: Optional[str] = None) -> list:
        """
        List files in a directory.
        
        Args:
            directory: Directory path
            extension: Optional file extension filter
            
        Returns:
            List of file paths
        """
        try:
            if not os.path.exists(directory):
                return []
                
            files = []
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    if extension is None or filename.endswith(extension):
                        files.append(filepath)
                        
            return sorted(files)
            
        except Exception as e:
            logger.exception(f"[FileUtils] Error listing files in {directory}: {e}")
            return [] 