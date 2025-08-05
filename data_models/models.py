# types/models.py
"""
Data models and type definitions for the smoke detection system.
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class NotificationSettings:
    """Notification configuration settings."""
    provider: str = ""
    token: str = ""
    user_key: str = ""

@dataclass
class CameraConfig:
    """Camera configuration settings."""
    id: str
    name: str
    ip: str
    port: int = 554
    username: str = "admin"
    password: str = ""
    stream_path: str = "/cam/realmonitor?channel=1&subtype=1"
    enabled: bool = True
    codec: str = "h264"
    frame_width: int = 896
    frame_height: int = 504
    latency_ms: int = 0
    target_fps: float = 3.0

@dataclass
class ProgramSettings:
    """Main program configuration settings."""
    log_level: str = "DEBUG"
    log_to_file: bool = True
    notification: NotificationSettings = field(default_factory=NotificationSettings)
    cameras: List[CameraConfig] = field(default_factory=list)
    sleep_time: float = 1.0
    frame_width: int = 896
    frame_height: int = 504
    surveillance_counter_threshold: int = 5
    email_counter_threshold: int = int(3600 / 3)
    sensitivity: int = 5
    sensitivity_val: int = 2
    motion_count_threshold: int = 850
    motion_threshold: int = 60
    n_patches_validate: int = 6
    n_frames_validation: int = 11
    sliding_window: int = 16
    verbose: int = 2
    with_sound: bool = False
    text_email: bool = True
    notification_retry_limit: int = 3
    metrics_queue_len: int = 60
    reconnect_delay_sec: int = 1
    watchdog_check_interval_sec: int = 10

    # Scheduler and detection toggle
    detection_enabled: bool = True
    detection_schedule_enabled: bool = False
    detection_start: str = "22:00"
    detection_end: str = "06:00"
    
    # Original parameters
    smokemode: int = 0

    # Legacy aliases for backward compatibility
    @property
    def SW(self): return self.sliding_window
    @property
    def SENSITIVITY_VAL(self): return self.sensitivity_val
    @property
    def MOTION_THRESHOLD(self): return self.motion_threshold
    @property
    def MOTION_COUNT_THRESHOLD(self): return self.motion_count_threshold
    @property
    def N_PATCHES_VALIDATE(self): return self.n_patches_validate
    @property
    def N_FRAMES_VALIDATION(self): return self.n_frames_validation
    @property
    def VERBOSE(self): return self.verbose

    @classmethod
    def from_dict(cls, data: dict) -> "ProgramSettings":
        """Create ProgramSettings from dictionary."""
        return cls(
            log_level=data.get("log_level", "DEBUG"),
            log_to_file=data.get("log_to_file", True),
            notification=NotificationSettings(**data.get("notification", {})),
            cameras=[CameraConfig(**cam) for cam in data.get("cameras", [])],
            sleep_time=data.get("sleep_time", 1.0),
            surveillance_counter_threshold=data.get("surveillance_counter_threshold", 5),
            email_counter_threshold=data.get("email_counter_threshold", int(3600 / 3)),
            sensitivity=data.get("sensitivity", 5),
            sensitivity_val=data.get("sensitivity_val", 2),
            motion_count_threshold=data.get("motion_count_threshold", 850),
            motion_threshold=data.get("motion_threshold", 60),
            n_patches_validate=data.get("n_patches_validate", 6),
            n_frames_validation=data.get("n_frames_validation", 11),
            sliding_window=data.get("sliding_window", 16),
            verbose=data.get("verbose", 2),
            with_sound=data.get("with_sound", False),
            text_email=data.get("text_email", True),
            notification_retry_limit=data.get("notification_retry_limit", 3),
            metrics_queue_len=data.get("metrics_queue_len", 60),
            reconnect_delay_sec=data.get("reconnect_delay_sec", 1),
            watchdog_check_interval_sec=data.get("watchdog_check_interval_sec", 10),
            detection_enabled=data.get("detection_enabled", True),
            detection_schedule_enabled=data.get("detection_schedule_enabled", False),
            detection_start=data.get("detection_start", "22:00"),
            detection_end=data.get("detection_end", "06:00"),
            smokemode=data.get("smokemode", 0),
        ) 