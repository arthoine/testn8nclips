#!/usr/bin/env python3
"""
Script de secours pour fusionner les clips déjà traités
Utilise un réencodage complet pour garantir la compatibilité (plus lent mais plus sûr)
"""
import subprocess
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python merge_clips_safe.py <dossier_temp_processed>")
        print("Exemple: python merge_clips_safe.py J:\\twitch_clips\\clip_xxx\\temp_processed")
        sys.exit(1)

    temp_folder = Path(sys.argv[1])

    if not temp_folder.exists():
        print(f"❌ Dossier introuvable: {temp_folder}")
        sys.exit(1)

    # Trouver tous les clips traités
    clips = sorted(temp_folder.glob("clip_*.mp4"))

    if not clips:
        print(f"❌ Aucun clip trouvé dans {temp_folder}")
        sys.exit(1)

    print(f"📁 Trouvé {len(clips)} clips à fusionner")

    # Créer le fichier de concaténation
    concat_file = temp_folder / 'concat_list_safe.txt'
    with open(concat_file, 'w', encoding='utf-8') as f:
        for clip in clips:
            escaped_path = str(clip).replace('\\', '/')
            f.write(f"file '{escaped_path}'\n")

    # Fichier de sortie
    output_file = temp_folder.parent / 'compilation_finale_safe.mp4'

    print(f'\n🎞️ Fusion avec réencodage complet (LENT mais SÛR)...')
    print(f'⏱️ Cela peut prendre 10-20 minutes pour {len(clips)} clips...')

    # Commande FFmpeg avec réencodage complet (HEVC -> H.264 si nécessaire)
    cmd = [
        'ffmpeg',
        '-hwaccel', 'auto',  # Accélération matérielle
        '-f', 'concat', '-safe', '0',
        '-i', str(concat_file),
        # Réencodage complet en H.264
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-profile:v', 'high',  # Profile H.264 compatible
        '-level', '4.0',
        '-r', '30',
        '-vsync', 'cfr',  # Constant Frame Rate
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2',
        '-movflags', '+faststart',
        '-max_muxing_queue_size', '1024',
        '-y', str(output_file)
    ]

    print(f'\n📋 Commande FFmpeg:')
    print(' '.join(cmd))
    print()

    try:
        # Lancer FFmpeg avec affichage en temps réel
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=1800  # 30 minutes max
        )

        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f'\n🎉 FUSION TERMINÉE!')
            print(f'📹 Fichier de sortie: {output_file}')
            print(f'📊 Taille: {file_size / (1024*1024):.1f} MB')
        else:
            print('❌ Le fichier de sortie n\'a pas été créé')
            sys.exit(1)

    except subprocess.TimeoutExpired:
        print('❌ Timeout dépassé (30 minutes)')
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print('❌ Erreur FFmpeg:')
        if e.stderr:
            print(e.stderr[-1000:])
        sys.exit(1)
    except Exception as e:
        print(f'❌ Erreur: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
