import os
import subprocess
import re
from faster_whisper import WhisperModel

def run_processing_pipeline(video_source, vo_path, bg_path, output_path):
    """
    Heavy-duty processing engine. Executed via Google Colab GPU environment.
    """
    workspace_dir = "workspace"
    os.makedirs(workspace_dir, exist_ok=True)
    
    raw_vid = os.path.join(workspace_dir, "raw.mp4")
    mixed_audio = os.path.join(workspace_dir, "mixed.mp3")
    ass_subs = os.path.join(workspace_dir, "subs.ass")

    # Clean up leftovers from previous processing cycles
    for f in [raw_vid, mixed_audio, ass_subs, output_path]:
        if os.path.exists(f): 
            os.remove(f)

    # --- STEP 1: DETECT MATERIAL SOURCE AND CAPTURE VIDEO ---
    if os.path.exists(video_source):
        # User uploaded a file directly from local manager
        raw_vid = video_source
    else:
        # User passed a web URL string, activate extraction
        import yt_dlp
        ydl_opts = {
            'format': 'best',
            'outtmpl': raw_vid,
            'overwrites': True,
            'quiet': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_source])

    # --- STEP 2: TRACK AUDIO TIMEFRAMES ---
    cmd_dur = [
        "ffprobe", "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        vo_path
    ]
    vo_duration = float(subprocess.run(cmd_dur, check=True, capture_output=True, text=True).stdout.strip())

    # --- STEP 3: DUCK BACKGROUND AUDIO TRACKS TO 7% ---
    cmd_mix = [
        "ffmpeg", "-y", "-i", vo_path, "-i", bg_path,
        "-filter_complex", "[1:a]volume=0.07[bg];[0:a][bg]amix=inputs=2:duration=first[a]",
        "-map", "[a]", mixed_audio
    ]
    subprocess.run(cmd_mix, check=True, capture_output=True)

    # --- STEP 4: SPEECH TRANSCRIPTION TO MULTI-COLOR WORD ENGINE ---
    # Loads model onto Google Colab GPU device context automatically for fast processing
    model = WhisperModel("tiny", device="cuda", compute_type="float16")
    segments, info = model.transcribe(vo_path, word_timestamps=True)
    
    colors = [
        "&H00FFFFFF",  # Pure White
        "&H0000FFFF",  # Bright Yellow
        "&H0000FF00",  # Neon Green
        "&H000000FF",  # Red
        "&H00FF00FF"   # Pink
    ]
    
    with open(ass_subs, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n")
        f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        # Alignment 2 centered text, MarginV 960 positions captions perfectly within safe viewer frames
        f.write("Style: KaraokeText,Impact,90,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,2,2,10,10,960,1\n\n")
        f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        
        color_idx = 0
        for segment in segments:
            for word in segment.words:
                start_time = f"0:{int(word.start//60)}:{int(word.start%60):02d}.{int((word.start%1)*100):02d}"
                end_time = f"0:{int(word.end//60)}:{int(word.end%60):02d}.{int((word.end%1)*100):02d}"
                clean_txt = word.word.strip().upper()
                
                chosen_color = colors[color_idx % len(colors)]
                color_idx += 1
                
                f.write(f"Dialogue: 0,{start_time},{end_time},KaraokeText,,0,0,0,,{{\\c{chosen_color}}}{clean_txt}\n")

    # --- STEP 5: RENDERING TRANSFORMATIONS AND TIMELINE CUTOFF ---
    clean_ass = ass_subs.replace("\\", "/")
    cmd_render = [
        "ffmpeg", "-y", "-i", raw_vid, "-i", mixed_audio,
        "-vf", f"eq=gamma=1.04:saturation=1.1,ass='{clean_ass}'",
        "-map", "0:v", "-map", "1:a",
        "-t", str(vo_duration),  # Strict rule: Stops rendering the exact millisecond the voice track ends
        "-c:v", "h264_nvenc", "-preset", "p4",  # Uses high-speed GPU compilation layer
        "-c:a", "aac", "-b:a", "192k",
        "-map_metadata", "-1",  # Strips away tracking data tags entirely
        output_path
    ]
    subprocess.run(cmd_render, check=True, capture_output=True)
    return True
