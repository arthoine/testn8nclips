from decord import VideoReader, cpu
import os

video_path = r"J:\claude\clip.mp4"

if not os.path.exists(video_path):
    print(f"❌ Fichier non trouvé: {video_path}")
    exit(1)

try:
    vr = VideoReader(video_path, ctx=cpu(0))
    total_frames = len(vr)
    fps = vr.get_avg_fps()
    print(f"✅ Vidéo trouvée: {video_path}")
    print(f"   Total frames: {total_frames}")
    print(f"   FPS: {fps:.2f}")

    # Afficher quelques frames échantillonnées
    sample_indices = [0, min(5, total_frames-1), min(10, total_frames-1)]
    for idx in sample_indices:
        frame = vr[idx].asnumpy()
        print(f"   Frame {idx}: shape={frame.shape}, dtype={frame.dtype}")

except Exception as e:
    print(f"❌ Erreur lecture vidéo: {e}")
