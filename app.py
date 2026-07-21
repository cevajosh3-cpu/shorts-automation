import streamlit as st
import os
import subprocess

# Try loading faster-whisper gracefully without crashing the web app
try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

st.set_page_config(page_title="AI Shorts Processor Pro", layout="centered")

st.title("🎬 AI Shorts Automation Dashboard")
st.write("Upload your files below to fully clean footage, balance audio, and generate colorful YouTube Shorts compliant captions.")
st.markdown("---")

st.subheader("1. Input Materials")
raw_video_file = st.file_uploader("Upload Original Short Video (MP4):", type=["mp4", "mov"])
voiceover_file = st.file_uploader("Upload New Voiceover (MP3/WAV):", type=["mp3", "wav"])
music_file = st.file_uploader("Upload Background Music (MP3/WAV):", type=["mp3", "wav"])

st.markdown("---")

if st.button("🚀 START FULL AUTO-PROCESS", type="primary"):
    if not raw_video_file or not voiceover_file or not music_file:
        st.error("Please upload ALL three files (Video, Voiceover, and Background Music) first!")
    elif WhisperModel is None:
        st.error("System configuration error: AI Caption Engine failed to load. Check requirements.txt.")
    else:
        status = st.empty()
        
        # Create work directories safely
        os.makedirs("workspace", exist_ok=True)
        raw_vid = "workspace/raw.mp4"
        vo_path = "workspace/vo.mp3"
        bg_path = "workspace/bg.mp3"
        mixed_audio = "workspace/mixed.mp3"
        ass_subs = "workspace/subs.ass"
        final_output = "workspace/final_render.mp4"

        try:
            # Clean up old files from previous runs
            for f in [raw_vid, vo_path, bg_path, mixed_audio, ass_subs, final_output]:
                if os.path.exists(f): 
                    os.remove(f)

            # Save uploaded streams locally on the server filesystem
            with open(raw_vid, "wb") as f:
                f.write(raw_video_file.getbuffer())
            with open(vo_path, "wb") as f: 
                f.write(voiceover_file.getbuffer())
            with open(bg_path, "wb") as f: 
                f.write(music_file.getbuffer())

            # --- STEP 1: MEASURE VOICE LENGTH ---
            status.info("⏳ Analyzing your voiceover track length...")
            cmd_dur = [
                "ffprobe", "-v", "error", 
                "-show_entries", "format=duration", 
                "-of", "default=noprint_wrappers=1:nokey=1", 
                vo_path
            ]
            vo_duration = float(subprocess.run(cmd_dur, check=True, capture_output=True, text=True).stdout.strip())

            # --- STEP 2: AUDIO BALANCE (DUCKING BACKGROUND MUSIC UP TO 7%) ---
            status.info("⏳ Advanced Audio Mixing (VO Dominant / Background Music Ducked to 7%)...")
            cmd_mix = [
                "ffmpeg", "-y", "-i", vo_path, "-i", bg_path,
                "-filter_complex", "[1:a]volume=0.07[bg];[0:a][bg]amix=inputs=2:duration=first[a]",
                "-map", "[a]", mixed_audio
            ]
            subprocess.run(cmd_mix, check=True, capture_output=True)

            # --- STEP 3: WORD-LEVEL TIMESTAMPS VIA WHISPER ---
            status.info("⏳ AI Engine transcribing speech word-by-word...")
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, info = model.transcribe(vo_path, word_timestamps=True)
            
            # --- STEP 4: GENERATE SHORTS COMPLIANT MULTI-COLOR REVOLVING CAPTIONS (ASS) ---
            status.info("⏳ Designing YouTube Shorts safe-zone colorful captions...")
            
            # Subtitle styling colors in hex format (AABBGGRR)
            colors = [
                "&H00FFFFFF",  # Pure White
                "&H0000FFFF",  # Bright Yellow
                "&H0000FF00",  # Neon Green
                "&H000000FF",  # Red
                "&H00FF80FF"   # Pink
            ]
            
            with open(ass_subs, "w", encoding="utf-8") as f:
                f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n")
                f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
                # Base layout font configuration. Alignment 2 (Bottom Center), MarginV 820 pushes it perfectly up into the middle safe zone
                f.write("Style: MultiColor,Impact,80,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,2,2,10,10,820,1\n\n")
                f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
                
                color_index = 0
                for segment in segments:
                    for word in segment.words:
                        start_time = f"0:{int(word.start//60)}:{int(word.start%60):02d}.{int((word.start%1)*100):02d}"
                        end_time = f"0:{int(word.end//60)}:{int(word.end%60):02d}.{int((word.end%1)*100):02d}"
                        clean_word = word.word.strip().upper()
                        
                        # Apply revolving color profile per word entry
                        chosen_color = colors[color_index % len(colors)]
                        color_index += 1
                        
                        f.write(f"Dialogue: 0,{start_time},{end_time},MultiColor,,0,0,0,,{{\\c{chosen_color}}}{clean_word}\n")

            # --- STEP 5: 10-STEP ANTI-COPYRIGHT RENDERING PIPELINE ---
            status.info("⏳ Running full anti-copyright processing layers...")
            
            # FIXED MATH: Simplified scale logic syntax prevents server engine parsing breaks completely
            video_filters = (
                "crop=in_w:in_h-300:0:150,"
                "scale=1.02*iw:1.02*ih,"
                "eq=gamma=1.05:saturation=1.1,"
                "fps=30,"
                "ass=workspace/subs.ass"
            )
            
            cmd_render = [
                "ffmpeg", "-y", "-i", raw_vid, "-i", mixed_audio,
                "-filter_complex", f"[0:v]{video_filters}[v]",
                "-map", "[v]", "-map", "1:a",
                "-t", str(vo_duration),  # Strict timing rule: Cuts the file exactly when voice track finishes
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                "-map_metadata", "-1",  # Wipes out all original metadata streams completely
                final_output
            ]
            subprocess.run(cmd_render, check=True, capture_output=True)

            status.success("🎉 Video processing and cleaning complete!")
            
            # --- STEP 6: HAND OVER THE COMPLETED ASSET AND DOWNLOAD INTERFACE ---
            st.subheader("2. Final Result")
            with open(final_output, "rb") as file:
                video_bytes = file.read()
                st.video(video_bytes)
                
                # Big full-width instant download button
                st.download_button(
                    label="⬇️ Download Finished Short Instantly",
                    data=video_bytes,
                    file_name="Cleaned_AI_Short.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

        except Exception as error:
            st.error(f"A processing breakdown occurred: {error}")

st.markdown("---")
