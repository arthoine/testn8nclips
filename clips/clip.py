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

        # Design futuriste style Valorant/Cyberpunk avec formes angulaires
        alpha_expr = f"if(lt(t,{fade_in}),t/{fade_in},if(gt(t,{fade_out}),({display_duration}-t)/0.5,1))"

        overlay_filter = (
            # === COUCHE 1: GLOW EXTERNE (Halo néon rose/violet) ===
            f"drawbox=x=25:y=25:w=500:h=90:color=#FF006E@0.15:t=fill:enable='between(t,0,{display_duration})',"

            # === COUCHE 2: FOND PRINCIPAL SOMBRE (Base overlay) ===
            f"drawbox=x=30:y=30:w=490:h=80:color=#0D0221@0.85:t=fill:enable='between(t,0,{display_duration})',"

            # === COUCHE 3: BANDE VIOLETTE DÉGRADÉE (Élément principal) ===
            # Partie gauche plus intense
            f"drawbox=x=35:y=35:w=150:h=70:color=#A637F5@0.9:t=fill:enable='between(t,0,{display_duration})',"
            # Partie centrale transition
            f"drawbox=x=185:y=35:w=150:h=70:color=#A637F5@0.6:t=fill:enable='between(t,0,{display_duration})',"
            # Partie droite fade out
            f"drawbox=x=335:y=35:w=180:h=70:color=#A637F5@0.2:t=fill:enable='between(t,0,{display_duration})',"

            # === COUCHE 4: ACCENT NÉON BLEU (Ligne supérieure) ===
            f"drawbox=x=35:y=35:w=480:h=3:color=#46C4F4@1.0:t=fill:enable='between(t,0,{display_duration})',"
            # Glow de la ligne bleue
            f"drawbox=x=35:y=32:w=480:h=9:color=#46C4F4@0.3:t=fill:enable='between(t,0,{display_duration})',"

            # === COUCHE 5: LIGNE ROSE NÉON (Ligne inférieure) ===
            f"drawbox=x=35:y=102:w=400:h=3:color=#FF006E@0.9:t=fill:enable='between(t,0,{display_duration})',"
            # Glow de la ligne rose
            f"drawbox=x=35:y=100:w=400:h=7:color=#FF006E@0.25:t=fill:enable='between(t,0,{display_duration})',"

            # === COUCHE 6: BORDURE GAUCHE ACCENT (Style Valorant) ===
            f"drawbox=x=30:y=30:w=5:h=80:color=#46C4F4@1.0:t=fill:enable='between(t,0,{display_duration})',"
            # Glow bordure
            f"drawbox=x=27:y=30:w=11:h=80:color=#46C4F4@0.4:t=fill:enable='between(t,0,{display_duration})',"

            # === COUCHE 7: PETITS ACCENTS DÉCORATIFS (Détails cyberpunk) ===
            # Point lumineux haut gauche
            f"drawbox=x=35:y=40:w=6:h=6:color=#FFFFFF@0.9:t=fill:enable='between(t,0,{display_duration})',"
            f"drawbox=x=33:y=38:w=10:h=10:color=#FFFFFF@0.2:t=fill:enable='between(t,0,{display_duration})',"
            # Point lumineux bas gauche
            f"drawbox=x=35:y=95:w=4:h=4:color=#FF006E@0.9:t=fill:enable='between(t,0,{display_duration})',"

            # === COUCHE 8: TEXTE STREAMER (Typographie futuriste) ===
            f"drawtext=text='{streamer_name}':"
            f"fontfile={font_path}:"
            f"fontsize=48:"
            f"fontcolor=#FFFFFF:"
            f"x=55:y=52:"
            # Glow cyan intense
            f"shadowcolor=#46C4F4@0.9:"
            f"shadowx=0:shadowy=0:"
            # Contour sombre pour contraste
            f"bordercolor=#000000@0.6:"
            f"borderw=2:"
            f"enable='between(t,0,{display_duration})':"
            f"alpha='{alpha_expr}'"
        )

        # Commande FFmpeg avec normalisation pour assurer la compatibilité
        cmd = [
            'ffmpeg', '-i', str(input_file),
            '-vf', overlay_filter,
            # Normaliser la vidéo pour la concaténation
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-r', '30',  # Forcer 30 FPS
            '-pix_fmt', 'yuv420p',  # Format de pixel standard
            # Audio
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',  # 48kHz sample rate
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
    print('⚙️ Réencodage et fusion des clips (peut prendre quelques minutes)...')

    # Concaténer tous les clips avec réencodage pour assurer la compatibilité
    output_file = output_folder / 'compilation_finale.mp4'
    concat_cmd = [
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', str(concat_file),
        # Réencoder pour garantir la compatibilité
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-r', '30',  # 30 FPS
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
        '-movflags', '+faststart',  # Optimisation pour lecture web
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
