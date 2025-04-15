# Step 7: Create the Compilation
from moviepy.editor import ImageSequenceClip, concatenate_videoclips

def create_compilation(segments, output_path='compilation.mp4'):
    all_clips = []
    for segment in segments:
        clip = ImageSequenceClip([cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in segment], fps=30)
        all_clips.append(clip)
    final_clip = concatenate_videoclips(all_clips)
    final_clip.write_videofile(output_path)

create_compilation(segments)