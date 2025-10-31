# 🔧 GUIDE DE DÉPANNAGE - SERVEUR LLAVA VIDEO

## 🎯 PROBLÈME: "The service refused the connection"

Cela signifie que ton serveur LLaVA ne tourne PAS sur `http://localhost:5000`

---

## ✅ SOLUTION RAPIDE

### Étape 1: Vérifie si le serveur tourne

**Windows CMD:**
```cmd
curl http://localhost:5000/health
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health"
```

**Python:**
```bash
python test_llava_server.py
```

---

### Étape 2: Si ça ne marche PAS, lance le serveur !

1. **Ouvre un terminal séparé** (PowerShell, CMD, ou Git Bash)

2. **Va dans le dossier de ton serveur:**
   ```cmd
   cd C:\chemin\vers\ton\serveur
   ```

3. **Lance le serveur:**
   ```cmd
   python llava_video_server.py
   ```

4. **Attends le message:**
   ```
   🚀 Server running on http://localhost:5000
   ```

5. **LAISSE CE TERMINAL OUVERT !**
   - Le serveur doit tourner en permanence
   - Ne ferme PAS ce terminal tant que tu utilises n8n

---

## 🐛 ERREURS COURANTES

### ❌ "Port 5000 already in use"
**Problème:** Un autre programme utilise le port 5000

**Solution:**
```cmd
# Windows: Voir qui utilise le port 5000
netstat -ano | findstr :5000

# Tuer le processus (remplace PID par le numéro)
taskkill /PID <PID> /F
```

---

### ❌ "Ollama not found"
**Problème:** Ollama n'est pas lancé

**Solution:**
```cmd
# Lance Ollama dans un autre terminal
ollama serve
```

---

### ❌ "Model llava-video not found"
**Problème:** Le modèle LLaVA n'est pas téléchargé

**Solution:**
```cmd
ollama pull llava
```

---

### ❌ "Connection timeout"
**Problème:** Le serveur est trop lent ou surchargé

**Solution:**
- Augmente le timeout dans n8n (options → timeout: 600000)
- Vérifie que ton PC a assez de RAM (minimum 8GB)
- Ferme d'autres programmes gourmands

---

## 🧪 TESTS DE DIAGNOSTIC

### Test 1: Port ouvert ?
```cmd
# Windows
telnet localhost 5000

# PowerShell
Test-NetConnection -ComputerName localhost -Port 5000
```

### Test 2: Serveur répond ?
```bash
python test_llava_server.py
```

### Test 3: Endpoint /batch fonctionne ?
```cmd
curl -X POST http://localhost:5000/batch ^
  -H "Content-Type: application/json" ^
  -d "{\"clips\":[{\"video_path\":\"test.mp4\",\"title\":\"Test\",\"views\":0,\"duration\":30,\"clip_id\":\"test\"}],\"total\":1}"
```

---

## 📋 CHECKLIST AVANT DE LANCER N8N

- [ ] Ollama tourne (`ollama serve` dans un terminal)
- [ ] Serveur LLaVA tourne (`python llava_video_server.py` dans un autre terminal)
- [ ] Port 5000 est libre (pas d'autre serveur dessus)
- [ ] Test `curl http://localhost:5000/health` fonctionne
- [ ] Les clips sont téléchargés dans `J:\twitch_clips`

---

## 🎬 ORDRE DE DÉMARRAGE

1. **Terminal 1:** Lance Ollama
   ```cmd
   ollama serve
   ```

2. **Terminal 2:** Lance le serveur LLaVA
   ```cmd
   python llava_video_server.py
   ```

3. **Attends les messages:**
   - Terminal 1: "Ollama is running"
   - Terminal 2: "Server running on port 5000"

4. **Maintenant lance n8n** dans un 3ème terminal
   ```cmd
   n8n start
   ```

5. **Exécute ton workflow !**

---

## 💡 TIPS

### Garder les serveurs actifs
- Utilise **Windows Terminal** pour avoir plusieurs onglets
- Ou lance chaque serveur dans un CMD/PowerShell séparé
- **NE FERME PAS** ces terminaux pendant l'utilisation !

### Logs du serveur
Si le serveur crash, regarde les logs dans le terminal du serveur LLaVA

### Performance
- L'analyse vidéo prend ~30s par clip
- Pour 15 clips = ~7-8 minutes d'analyse
- Sois patient ! 🕐

---

## 🆘 SI RIEN NE MARCHE

1. Redémarre tout:
   - Ferme tous les terminaux
   - Redémarre Ollama
   - Redémarre le serveur LLaVA
   - Relance n8n

2. Vérifie les logs:
   - Dans le terminal du serveur LLaVA
   - Dans n8n (onglet "Executions")

3. Teste manuellement avec Python:
   ```bash
   python test_llava_server.py
   ```

4. Contacte-moi avec:
   - Le message d'erreur exact
   - Les logs du serveur
   - Le résultat de `test_llava_server.py`

---

## 📞 CONTACT

Si tu es bloqué, envoie-moi:
1. Screenshot de l'erreur n8n
2. Logs du terminal serveur LLaVA
3. Résultat de `python test_llava_server.py`
