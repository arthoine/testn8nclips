import subprocess
import json
from pathlib import Path

# Récupérer les données de l'input
data = $input.first().json

output_folder = Path(data['full_output_path'])
json_file = output_folder / 'clips_data.json'

# Charger les métadonnées des clips
with open(json_file, 'r', encoding='utf-8') as f:
    json_data = json.load(f)

clips = json_data['clips']
print(f'\n🎬 Compilation de {len(clips)} clips...')

# Créer le dossier temporaire
temp_folder = output_folder / 'temp_processed'
temp_folder.mkdir(exist_ok=True)

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
        f"fontfile=/Windows/Fonts/arial.ttf:"
        f"fontsize=32:"
        f"fontcolor=#9D4EDD:"
        f"bordercolor=#00D9FF:"
        f"borderw=2:"
        f"x=30:y=30:"
        f"box=1:"
        f"boxcolor=black@0.7:"
        f"boxborderw=8:"
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
    except subprocess.TimeoutExpired:
        print(f'⏱️ Timeout dépassé pour {clip["id"]}')
        continue
    except subprocess.CalledProcessError as e:
        print(f'❌ Erreur FFmpeg: {e.stderr[:200]}')
        continue
    except Exception as e:
        print(f'❌ Erreur inattendue: {e}')
        continue

print(f'\n✅ {len(processed_clips)} clips traités avec succès')

if len(processed_clips) == 0:
    return [{
        'status': 'error',
        'error': 'Aucun clip n\'a pu être traité',
        'clips_count': len(clips)
    }]

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
    print(f'📹 {output_file}')

    # Retourner les résultats en tant que LISTE
    return [{
        'status': 'success',
        'video_path': str(output_file),
        'clips_count': len(clips),
        'processed_clips': len(processed_clips),
        'duration': data['total_duration_formatted'],
        'message': f'Compilation créée avec succès: {len(processed_clips)}/{len(clips)} clips'
    }]
except subprocess.CalledProcessError as e:
    print(f'❌ Erreur concaténation: {e.stderr}')
    return [{
        'status': 'error',
        'error': f'Erreur concaténation: {e.stderr[:500]}',
        'clips_count': len(clips),
        'processed_clips': len(processed_clips)
    }]
except Exception as e:
    print(f'❌ Erreur: {e}')
    return [{
        'status': 'error',
        'error': str(e),
        'clips_count': len(clips),
        'processed_clips': len(processed_clips)
    }]
