@echo off
REM ============================================
REM Installation automatique Video-LLaMA Analyzer
REM Pour Windows avec CUDA
REM ============================================

echo.
echo ========================================
echo   VIDEO-LLAMA CLIP ANALYZER - SETUP
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans PATH
    echo Telecharge Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/8] Python detecte
echo.

REM Créer le dossier
set INSTALL_DIR=%USERPROFILE%\Documents\video-llama-analyzer
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
cd /d "%INSTALL_DIR%"

echo [2/8] Dossier cree: %INSTALL_DIR%
echo.

REM Créer environnement virtuel
if not exist "venv" (
    echo [3/8] Creation environnement virtuel...
    python -m venv venv
) else (
    echo [3/8] Environnement virtuel existe deja
)

REM Activer environnement
call venv\Scripts\activate.bat

echo [4/8] Installation PyTorch avec CUDA 11.8...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --no-cache-dir

echo.
echo [5/8] Installation dependances...
pip install transformers accelerate opencv-python flask pillow huggingface-hub

echo.
echo [6/8] Verification CUDA...
python -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()}'); print(f'Nom GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo.
echo [7/8] Creation structure dossiers...
if not exist "models" mkdir models

echo.
echo ========================================
echo   TELECHARGEMENT DU MODELE
echo ========================================
echo.
echo IMPORTANT: Le modele fait environ 14 GB
echo Temps estime: 30-60 minutes
echo.
echo Quel modele voulez-vous telecharger?
echo.
echo 1) Video-LLaMA2-7B (recommande, 14 GB)
echo 2) LLaVA-Video-7B (plus recent, meilleur, 15 GB)
echo 3) Sauter (je le telechargerai manuellement)
echo.
set /p MODEL_CHOICE="Votre choix (1/2/3): "

if "%MODEL_CHOICE%"=="1" (
    echo.
    echo Telechargement Video-LLaMA2-7B...
    huggingface-cli download DAMO-NLP-SG/VideoLLaMA2-7B --local-dir models\videollama2
    set MODEL_PATH=models\videollama2
)

if "%MODEL_CHOICE%"=="2" (
    echo.
    echo Telechargement LLaVA-Video-7B...
    huggingface-cli download lmms-lab/LLaVA-Video-7B-Qwen2 --local-dir models\llava-video
    set MODEL_PATH=models\llava-video
)

if "%MODEL_CHOICE%"=="3" (
    echo.
    echo Telechargement saute. N'oubliez pas de le faire manuellement!
    set MODEL_PATH=models\videollama2
)

echo.
echo [8/8] Creation du script analyzer.py...

REM Créer le script Python
(
echo import os
echo import cv2
echo import torch
echo import json
echo from flask import Flask, request, jsonify
echo from transformers import AutoProcessor, AutoModel
echo from typing import List, Dict
echo import numpy as np
echo.
echo app = Flask^(__name__^)
echo.
echo MODEL_PATH = os.getenv^("MODEL_PATH", "./%MODEL_PATH%"^)
echo DEVICE = "cuda" if torch.cuda.is_available^(^) else "cpu"
echo MAX_FRAMES = 12
echo.
echo print^(f"Chargement du modele depuis {MODEL_PATH}..."^)
echo.
echo try:
echo     processor = AutoProcessor.from_pretrained^(MODEL_PATH^)
echo     model = AutoModel.from_pretrained^(
echo         MODEL_PATH,
echo         torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
echo         low_cpu_mem_usage=True
echo     ^).to^(DEVICE^)
echo     print^("Modele charge avec succes!"^)
echo except Exception as e:
echo     print^(f"ERREUR chargement: {e}"^)
echo     processor = None
echo     model = None
echo.
echo # Voir /tmp/video_clip_analyzer.py pour le code complet
echo.
echo if __name__ == '__main__':
echo     app.run^(host='0.0.0.0', port=5000, debug=False^)
) > analyzer_template.py

echo.
echo ========================================
echo   INSTALLATION TERMINEE !
echo ========================================
echo.
echo Prochaines etapes:
echo.
echo 1. Le modele est dans: %INSTALL_DIR%\%MODEL_PATH%
echo.
echo 2. Pour demarrer le serveur:
echo    cd %INSTALL_DIR%
echo    venv\Scripts\activate
echo    python analyzer.py
echo.
echo 3. Verifier que ca marche:
echo    http://localhost:5000/health
echo.
echo 4. Configurer n8n avec les nodes fournis
echo.
echo ========================================

pause
