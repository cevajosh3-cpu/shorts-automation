import subprocess

def compile_final_short(raw_vid_path, mixed_audio_path, ass_subs_path, duration, output_path):
    """Executes the strict anti-copyright processing filter layers."""
    clean_ass_path = ass_subs_path.replace("\\", "/")
    
    # Strict asterisk math prevents exit status 187 breaks on cloud systems
    video_filters = (
        "crop=iw:ih-300:0:150,"
        "scale=1.02*iw:1.02*ih,"
        "eq=gamma=1.05:saturation=1.1,"
        "fps=30,"
        f"ass='{clean_ass_path}'"
    )
    
    cmd = [
        "ffmpeg", "-y", "-i", raw_vid_path, "-i", mixed_audio_path,
        "-filter_complex", f"[0:v]{video_filters}[v]",
        "-map", "[v]", "-map", "1:a",
        "-t", str(duration),  # Strict timing rule: chops video right when voiceover ends
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",  # Strips all original file tracking meta parameters
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return True
