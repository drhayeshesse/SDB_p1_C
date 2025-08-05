# main_utils.py
import logging
import time
from datetime import datetime
from collections import deque
import cv2
import os
import numpy as np

from preprocessing.frame_normalizer import FrameNormalizer
from notification.notifier_factory import NotifierFactory
from utils.settings import load_settings
from smoke.smoke_detector import SmokeDetector

# Optional event recording modules (if implemented)
event_recorder = None
snapshot_manager = None

def initialize_event_recorder(settings):
    global event_recorder, snapshot_manager
    try:
        from event_recorder.clip_writer import ClipWriter
        from event_recorder.snapshot_manager import SnapshotManager
        event_recorder = ClipWriter(settings)
        snapshot_manager = SnapshotManager(settings)
    except ImportError:
        event_recorder = None
        snapshot_manager = None


def initialize_logger(log_to_file=True):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_to_file:
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/system.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Set log level for dashboard routes too
    for name in [
        "dashboard", "dashboard.routes", "dashboard.routes.home",
        "dashboard.routes.metrics", "dashboard.routes.cameras"
    ]:
        logging.getLogger(name).setLevel(logging.DEBUG)

    return logging.getLogger("Main")


def initialize_notifier(settings):
    return NotifierFactory.create_from_settings(settings.notification)


def is_within_schedule(start="22:00", end="06:00", override=None):
    if override is not None:
        return override

    now = datetime.now().time()
    start_time = datetime.strptime(start, "%H:%M").time()
    end_time = datetime.strptime(end, "%H:%M").time()

    if start_time < end_time:
        return start_time <= now <= end_time
    return now >= start_time or now <= end_time


def save_snapshot(cam_id, frame):
    os.makedirs(f"static/snapshots/{cam_id}", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"static/snapshots/{cam_id}/smoke_{timestamp}.jpg"
    cv2.imwrite(path, frame)


def grab_video_sequence(stream_manager, camera_id, settings, video_array):
    logger = logging.getLogger("Main")
    logger.debug(f"[{camera_id}] Capturing video sequence for validation...")

    for ki in range(settings.n_frames_validation):
        frame = stream_manager.get_frame(camera_id)

        if frame is not None:
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32)
            else:
                gray = frame.astype(np.float32)

            gray_resized = cv2.resize(
                gray,
                (settings.frame_width, settings.frame_height),
                interpolation=cv2.INTER_AREA
            )
            video_array[ki, :, :] = gray_resized

        time.sleep(settings.sleep_time)

    logger.debug(f"[{camera_id}] Video sequence captured.")


def run_detection_loop(settings, cameras, stream_manager, notifier, frame_buffer, frame_normalizer):
    """Main detection loop that processes frames from all cameras."""
    logger = logging.getLogger("Main")
    logger.info("[DETECTION] Starting detection loop")
    
    try:
        while True:
            for camera in cameras:
                if not camera.enabled:
                    continue
                    
                camera_id = str(camera.id)
                logger.info(f"[CAM:{camera_id}] Starting processing cycle")
                frame = stream_manager.get_frame(camera_id)
                
                if frame is not None:
                    logger.info(f"[CAM:{camera_id}] Frame received | shape: {frame.shape}")
                    # Process frame through frame normalizer
                    smoke_detected, processed_frames = frame_normalizer.process_frame(
                        camera_id, frame, camera
                    )
                    
                    if smoke_detected:
                        logger.warning(f"[CAM:{camera_id}] SMOKE DETECTED!")
                        # Send notification
                        if notifier:
                            notifier.send_notification(
                                f"Smoke detected on camera {camera_id}",
                                f"Smoke detected at {datetime.now()}"
                            )
                else:
                    logger.warning(f"[CAM:{camera_id}] No frame received")
            
            # Sleep after processing all cameras, not between each camera
            time.sleep(settings.sleep_time)
                
    except KeyboardInterrupt:
        logger.info("[DETECTION] Detection loop interrupted")
    except Exception as e:
        logger.exception(f"[DETECTION] Error in detection loop: {e}")