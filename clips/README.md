# Script de Compilation de Clips Twitch

Ce script Python compile automatiquement plusieurs clips Twitch en une seule vidéo avec overlay du nom du streamer.

## Prérequis

- Python 3.6+
- FFmpeg installé et accessible dans le PATH

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
