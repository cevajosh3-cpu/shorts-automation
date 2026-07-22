import subprocess

def get_audio_duration(audio_path):
    """Finds the exact length of the voiceover down to the millisecond."""
    cmd = [
        "ffprobe", "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        audio_path
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return float(result.stdout.strip())

def mix_audio_tracks(vo_path, bg_path, output_path):
    """Mixes voiceover at 100% and background music ducked down to 7%."""
    cmd = [
        "ffmpeg", "-y", "-i", vo_path, "-i", bg_path,
        "-filter_complex", "[1:a]volume=0.07[bg];[0:a][bg]amix=inputs=2:duration=first[a]",
        "-map", "[a]", output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return True
