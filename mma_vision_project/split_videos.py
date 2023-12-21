import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from glob import glob

import IPython.display as ipd
from tqdm.notebook import tqdm

import subprocess

from moviepy.video.io.VideoFileClip import VideoFileClip
import os

def split_video(input_video_path, output_folder, segment_duration):
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_folder, exist_ok=True)

    # Charger la vidéo
    video_clip = VideoFileClip(input_video_path)

    # Obtenir la durée totale de la vidéo
    total_duration = video_clip.duration

    # Calculer le nombre total de segments
    total_segments = int(total_duration // segment_duration)

    # Boucle pour extraire chaque segment
    for segment_num in range(total_segments):
        # Calculer les temps de début et de fin du segment
        start_time = segment_num * segment_duration
        end_time = (segment_num + 1) * segment_duration

        # Extraire le segment de la vidéo
        segment_clip = video_clip.subclip(start_time, end_time)

        # Sauvegarder le segment dans un fichier
        output_path = os.path.join(output_folder, f'segment_{segment_num + 1}.mp4')
        segment_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    # Fermer la vidéo d'origine
    video_clip.close()


if __name__ == "__main__":
    input_video_path = 'dataset/train/eating_source/Israel Adesanya bulking on meat pie ahead of Alex Pereira fight #ufc #shorts #ufc281.mp4'
    output_folder = 'dataset/train/eating_source'
    segment_duration = 5  # Durée de chaque segment en secondes

    split_video(input_video_path, output_folder, segment_duration)