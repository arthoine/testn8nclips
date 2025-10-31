cd C:\Users\Antoine\Documents\video-llama-analyzer
venv\Scripts\activate
python analyzer.py
```

Tu devrais voir :
```
🚀 Démarrage du serveur d'analyse vidéo sur cuda...
📂 Modèle: .\models\llava-video
📥 Chargement du modèle LLaVA-Video (peut prendre 1-2 minutes)...
✅ Modèle chargé avec succès!

============================================================
🎬 LLaVA-Video Analyzer - Serveur démarré
============================================================

📡 URL: http://localhost:5000

📍 Endpoints:
   GET  /health  - Vérifier l'état
   POST /analyze - Analyser un clip
   POST /batch   - Analyser plusieurs clips

============================================================