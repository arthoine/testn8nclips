#!/usr/bin/env python3
"""
🎥 VIDEO CLIP ANALYZER API - LLaVA-Video Edition (Windows + GPU NVIDIA)
Analyse les clips Twitch avec LLaVA-Video pour scorer leur qualité
"""

import os
import sys
import json
import warnings
import numpy as np
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")

from flask import Flask, request, jsonify
from typing import Dict
from decord import VideoReader, cpu
import copy

warnings.filterwarnings("ignore")

# ⚠️ DÉSACTIVER FLASHATTENTION POUR WINDOWS
os.environ["DISABLE_FLASH_ATTN"] = "1"

# Importer LLaVA
try:
    from llava.model.builder import load_pretrained_model
    from llava.mm_utils import tokenizer_image_token
    from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
    from llava.conversation import conv_templates
    LLAVA_AVAILABLE = True
except ImportError:
    print("⚠️ LLaVA non installé. Installez avec: pip install git+https://github.com/LLaVA-VL/LLaVA-NeXT.git")
    LLAVA_AVAILABLE = False

app = Flask(__name__)

# Configuration
MODEL_PATH = r".\models\llava-video"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_FRAMES = 16  # Réduit pour éviter les problèmes de mémoire

print(f"\n🚀 Démarrage du serveur d'analyse vidéo sur {DEVICE}...")
print(f"📂 Modèle: {MODEL_PATH}")

# Charger le modèle LLaVA-Video
tokenizer = None
model = None
image_processor = None

if LLAVA_AVAILABLE:
    try:
        print("📥 Chargement du modèle LLaVA-Video (1-2 minutes)...")
        tokenizer, model, image_processor, max_length = load_pretrained_model(
            MODEL_PATH,
            None,
            "llava_qwen",
            torch_dtype="float16",
            device_map=None,
            attn_implementation="eager"
        )
        model = model.to(DEVICE)
        model.eval()
        print("✅ Modèle chargé avec succès!")
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")
        model = None

def load_video_frames(video_path: str, max_frames: int = MAX_FRAMES) -> tuple:
    """Charge les frames d'une vidéo avec Decord"""
    try:
        vr = VideoReader(video_path, ctx=cpu(0), num_threads=1)
        total_frames = len(vr)
        video_fps = vr.get_avg_fps()
        video_time = total_frames / video_fps

        # Échantillonnage uniforme
        frame_indices = np.linspace(0, total_frames - 1, min(max_frames, total_frames), dtype=int)
        frames = vr.get_batch(frame_indices).asnumpy()
        frame_times = [i / video_fps for i in frame_indices]
        frame_time_str = ",".join([f"{t:.2f}s" for t in frame_times])

        return frames, frame_time_str, video_time
    except Exception as e:
        print(f"❌ Erreur lecture vidéo {video_path}: {e}")
        return None, None, None

def analyze_clip_with_llava(video_path: str, title: str, views: int, duration: float) -> Dict:
    """Analyse un clip avec LLaVA-Video"""
    if model is None or not LLAVA_AVAILABLE:
        return {"score": 50, "reason": "Modèle non disponible", "error": True}

    try:
        frames, frame_time_str, video_time = load_video_frames(video_path, MAX_FRAMES)
        if frames is None or len(frames) == 0:
            return {"score": 0, "reason": "Impossible de lire la vidéo", "error": True}

        # Prétraiter les frames et éviter le meta tensor
        video_tensor = image_processor.preprocess(frames, return_tensors="pt")["pixel_values"]
        video_tensor = video_tensor.float().contiguous()  # ← Fix Windows / Meta tensor
        video_tensor = video_tensor.to(DEVICE, dtype=torch.float16)
        video_tensor = [video_tensor]

        print(f"Video tensor shape: {video_tensor[0].shape}, dtype: {video_tensor[0].dtype}, device: {video_tensor[0].device}")

        # Créer le prompt d'analyse
        time_instruction = f"The video lasts for {video_time:.2f} seconds, and {len(frames)} frames are sampled from it at {frame_time_str}."
        question = f"""{DEFAULT_IMAGE_TOKEN}
{time_instruction}

Analyze this Rust gameplay clip and rate it 0-100:

Title: "{title}"
Views: {views}
Duration: {duration}s

Criteria:
1. ACTION CONTENT (0-40pts)
2. VISUAL QUALITY (0-25pts)
3. VIEWER INTEREST (0-25pts)
4. TITLE ACCURACY (0-10pts)

Respond ONLY in JSON format:
{{"score": 85, "reason": "Intense combat with 1v3 clutch, excellent visual quality, matches title"}}
"""

        conv = copy.deepcopy(conv_templates["qwen_1_5"])
        conv.append_message(conv.roles[0], question)
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

        input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt").unsqueeze(0).to(DEVICE)

        print("🤖 Génération de l'analyse IA...")
        with torch.no_grad():
            output_ids = model.generate(
                input_ids,
                images=video_tensor,
                modalities=["video"],
                do_sample=False,
                temperature=0,
                max_new_tokens=200,
            )

        response = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()
        print(f"💬 Réponse brute: {response[:100]}...")

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
                result['score'] = int(result.get('score', 60))
            else:
                result = {"score": 60, "reason": f"Analyse complétée: {response[:100]}"}
        except (json.JSONDecodeError, ValueError):
            result = {"score": 60, "reason": f"Réponse IA (format inattendu): {response[:150]}"}

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"score": 50, "reason": f"Erreur technique: {str(e)}", "error": True}

# ------------------ Endpoints ------------------ #

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None, "device": DEVICE, "llava_available": LLAVA_AVAILABLE, "cuda_available": torch.cuda.is_available(), "max_frames": MAX_FRAMES})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    video_path = data.get('video_path')
    title = data.get('title', '')
    views = data.get('views', 0)
    duration = data.get('duration', 0)

    if not video_path or not os.path.exists(video_path):
        return jsonify({"error": f"video_path invalide ou fichier inexistant: {video_path}"}), 400

    result = analyze_clip_with_llava(video_path, title, views, duration)
    return jsonify(result)

@app.route('/batch', methods=['POST'])
def batch_analyze():
    data = request.json
    clips = data.get('clips', [])
    results = []
    for i, clip in enumerate(clips):
        result = analyze_clip_with_llava(
            clip.get('video_path'),
            clip.get('title', ''),
            clip.get('views', 0),
            clip.get('duration', 0)
        )
        result['index'] = i + 1
        results.append(result)
    return jsonify({"clips": results, "total_analyzed": len(results)})

# ------------------ Main ------------------ #
if __name__ == '__main__':
    print(f"🎬 LLaVA-Video Analyzer sur {DEVICE}, max frames {MAX_FRAMES}")
    app.run(host='0.0.0.0', port=5000, debug=False)
