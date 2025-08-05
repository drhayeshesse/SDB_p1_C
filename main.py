import logging
from threading import Thread
from utils.settings import load_settings
from utils.camera_config import load_cameras
from rtsp_stream.stream_manager import StreamManager as RTSPStreamManager
from dashboard.app import run_dashboard
from utils.main_utils import (
    initialize_notifier, initialize_logger,
    run_detection_loop, initialize_event_recorder
)
from frame_buffer.frame_buffer import FrameBuffer
from preprocessing.frame_normalizer import FrameNormalizer

# === Initialize logger (console + optional file) ===
logger = initialize_logger()
logger.info("[SYSTEM] Logger initialized")

# === Load settings and cameras ===
settings = load_settings()
logger.info(f"[SYSTEM] Settings loaded: {settings}")
cameras = load_cameras()
logger.info(f"[SYSTEM] Loaded {len(cameras)} cameras")

# === Display system information (original logic) ===
logger.info(" ")
logger.info(" ------------  ---------------  ------------  ------------ ")
logger.info(" ------------  ---------------  ------------  ------------ ")
logger.info(" ------------  ---------------  ------------  ------------ ")
logger.info(" ------------  Smoke Detective  (python app) ")
logger.info(" ")
logger.info(" ")
logger.info(f" Interval between frames:                    {settings.sleep_time}")
logger.info(f" SENSITIVITY threshold:                      {settings.sensitivity}")
logger.info(f" SENSITIVITY_VAL (validation) threshold:     {settings.sensitivity_val}")
logger.info(f" MOTION THRESHOLD:                           {settings.motion_threshold}")
logger.info(f" MOTION COUNT THRESHOLD:                     {settings.motion_count_threshold}")
logger.info(f" Surveillance counter reset:                 {settings.surveillance_counter_threshold}")
logger.info(f" Validation frames:                          {settings.n_frames_validation}")
logger.info(f" Patch size:                                 {settings.sliding_window}")
logger.info(f" N_PATCHES_VALIDATE:                         {settings.n_patches_validate}")
logger.info(" ")

# === Initialize notifier ===
notifier = initialize_notifier(settings)
logger.info("[SYSTEM] Notifier initialized")

# === Initialize event recorder ===
initialize_event_recorder(settings)
logger.info("[SYSTEM] Event recorder initialized")

# === Start stream manager ===
stream_manager = RTSPStreamManager(settings)
stream_manager.start_all_streams(cameras)
logger.info("[SYSTEM] All camera streams started")

# === Initialize frame buffer and FrameNormalizer ===
frame_buffer = FrameBuffer((settings.frame_width, settings.frame_height))
frame_normalizer = FrameNormalizer(settings, frame_buffer)
logger.info("[SYSTEM] FrameNormalizer initialized")



# === Start Flask dashboard (in thread) ===
logger.info("[DASHBOARD] Starting dashboard on http://localhost:5050")
Thread(target=run_dashboard, args=(settings, frame_buffer), daemon=True).start()

# === Start detection loop (original two-phase logic) ===
try:
    logger.info("[DETECTION] Starting main detection loop")
    run_detection_loop(settings, cameras, stream_manager, notifier, frame_buffer, frame_normalizer)
except KeyboardInterrupt:
    logger.info("[SYSTEM] Shutdown signal received")
    stream_manager.stop_all_streams()
    logger.info("[SYSTEM] All streams stopped")