# Step 2: Extract Frames from the Video
import cv2

def extract_frames(video_path, frame_rate=1):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    frames = []
    while success:
        if count % frame_rate == 0:
            frames.append(image)
        success, image = vidcap.read()
        count += 1
    vidcap.release()
    return frames

frames = extract_frames('video.mp4')


