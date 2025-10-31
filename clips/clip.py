import subprocess
import json
import sys
import argparse
import shutil
from pathlib import Path

def check_ffmpeg():
    """Vérifie si FFmpeg est installé et accessible"""
    if shutil.which('ffmpeg') is None:
        print('❌ ERREUR: FFmpeg n\'est pas installé ou n\'est pas dans le PATH')
        print('\n📥 Pour installer FFmpeg:')
        print('   Windows: https://www.ffmpeg.org/download.html')
        print('            ou utilisez: winget install ffmpeg')
        print('   Linux:   sudo apt install ffmpeg (Debian/Ubuntu)')
        print('            sudo dnf install ffmpeg (Fedora)')
        print('   macOS:   brew install ffmpeg')
        print('\n💡 Assurez-vous que FFmpeg est dans votre PATH après installation')
        sys.exit(1)

    # Vérifier la version de FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        version_line = result.stdout.split('\n')[0]
        print(f'✅ FFmpeg détecté: {version_line}')
    except Exception as e:
        print(f'⚠️ FFmpeg trouvé mais erreur lors de la vérification de la version: {e}')

def main():
    # Parser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description='Compiler des clips Twitch en une vidéo unique')
    parser.add_argument('clips_path', type=str, help='Chemin du dossier contenant les clips MP4')
    parser.add_argument('--json', '-j', type=str, help='Chemin du fichier JSON (par défaut: clips_data.json dans le dossier des clips)')

    args = parser.parse_args()

    # Vérifier FFmpeg avant tout
    check_ffmpeg()

    # Définir les chemins
    output_folder = Path(args.clips_path)

    if not output_folder.exists():
        print(f'❌ Erreur: Le dossier {output_folder} n\'existe pas')
        sys.exit(1)

    # Déterminer le fichier JSON
    if args.json:
        json_file = Path(args.json)
    else:
        json_file = output_folder / 'clips_data.json'

    if not json_file.exists():
        print(f'❌ Erreur: Le fichier JSON {json_file} n\'existe pas')
        sys.exit(1)

    # Charger les métadonnées des clips
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    clips = json_data['clips']
    print(f'\n🎬 Compilation de {len(clips)} clips...')

    # Créer le dossier temporaire
    temp_folder = output_folder / 'temp_processed'
    temp_folder.mkdir(exist_ok=True)

    # Détecter le chemin de la font selon le système
    import platform
    if platform.system() == 'Windows':
        font_path = '/Windows/Fonts/arial.ttf'
    else:
        # Linux: essayer plusieurs chemins possibles
        possible_fonts = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/TTF/DejaVuSans.ttf'
        ]
        font_path = None
        for font in possible_fonts:
            if Path(font).exists():
                font_path = font
                break
        if not font_path:
            print('⚠️ Aucune font trouvée, utilisation de la font par défaut')
            font_path = 'sans'  # Font par défaut de FFmpeg

    # Traiter chaque clip avec overlay
    processed_clips = []
    for idx, clip in enumerate(clips, 1):
        print(f'[{idx}/{len(clips)}] {clip["broadcaster_name"]}...')

        input_file = output_folder / f"{clip['id']}.mp4"
        temp_output = temp_folder / f"clip_{idx:03d}_processed.mp4"

        # Vérifier que le fichier d'entrée existe
        if not input_file.exists():
            print(f'⚠️ Fichier manquant: {input_file}')
            continue

        # Créer le filtre d'overlay avec échappement correct
        streamer_name = clip['broadcaster_name'].replace("'", "'\\\\\\'").replace(':', '\\\\:')
        display_duration = min(6.0, clip['duration'])
        fade_in = 0.3
        fade_out = max(0.5, display_duration - 0.5)

        overlay_filter = (
            f"drawtext=text='{streamer_name}':"
            f"fontfile={font_path}:"
            f"fontsize=56:"
            f"fontcolor=#0080FF:"
            f"bordercolor=#FFFFFF:"
            f"borderw=3:"
            f"x=40:y=40:"
            f"box=1:"
            f"boxcolor=black@0.8:"
            f"boxborderw=20:"
            f"enable='between(t,0,{display_duration})':"
            f"alpha='if(lt(t,{fade_in}),t/{fade_in},if(gt(t,{fade_out}),({display_duration}-t)/0.5,1))'"
        )

        # Commande FFmpeg
        cmd = [
            'ffmpeg', '-i', str(input_file),
            '-vf', overlay_filter,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k',
            '-y', str(temp_output)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
            processed_clips.append(str(temp_output))
        except FileNotFoundError:
            print(f'❌ FFmpeg introuvable - Vérifiez votre installation')
            print(f'   Commande tentée: {" ".join(cmd[:3])}...')
            sys.exit(1)
        except subprocess.TimeoutExpired:
            print(f'⏱️ Timeout dépassé pour {clip["id"]}')
            continue
        except subprocess.CalledProcessError as e:
            print(f'❌ Erreur FFmpeg pour {clip["id"]}:')
            if e.stderr:
                # Afficher les dernières lignes de l'erreur FFmpeg
                error_lines = e.stderr.strip().split('\n')
                for line in error_lines[-5:]:
                    print(f'   {line}')
            continue
        except Exception as e:
            print(f'❌ Erreur inattendue pour {clip["id"]}: {type(e).__name__} - {e}')
            continue

    print(f'\n✅ {len(processed_clips)} clips traités avec succès')

    if len(processed_clips) == 0:
        print(f'❌ Aucun clip n\'a pu être traité sur {len(clips)} clips')
        sys.exit(1)

    # Créer le fichier de concaténation
    concat_file = temp_folder / 'concat_list.txt'
    with open(concat_file, 'w', encoding='utf-8') as f:
        for clip_path in processed_clips:
            # Échapper les backslashes pour FFmpeg
            escaped_path = clip_path.replace('\\', '/')
            f.write(f"file '{escaped_path}'\n")

    print('\n🎞️ Assemblage final...')

    # Concaténer tous les clips
    output_file = output_folder / 'compilation_finale.mp4'
    concat_cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        '-y', str(output_file)
    ]

    try:
        result = subprocess.run(concat_cmd, capture_output=True, text=True, check=True, timeout=600)
        print(f'\n🎉 COMPILATION TERMINÉE!')
        print(f'📹 Fichier de sortie: {output_file}')
        print(f'📊 Stats: {len(processed_clips)}/{len(clips)} clips traités')

        # Afficher la durée totale si disponible dans les métadonnées
        if 'metadata' in json_data and 'total_duration' in json_data['metadata']:
            print(f'⏱️ Durée totale: {json_data["metadata"]["total_duration"]}')

        sys.exit(0)
    except FileNotFoundError:
        print(f'❌ FFmpeg introuvable lors de la concaténation')
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f'❌ Erreur lors de la concaténation finale:')
        if e.stderr:
            error_lines = e.stderr.strip().split('\n')
            for line in error_lines[-5:]:
                print(f'   {line}')
        print(f'📊 {len(processed_clips)}/{len(clips)} clips ont été traités avant l\'erreur')
        sys.exit(1)
    except Exception as e:
        print(f'❌ Erreur inattendue: {type(e).__name__} - {e}')
        print(f'📊 {len(processed_clips)}/{len(clips)} clips ont été traités avant l\'erreur')
        sys.exit(1)


if __name__ == '__main__':
    main()
