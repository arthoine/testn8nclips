import torch
import cv2
import json
from llava import LlavaVideo

# -----------------------------
# CONFIGURATION
# -----------------------------
VIDEO_PATH = "clip.mp4"           # Chemin vers ta vidéo
OUTPUT_JSON = "llava_video_output.json"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# -----------------------------
# INITIALISATION DU MODELE
# -----------------------------
print(f"Initialisation du modèle LLaVA-Video sur {DEVICE}...")
model = LlavaVideo.from_pretrained("llava/video-llava", device=DEVICE)
model.eval()

# -----------------------------
# LECTURE DE LA VIDEO
# -----------------------------
print("Lecture de la vidéo...")
cap = cv2.VideoCapture(VIDEO_PATH)
frames = []
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frames.append(frame)
    frame_count += 1
    if frame_count % 50 == 0:
        print(f"{frame_count} frames lues...")

cap.release()
print(f"Lecture terminée : {frame_count} frames au total.")

# -----------------------------
# TRAITEMENT VIDEO
# -----------------------------
print("Traitement de la vidéo avec LLaVA-Video...")
outputs = model.process_video(frames)

# -----------------------------
# SAUVEGARDE DES RESULTATS
# -----------------------------
print(f"Sauvegarde des résultats dans {OUTPUT_JSON}...")
results = {f"frame_{i}": out for i, out in enumerate(outputs)}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print("Traitement terminé avec succès !")
