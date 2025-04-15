import streamlit as st
import os
import cv2
import tempfile
import numpy as np
import torch
from torchvision import transforms
from PIL import Image


# Charger un modèle de détection d'activité pré-entraîné (exemple : I3D, SlowFast, etc.)
# Remplacez par un vrai modèle adapté
class SimpleActionDetector:
    def __init__(self):
        self.model = torch.hub.load('facebookresearch/pytorchvideo', 'slowfast_r50', pretrained=True)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def predict(self, frames):
        frames = [self.transform(Image.fromarray(frame)) for frame in frames]
        frames = torch.stack(frames).unsqueeze(0)  # Ajouter batch dimension
        with torch.no_grad():
            output = self.model(frames)
        return output.argmax().item()  # Retourne l'action détectée


# Initialiser le détecteur
detector = SimpleActionDetector()


# Fonction améliorée pour détecter les moments de sparring
def detect_sparring(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    sparring_moments = []
    frame_buffer = []

    for i in range(0, frame_count, fps * 2):  # Vérification toutes les 2 secondes
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break

        frame_buffer.append(frame)

        if len(frame_buffer) == 16:  # Exemple : utiliser 16 frames pour la détection
            action = detector.predict(frame_buffer)
            frame_buffer = []

            if action == 1:  # Supposons que 1 = sparring (ajuster selon le modèle)
                sparring_moments.append(i / fps)

    cap.release()
    return sparring_moments


# Interface
st.title("Extraction de Sparrings en Vidéo")

uploaded_file = st.file_uploader("Uploader une vidéo de sport de combat", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())

    st.video(tfile.name)

    if st.button("Extraire les moments de sparring"):
        moments = detect_sparring(tfile.name)

        if moments:
            st.write("Moments détectés (en secondes) :", moments)
        else:
            st.write("Aucun sparring détecté.")
