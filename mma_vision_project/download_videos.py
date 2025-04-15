# Step 1: Download the YouTube Video
import pytube


def download_video(url, output_path='video.mp4'):
    yt = pytube.YouTube(url)
    ys = yt.streams.get_highest_resolution()
    ys.download(filename=output_path)


download_video('https://www.youtube.com/watch?v=mTooMUg7V9w&ab_channel=WALKMASTER')

