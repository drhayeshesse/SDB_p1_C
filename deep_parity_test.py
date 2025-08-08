import cv2
import numpy as np
import logging
import os
from collections import deque
from datetime import datetime

from smoke.smoke_detector_no_motion import SmokeDetector as SmokeDetectorStandard
from smoke.smoke_detector_optimized_no_motion import SmokeDetector as SmokeDetectorOptimized
from utils.settings import load_settings

# Path to standard parity test video
video_path = "assets/videos/parity_test_video.avi"

# Configure logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "deep_parity_test.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ParityTest")


def load_parity_video(path):
    """Load frames from the standard parity test video."""
    cap = cv2.VideoCapture(path)

    if not cap.isOpened():
        raise FileNotFoundError(f"Parity test video not found: {path}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    logger.info(f"Loaded {len(frames)} frames from {path} for parity testing")
    return frames


def deep_parity_test():
    settings = load_settings()
    logger.info(f"Settings loaded: {settings}")

    # Init detectors
    det_std = SmokeDetectorStandard(settings)
    det_opt = SmokeDetectorOptimized(settings)

    # Load pre-generated parity test video frames
    frames = load_parity_video(video_path)

    buffer = deque(maxlen=11)
    mismatches = 0

    for idx, frame in enumerate(frames):
        buffer.append(frame)

        if len(buffer) == 11:
            gray_buffer = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in buffer]
            gray_stack = np.stack(gray_buffer).astype(np.float32)

            std_result, _ = det_std.check_video_for_smoke(
                gray_stack, camera_id="TEST_CAM"
                )
            opt_result, _ = det_opt.check_video_for_smoke(
                 gray_stack, camera_id="TEST_CAM"
                )

            match = std_result == opt_result
            logger.info(
                f"Frame {idx:02d} | Std: {std_result} | Opt: {opt_result} | Match: {match}"
            )

            if not match:
                mismatches += 1
                logger.error(f"❌ Mismatch at frame {idx:02d}")

    if mismatches == 0:
        logger.info(
            "✅ All detection results match between standard and optimized detectors."
        )
    else:
        logger.warning(
            f"⚠️ {mismatches} mismatches found between detectors."
        )


if __name__ == "__main__":
    deep_parity_test()