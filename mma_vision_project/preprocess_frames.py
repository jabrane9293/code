# Step 3: Preprocess the Frames
import numpy as np

def preprocess_frames_movinet(frames):
    preprocessed_frames = []
    for frame in frames:
        frame = cv2.resize(frame, (224, 224))
        frame = frame / 255.0  # Normalize to [0, 1]
        preprocessed_frames.append(frame)
    return np.array(preprocessed_frames)

preprocessed_frames = preprocess_frames_movinet(frames)

