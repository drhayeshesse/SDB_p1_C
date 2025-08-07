import cv2
import numpy as np
import os

# Config
width, height = 896, 504
fps = 5
duration_no_smoke_start = 30  # seconds
duration_smoke_cycle = 15     # build + fade
duration_no_smoke_end = 15    # seconds
save_path = "assets/videos/parity_test_video.avi"

os.makedirs(os.path.dirname(save_path), exist_ok=True)

# VLC-friendly writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(save_path, fourcc, fps, (width, height), isColor=True)

def generate_smoke_frame(level):
    """
    Generate synthetic frame with smoke at level [0-1].
    level=0 => no smoke, level=1 => full smoke
    """
    base = np.full((height, width, 3), 180, dtype=np.uint8)  # background
    if level > 0:
        smoke = np.random.normal(loc=200, scale=25, size=(height, width)).astype(np.uint8)
        smoke_colored = cv2.cvtColor(smoke, cv2.COLOR_GRAY2BGR)
        base = cv2.addWeighted(base, 1 - level, smoke_colored, level, 0)
    return base

# Phase 1: No smoke
for _ in range(duration_no_smoke_start * fps):
    out.write(generate_smoke_frame(0))

# Phase 2: Smoke build-up (half of smoke cycle)
for i in range((duration_smoke_cycle // 2) * fps):
    level = i / ((duration_smoke_cycle // 2) * fps)
    out.write(generate_smoke_frame(level))

# Phase 3: Smoke fade (second half of smoke cycle)
for i in range((duration_smoke_cycle // 2) * fps):
    level = 1 - (i / ((duration_smoke_cycle // 2) * fps))
    out.write(generate_smoke_frame(level))

# Phase 4: No smoke again
for _ in range(duration_no_smoke_end * fps):
    out.write(generate_smoke_frame(0))

out.release()
print(f"✅ Parity test video saved: {save_path}")
print("🎥 Plays in VLC, 1 minute total duration.")