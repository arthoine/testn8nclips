#!/usr/bin/env python3
"""
🎥 VIDEO CLIP ANALYZER API - LLaVA-Video Edition (Windows Compatible + Fixed)
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
from typing import List, Dict
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
MAX_FRAMES = 16  # 🔧 Réduit pour éviter les problèmes de mémoire

print(f"\n🚀 Démarrage du serveur d'analyse vidéo sur {DEVICE}...")
print(f"📂 Modèle: {MODEL_PATH}")

# Charger le modèle LLaVA-Video
tokenizer = None
model = None
image_processor = None

if LLAVA_AVAILABLE:
    try:
        print("📥 Chargement du modèle LLaVA-Video (peut prendre 1-2 minutes)...")
        print("   ⚠️ Windows détecté - FlashAttention désactivé")
        
        # 🔧 FIX: Ne pas utiliser device_map="auto" pour éviter les conflits
        # On charge directement sur le device voulu
        tokenizer, model, image_processor, max_length = load_pretrained_model(
            MODEL_PATH,
            None,
            "llava_qwen",
            torch_dtype="float16",
            device_map=None,  # ← Changé de "auto" à None
            attn_implementation="eager"
        )
        
        # Maintenant on peut déplacer le modèle sans problème
        print(f"🔧 Déplacement du modèle sur {DEVICE}...")
        model = model.to(DEVICE)
        model.eval()
        
        print("✅ Modèle chargé avec succès!")
    except TypeError as e:
        print(f"⚠️ Tentative de chargement sans attn_implementation...")
        try:
            tokenizer, model, image_processor, max_length = load_pretrained_model(
                MODEL_PATH,
                None,
                "llava_qwen",
                torch_dtype="float16",
                device_map=None  # ← Aussi None ici
            )
            print(f"🔧 Déplacement du modèle sur {DEVICE}...")
            model = model.to(DEVICE)
            model.eval()
            print("✅ Modèle chargé avec succès!")
        except Exception as e2:
            print(f"❌ Erreur chargement modèle: {e2}")
            model = None
    except Exception as e:
        print(f"❌ Erreur chargement modèle: {e}")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifiez que le modèle est dans: models\\llava-video")
        print("2. Réinstallez LLaVA-NeXT")
        print("3. Si erreur CUDA: Utilisez CPU en modifiant DEVICE = 'cpu'")
        model = None


def load_video_frames(video_path: str, max_frames: int = MAX_FRAMES) -> tuple:
    """Charge les frames d'une vidéo avec decord"""
    try:
        vr = VideoReader(video_path, ctx=cpu(0), num_threads=1)
        total_frames = len(vr)
        video_fps = vr.get_avg_fps()
        video_time = total_frames / video_fps

        # Échantillonnage uniforme
        if total_frames > max_frames:
            frame_indices = np.linspace(0, total_frames - 1, max_frames, dtype=int)
        else:
            frame_indices = np.arange(total_frames)

        # Extraire les frames
        frames = vr.get_batch(frame_indices).asnumpy()

        # Calculer les timestamps
        frame_times = [i / video_fps for i in frame_indices]
        frame_time_str = ",".join([f"{t:.2f}s" for t in frame_times])

        return frames, frame_time_str, video_time

    except Exception as e:
        print(f"❌ Erreur lecture vidéo {video_path}: {e}")
        return None, None, None


def analyze_clip_with_llava(video_path: str, title: str, views: int, duration: float) -> Dict:
    """Analyse un clip avec LLaVA-Video"""

    if model is None or not LLAVA_AVAILABLE:
        return {
            "score": 50,
            "reason": "Modèle non disponible",
            "error": True
        }

    try:
        # Charger la vidéo
        frames, frame_time_str, video_time = load_video_frames(video_path, MAX_FRAMES)

        if frames is None:
            return {
                "score": 0,
                "reason": "Impossible de lire la vidéo",
                "error": True
            }

        # Prétraiter les frames
        video_tensor = image_processor.preprocess(frames, return_tensors="pt")["pixel_values"]
        
        # 🔧 FIX CRITIQUE: Déplacer le tensor sur GPU en float16
        video_tensor = video_tensor.to(DEVICE, dtype=torch.float16)
        video_tensor = [video_tensor]

        # Créer le prompt d'analyse
        time_instruction = f"The video lasts for {video_time:.2f} seconds, and {len(frames)} frames are sampled from it at {frame_time_str}."

        question = f"""{DEFAULT_IMAGE_TOKEN}
{time_instruction}

Analyze this Rust gameplay clip and rate it 0-100:

Title: "{title}"
Views: {views}
Duration: {duration}s

Criteria:
1. ACTION CONTENT (0-40pts): Epic moments (clutch, ace, raid) vs static/menu/AFK
2. VISUAL QUALITY (0-25pts): Clear image, smooth movement, good composition
3. VIEWER INTEREST (0-25pts): Engaging, suspenseful, memorable
4. TITLE ACCURACY (0-10pts): Title matches content, not misleading clickbait

Respond ONLY in JSON format:
{{"score": 85, "reason": "Intense combat with 1v3 clutch, excellent visual quality, matches title"}}
"""

        # Préparer la conversation
        conv_template = "qwen_1_5"
        conv = copy.deepcopy(conv_templates[conv_template])
        conv.append_message(conv.roles[0], question)
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

        # Tokenizer
        input_ids = tokenizer_image_token(
            prompt,
            tokenizer,
            IMAGE_TOKEN_INDEX,
            return_tensors="pt"
        ).unsqueeze(0).to(DEVICE)

        # Générer la réponse
        print(f"   🤖 Génération de l'analyse IA...")
        with torch.no_grad():
            output_ids = model.generate(
                input_ids,
                images=video_tensor,
                modalities=["video"],
                do_sample=False,
                temperature=0,
                max_new_tokens=200,
            )

        # Décoder
        response = tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0].strip()
        print(f"   💬 Réponse brute: {response[:100]}...")

        # Parser le JSON
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
                result['score'] = int(result.get('score', 60))
                print(f"   ✅ Score: {result['score']}/100")
            else:
                result = {
                    "score": 60,
                    "reason": f"Analyse complétée: {response[:100]}"
                }
        except (json.JSONDecodeError, ValueError) as e:
            result = {
                "score": 60,
                "reason": f"Réponse IA (format inattendu): {response[:150]}"
            }

        return result

    except Exception as e:
        print(f"❌ Erreur analyse: {e}")
        import traceback
        traceback.print_exc()
        return {
            "score": 50,
            "reason": f"Erreur technique: {str(e)}",
            "error": True
        }


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "device": DEVICE,
        "llava_available": LLAVA_AVAILABLE,
        "cuda_available": torch.cuda.is_available(),
        "max_frames": MAX_FRAMES
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyse un clip vidéo"""
    data = request.json

    video_path = data.get('video_path')
    title = data.get('title', '')
    views = data.get('views', 0)
    duration = data.get('duration', 0)

    if not video_path or not os.path.exists(video_path):
        return jsonify({
            "error": f"video_path invalide ou fichier inexistant: {video_path}"
        }), 400

    result = analyze_clip_with_llava(video_path, title, views, duration)
    return jsonify(result)


@app.route('/batch', methods=['POST'])
def batch_analyze():
    """Analyse plusieurs clips en batch"""
    data = request.json
    clips = data.get('clips', [])

    results = []
    total = len(clips)
    
    print(f"\n🎬 Début de l'analyse batch de {total} clips...")
    
    for i, clip in enumerate(clips):
        print(f"\n📹 Clip {i+1}/{total}: {clip.get('title', 'N/A')}")
        print(f"   📁 Fichier: {clip.get('video_path', 'N/A')}")
        
        result = analyze_clip_with_llava(
            clip.get('video_path'),
            clip.get('title', ''),
            clip.get('views', 0),
            clip.get('duration', 0)
        )
        result['index'] = i + 1
        results.append(result)
        
        if not result.get('error'):
            print(f"   ✅ Score: {result.get('score', 'N/A')}/100")
        else:
            print(f"   ❌ Erreur: {result.get('reason', 'N/A')}")

    print(f"\n✅ Analyse batch terminée: {len(results)} clips traités")

    return jsonify({
        "clips": results,
        "total_analyzed": len(results)
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎬 LLaVA-Video Analyzer - Serveur démarré")
    print("="*60)
    print(f"\n📡 URL: http://localhost:5000")
    print("\n📍 Endpoints:")
    print("   GET  /health  - Vérifier l'état")
    print("   POST /analyze - Analyser un clip")
    print("   POST /batch   - Analyser plusieurs clips")
    print("\n💡 Tips:")
    print(f"   - Max frames par vidéo: {MAX_FRAMES}")
    print(f"   - Analyse ~30-45s par clip")
    print(f"   - GPU: {DEVICE.upper()}")
    print("\n" + "="*60 + "\n")

    if not LLAVA_AVAILABLE:
        print("⚠️ ATTENTION: LLaVA non installé!")
        print("Installez avec: pip install git+https://github.com/LLaVA-VL/LLaVA-NeXT.git")
        print("\n")
    
    if model is None:
        print("⚠️ ATTENTION: Modèle non chargé!")
        print("Le serveur fonctionne mais retournera des erreurs.")
        print("\n")

    app.run(host='0.0.0.0', port=5000, debug=False)