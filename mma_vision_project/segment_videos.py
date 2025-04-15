# Step 6: Segment the Video
def segment_video_movinet(frames, predicted_labels, target_labels=['fighting', 'sparring']):
    segments = []
    current_segment = []
    for frame, label in zip(frames, predicted_labels):
        if label in target_labels:
            current_segment.append(frame)
        else:
            if current_segment:
                segments.append(current_segment)
                current_segment = []
    if current_segment:
        segments.append(current_segment)
    return segments

segments = segment_video_movinet(frames, predicted_labels)

