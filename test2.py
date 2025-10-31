import requests
import json
import os

# ------------------ CONFIG ------------------ #
SERVER_URL = "http://localhost:5000/analyze"
VIDEO_PATH = r"J:\claude\clip.mp4"  # ← chemin vers ta vidéo
TITLE = "Test Clip"
VIEWS = 1000
DURATION = 30  # secondes

# Vérifier que le fichier existe
if not os.path.exists(VIDEO_PATH):
    print(f"❌ Fichier non trouvé: {VIDEO_PATH}")
    exit(1)

# Préparer le payload
payload = {
    "video_path": VIDEO_PATH,
    "title": TITLE,
    "views": VIEWS,
    "duration": DURATION
}

# Envoyer la requête POST
print("📤 Envoi de la requête au serveur LLaVA...")
try:
    response = requests.post(SERVER_URL, json=payload, timeout=300)
except requests.exceptions.RequestException as e:
    print(f"❌ Erreur requête: {e}")
    exit(1)

# Vérifier la réponse
if response.status_code == 200:
    try:
        data = response.json()
        print("✅ Analyse terminée !")
        print(f"   Score : {data.get('score', 'N/A')}/100")
        print(f"   Raison: {data.get('reason', 'N/A')}")
    except json.JSONDecodeError:
        print("❌ Impossible de décoder la réponse JSON")
        print(response.text)
else:
    print(f"❌ Erreur HTTP {response.status_code}")
    print(response.text)
