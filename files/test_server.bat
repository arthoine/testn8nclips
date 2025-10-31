@echo off
REM Test rapide du serveur LLaVA

echo ============================================
echo TEST SERVEUR LLAVA - PORT 5000
echo ============================================
echo.

echo Test 1: Ping du port 5000...
curl -s -o nul -w "Status: %%{http_code}\n" http://localhost:5000/health 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Le serveur ne repond pas !
    echo.
    echo Solutions:
    echo   1. Lance le serveur: python llava_video_server.py
    echo   2. Verifie qu'Ollama tourne: ollama serve
    echo   3. Verifie le port 5000 disponible
    echo.
    pause
    exit /b 1
)

echo.
echo Test 2: Endpoint /health...
curl -s http://localhost:5000/health
echo.

echo.
echo Test 3: Test JSON simple...
echo {"clips":[{"video_path":"test.mp4","title":"Test","views":0,"duration":30,"clip_id":"test"}],"total":1} > test_data.json
curl -X POST http://localhost:5000/batch -H "Content-Type: application/json" -d @test_data.json
del test_data.json
echo.

echo.
echo ============================================
echo TEST TERMINE !
echo ============================================
pause
