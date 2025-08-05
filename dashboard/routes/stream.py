from flask import Blueprint, Response, current_app
import cv2
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)
bp = Blueprint('stream', __name__)

def generate_mjpeg(camera_id: str, stage: str, frame_buffer):
    while True:
        try:
            frame = frame_buffer.get_frame(camera_id, stage)

            if frame is not None:
                if frame.dtype != np.uint8:
                    frame = np.clip(frame, 0, 255).astype(np.uint8)
                if len(frame.shape) == 2:
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                else:
                    logger.warning(f"[Stream] JPEG encode failed for {camera_id}, stage {stage}")
            else:
                logger.debug(f"[Stream] No frame for {camera_id}, stage {stage}")
                time.sleep(0.1)  # prevent busy loop

        except Exception as e:
            logger.exception(f"[Stream] MJPEG generation error for {camera_id}, stage {stage}: {e}")
            break

@bp.route('/<camera_id>/<stage>')
def video_feed(camera_id: str, stage: str):
    from flask import current_app
    with current_app.app_context():
        try:
            valid_stages = ['original', 'current', 'base', 'heatmap', 'mean', 'diff', 'wasserstein']
            if stage not in valid_stages:
                return {'error': f'Invalid stage: {stage}'}, 400

            logger.debug(f"[Stream] Starting MJPEG stream for {camera_id}, stage {stage}")
            frame_buffer = current_app.config['FRAME_BUFFER']  # inside context

            return Response(
                generate_mjpeg(camera_id, stage, frame_buffer),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )

        except Exception as e:
            logger.exception(f"[Stream] Error in video feed: {e}")
            return {'error': str(e)}, 500

@bp.route('/<camera_id>')
def camera_stream(camera_id: str):
    return video_feed(camera_id, 'original')