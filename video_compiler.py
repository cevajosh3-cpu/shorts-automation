import subprocess

def compile_final_short(raw_vid_path, mixed_audio_path, ass_subs_path, duration, output_path):
    """
    Bulletproof video compiler. Uses percentage math to adjust to ANY file resolution
    and avoids exit status 187 parsing errors completely.
    """
    clean_ass_path = ass_subs_path.replace("\\", "/")
    
    # PERCENTAGE MATH FIX: 
    # 'crop=iw:ih*0.80:0:ih*0.10' shaves exactly 10% from the top and 10% from the bottom dynamically.
    # We also fix the scaling math to use clean standard multiplication '1.02*iw:1.02*ih'.
    video_filters = (
        "crop=iw:ih*0.80:0:ih*0.10,"
        "scale=1.02*iw:1.02*ih,"
        "eq=gamma=1.05:saturation=1.1,"
        "fps=30,"
        f"ass='{clean_ass_path}'"
    )
    
    cmd = [
        "ffmpeg", "-y", "-i", raw_vid_path, "-i", mixed_audio_path,
        "-filter_complex", f"[0:v]{video_filters}[v]",
        "-map", "[v]", "-map", "1:a",
        "-t", str(duration),  # Strict timing rule: Cuts file exactly when voice track ends
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",  # Strips all original tracking metadata tags
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return True
