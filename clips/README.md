# Script de Compilation de Clips Twitch

Ce script Python compile automatiquement plusieurs clips Twitch en une seule vidéo avec overlay du nom du streamer.

## Prérequis

### Python
- Python 3.6 ou supérieur

### FFmpeg (REQUIS)
FFmpeg doit être installé et accessible dans votre PATH système.

**Installation de FFmpeg:**

**Windows:**
```powershell
# Option 1: Avec winget (Windows 10/11)
winget install ffmpeg

# Option 2: Téléchargement manuel
# 1. Téléchargez depuis https://www.ffmpeg.org/download.html
# 2. Extrayez l'archive
# 3. Ajoutez le dossier bin à votre PATH système
```

**Linux:**
```bash
# Debian/Ubuntu
sudo apt update && sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

**macOS:**
```bash
# Avec Homebrew
brew install ffmpeg
```

**Vérification de l'installation:**
```bash
ffmpeg -version
```

Le script vérifiera automatiquement la présence de FFmpeg au démarrage.

## Utilisation

### Syntaxe de base

```bash
python clip.py <chemin_dossier_clips> [--json <chemin_fichier_json>]
```

### Paramètres

- `clips_path` (obligatoire) : Chemin du dossier contenant les fichiers MP4 des clips
- `--json` ou `-j` (optionnel) : Chemin du fichier JSON contenant les métadonnées. Par défaut, le script cherche `clips_data.json` dans le dossier des clips

### Exemples

#### Utilisation avec le JSON par défaut
```bash
python clip.py /chemin/vers/dossier_clips/
```

#### Utilisation avec un JSON personnalisé
```bash
python clip.py /chemin/vers/dossier_clips/ --json /chemin/vers/custom.json
```

#### Sur Windows
```cmd
python clip.py J:\claude\clips\clip_twitch_ARC_Raiders_20251031_0107\
```

#### Sur Linux
```bash
python3 clip.py /home/user/testn8nclips/clips/clip_twitch_ARC_Raiders_20251031_0107/
```

## Structure attendue

### Dossier des clips
Le dossier doit contenir :
- Les fichiers MP4 nommés avec leur ID (ex: `DifferentFitTroutCoolStoryBob-5TixTPM58R2gfWCu.mp4`)
- Un fichier `clips_data.json` (ou spécifié avec --json)

### Format du fichier JSON
```json
{
  "metadata": {
    "total_clips": 3,
    "total_duration": "1m48s",
    "game": "ARC Raiders"
  },
  "clips": [
    {
      "id": "DifferentFitTroutCoolStoryBob-5TixTPM58R2gfWCu",
      "broadcaster_name": "MasterSnakou",
      "duration": 18,
      "title": "THE grenade",
      "view_count": 251
    }
  ]
}
```

## Sortie

Le script génère :
- Un dossier `temp_processed/` contenant les clips avec overlay
- Un fichier `compilation_finale.mp4` dans le dossier des clips

## Fonctionnalités

- Ajout automatique du nom du streamer en overlay (6 secondes max)
- Fade in/out de l'overlay
- Détection automatique de la font système (Windows/Linux)
- Gestion des erreurs et timeouts
- Statistiques de traitement

## Codes de retour

- `0` : Succès
- `1` : Erreur (dossier inexistant, JSON invalide, aucun clip traité, erreur FFmpeg)

## Dépannage

### Erreur: "FFmpeg n'est pas installé ou n'est pas dans le PATH"

**Symptômes:**
```
❌ ERREUR: FFmpeg n'est pas installé ou n'est pas dans le PATH
```

**Solutions:**
1. Installez FFmpeg selon les instructions ci-dessus
2. Vérifiez que FFmpeg est dans votre PATH:
   - Ouvrez un nouveau terminal/PowerShell
   - Tapez `ffmpeg -version`
   - Si cela ne fonctionne pas, redémarrez votre terminal après l'installation

**Windows:** Après avoir ajouté FFmpeg au PATH, redémarrez PowerShell/CMD

### Erreur: "Le fichier spécifié est introuvable"

Si vous voyez `[WinError 2] Le fichier spécifié est introuvable`, cela signifie que FFmpeg n'est pas trouvé. Suivez les étapes ci-dessus.

### Les clips ne sont pas trouvés

Vérifiez que:
1. Le chemin du dossier est correct
2. Les fichiers MP4 sont nommés avec leur ID (ex: `DifferentFitTroutCoolStoryBob-5TixTPM58R2gfWCu.mp4`)
3. Les IDs dans le JSON correspondent aux noms des fichiers MP4

### Problèmes de font sur Windows

Si vous rencontrez des erreurs liées aux fonts:
1. Le script utilise par défaut `C:\Windows\Fonts\arial.ttf`
2. Vérifiez que cette font existe sur votre système
3. Si nécessaire, le chemin est automatiquement détecté selon votre OS
