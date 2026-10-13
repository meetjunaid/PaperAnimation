"""usage: check_video.py <video.mp4> <sheet.png>

Prints the video's size, frame rate, frame count, duration and whether it has
sound, and saves a
contact sheet with one thumbnail per card. A thin red cross marks the frame
centre, where the highlighted phrase should sit on every card.
"""
import subprocess
import sys
import cv2
import imageio_ffmpeg
import numpy as np

src, out = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS)
w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
tw = 270 if h > w else 480
th = round(tw * h / w)
picks = {int(i * 0.125 * fps + 0.5) + 2 for i in range(23)}  # a few frames into each card
thumbs, n = [], 0
while True:
    ok, fr = cap.read()
    if not ok:
        break
    if n in picks:
        t = cv2.resize(fr, (tw, th), interpolation=cv2.INTER_AREA)
        cv2.line(t, (tw // 2 - 12, th // 2), (tw // 2 + 12, th // 2), (0, 0, 255), 1)
        cv2.line(t, (tw // 2, th // 2 - 12), (tw // 2, th // 2 + 12), (0, 0, 255), 1)
        thumbs.append(t)
    n += 1
cols = 8 if h > w else 6
thumbs += [np.zeros_like(thumbs[0])] * (-len(thumbs) % cols)
cv2.imwrite(out, np.vstack([np.hstack(thumbs[r:r + cols]) for r in range(0, len(thumbs), cols)]))
probe = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", src], capture_output=True, text=True).stderr
sound = "with sound" if "Audio:" in probe else "silent"
print(f"{src}: {w}x{h}, {fps:g} fps, {n} frames, {n / fps:.2f} s, {sound} -> {out}")
