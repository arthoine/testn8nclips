import os
import cv2
import torch
import json
from flask import Flask, request, jsonify
from transformers import AutoProcessor, AutoModel
from typing import List, Dict
import numpy as np

app = Flask(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", "./models\llava-video")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_FRAMES = 12

print(f"Chargement du modele depuis {MODEL_PATH}...")

try:
    processor = AutoProcessor.from_pretrained(MODEL_PATH)
    model = AutoModel.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
        low_cpu_mem_usage=True
    ).to(DEVICE)
    print("Modele charge avec succes!")
except Exception as e:
    print(f"ERREUR chargement: {e}")
    processor = None
    model = None

# Voir /tmp/video_clip_analyzer.py pour le code complet

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
