# Test du serveur LLaVA Video - PowerShell
# Usage: powershell -ExecutionPolicy Bypass -File test_server.ps1

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 49) -ForegroundColor Cyan
Write-Host "🎬 DIAGNOSTIC SERVEUR LLAVA VIDEO" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 49) -ForegroundColor Cyan
Write-Host ""

# Test 1: Port 5000 ouvert ?
Write-Host "🔍 Test 1: Vérification du port 5000..." -ForegroundColor Cyan
Write-Host ("-" * 50) -ForegroundColor Gray

try {
    $connection = Test-NetConnection -ComputerName localhost -Port 5000 -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "✅ Port 5000 est OUVERT - Un service écoute" -ForegroundColor Green
        $portOpen = $true
    } else {
        Write-Host "❌ Port 5000 est FERMÉ - Aucun service" -ForegroundColor Red
        Write-Host "   → Lance: python llava_video_server.py" -ForegroundColor Yellow
        $portOpen = $false
    }
} catch {
    Write-Host "⚠️  Impossible de tester le port (erreur réseau)" -ForegroundColor Yellow
    $portOpen = $false
}

if (-not $portOpen) {
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor Red
    Write-Host ("=" * 49) -ForegroundColor Red
    Write-Host "❌ DIAGNOSTIC: Le serveur ne tourne PAS" -ForegroundColor Red
    Write-Host "=" -NoNewline -ForegroundColor Red
    Write-Host ("=" * 49) -ForegroundColor Red
    Write-Host ""
    Write-Host "📝 SOLUTION:" -ForegroundColor Yellow
    Write-Host "   1. Ouvre PowerShell/CMD" -ForegroundColor White
    Write-Host "   2. cd C:\chemin\vers\ton\serveur" -ForegroundColor White
    Write-Host "   3. python llava_video_server.py" -ForegroundColor White
    Write-Host "   4. Attends 'Server running on port 5000'" -ForegroundColor White
    Write-Host ""
    Pause
    exit 1
}

# Test 2: Endpoint /health
Write-Host ""
Write-Host "🔍 Test 2: Test de l'endpoint /health..." -ForegroundColor Cyan
Write-Host ("-" * 50) -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get -TimeoutSec 5
    Write-Host "✅ Serveur LLaVA répond !" -ForegroundColor Green
    Write-Host "   Réponse: $($response | ConvertTo-Json -Compress)" -ForegroundColor White
    $healthOk = $true
} catch {
    Write-Host "❌ ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    $healthOk = $false
}

# Test 3: Endpoint /batch avec données factices
Write-Host ""
Write-Host "🔍 Test 3: Test de l'endpoint /batch..." -ForegroundColor Cyan
Write-Host ("-" * 50) -ForegroundColor Gray

$testData = @{
    clips = @(
        @{
            video_path = "C:/test/video.mp4"
            title = "Test Clip"
            views = 1000
            duration = 30
            clip_id = "test123"
        }
    )
    total = 1
} | ConvertTo-Json

try {
    Write-Host "📤 Envoi de 1 clip de test..." -ForegroundColor White
    $response = Invoke-RestMethod -Uri "http://localhost:5000/batch" -Method Post -Body $testData -ContentType "application/json" -TimeoutSec 30
    Write-Host "✅ Endpoint /batch fonctionne !" -ForegroundColor Green
    Write-Host "   Clips analysés: $($response.total_analyzed)" -ForegroundColor White
    $batchOk = $true
} catch {
    Write-Host "❌ ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    $batchOk = $false
}

# Résumé
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 49) -ForegroundColor Cyan
Write-Host "📊 RÉSUMÉ DU DIAGNOSTIC" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 49) -ForegroundColor Cyan

if ($portOpen) {
    Write-Host "Port 5000:        ✅ Ouvert" -ForegroundColor Green
} else {
    Write-Host "Port 5000:        ❌ Fermé" -ForegroundColor Red
}

if ($healthOk) {
    Write-Host "Endpoint /health: ✅ OK" -ForegroundColor Green
} else {
    Write-Host "Endpoint /health: ❌ Échec" -ForegroundColor Red
}

if ($batchOk) {
    Write-Host "Endpoint /batch:  ✅ OK" -ForegroundColor Green
} else {
    Write-Host "Endpoint /batch:  ❌ Échec" -ForegroundColor Red
}

Write-Host ""
if ($portOpen -and $healthOk -and $batchOk) {
    Write-Host "🎉 TOUT FONCTIONNE ! Ton serveur LLaVA est prêt !" -ForegroundColor Green
} else {
    Write-Host "⚠️  Il y a des problèmes - Vérifie les erreurs ci-dessus" -ForegroundColor Yellow
}

Write-Host ""
Pause
