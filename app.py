import streamlit as st
import os
import subprocess

# Try loading faster-whisper gracefully without crashing the web app
try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

st.set_page_config(page_title="AI Shorts Processor", layout="centered")

st.title("🎬 AI Shorts Automation Dashboard")
st.write("Upload your files below to clean video text, mix audio, and generate word-by-word colorful captions.")
st.markdown("---")

st.subheader("1. Input Materials")
youtube_url = st.text_input("Paste YouTube Shorts URL Here:", placeholder="https://www.youtube.com/shorts/...")
voiceover_file = st.file_uploader("Upload New Voiceover (MP3/WAV):", type=["mp3", "wav"])
music_file = st.file_uploader("Upload Background Music (MP3/WAV):", type=["mp3", "wav"])

st.markdown("---")

if st.button("🚀 START FULL AUTO-PROCESS", type="primary"):
    if not youtube_url or not voiceover_file or not music_file:
        st.error("Please fill in the YouTube link and upload BOTH audio files first!")
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

            # Save uploaded audio streams
            with open(vo_path, "wb") as f: 
                f.write(voiceover_file.getbuffer())
            with open(bg_path, "wb") as f: 
                f.write(music_file.getbuffer())

            # --- STEP 1: DOWNLOAD RAW YOUTUBE SHORT ---
            status.info("⏳ Downloading video from YouTube safely...")
            # Using standard standalone format selection to avoid cloud server streaming errors
            cmd_dl = [
                "yt-dlp", 
                "-f", "best", 
                "--force-overwrites", 
                "-o", raw_vid, 
                youtube_url
            ]
            subprocess.run(cmd_dl, check=True, capture_output=True)

            # --- STEP 2: MEASURE VOICE LENGTH ---
            status.info("⏳ Analyzing your voiceover track length...")
            cmd_dur = [
                "ffprobe", "-v", "error", 
                "-show_entries", "format=duration", 
                "-of", "default=noprint_wrappers=1:nokey=1", 
                vo_path
            ]
            vo_duration = float(subprocess.run(cmd_dur, check=True, capture_output=True, text=True).stdout.strip())

            # --- STEP 3: AUDIO DUCKING MIX ---
            status.info("⏳ Mixing sound (VO at 100% / BG Music down by 80%)...")
            cmd_mix = [
                "ffmpeg", "-y", "-i", vo_path, "-i", bg_path,
                "-filter_complex", "[1:a]volume=0.20[bg];[0:a][bg]amix=inputs=2:duration=first[a]",
                "-map", "[a]", mixed_audio
            ]
            subprocess.run(cmd_mix, check=True, capture_output=True)

            # --- STEP 4: WORD-LEVEL TIMESTAMPS VIA WHISPER ---
            status.info("⏳ AI Engine transcribing speech word-by-word...")
            model = WhisperModel("tiny", device="cpu", compute_type="int8")
            segments, info = model.transcribe(vo_path, word_timestamps=True)
            
            # --- STEP 5: GENERATE DYNAMIC KARAOKE STYLES (ASS) ---
            status.info("⏳ Generating colorful word-by-word visual layout...")
            with open(ass_subs, "w", encoding="utf-8") as f:
                f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n")
                f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
                # Default text color is Pink (&HBB00FF), active karaoke highlighting color is Yellow (&H00FFFF)
                f.write("Style: Karaoke,Arial,65,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,0,2,10,10,960,1\n\n")
                f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
                
                for segment in segments:
                    for word in segment.words:
                        start_time = f"0:{int(word.start//60)}:{int(word.start%60):02d}.{int((word.start%1)*100):02d}"
                        end_time = f"0:{int(word.end//60)}:{int(word.end%60):02d}.{int((word.end%1)*100):02d}"
                        clean_word = word.word.strip().upper()
                        # Advanced Substation Karaoke timing structure (\k duration in centiseconds)
                        duration_cs = int((word.end - word.start) * 100)
                        f.write(f"Dialogue: 0,{start_time},{end_time},Karaoke,,0,0,0,,{{\\k{duration_cs}}}{clean_word}\n")

            # --- STEP 6: COMPILE EVERYTHING INTO COMPRESSED VIDEO ---
            status.info("⏳ Cleaning footage, cutting to length, and burning captions...")
            # Automatically crops 150px off top/bottom to clean text margins, replaces audio streams, cuts timeline at audio end
            cmd_render = [
                "ffmpeg", "-y", "-i", raw_vid, "-i", mixed_audio,
                "-filter_complex", f"[0:v]crop=in_w:in_h-300:0:150,ass={ass_subs}[v]",
                "-map", "[v]", "-map", "1:a",
                "-t", str(vo_duration),  # Crucial master instruction: cuts video right when voiceover stops
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k", final_output
            ]
            subprocess.run(cmd_render, check=True, capture_output=True)

            status.success("🎉 Video completed successfully!")
            
            # --- STEP 7: HAND OVER THE COMPLETED ASSET ---
            st.subheader("2. Final Result")
            with open(final_output, "rb") as file:
                st.video(file.read())
                st.download_button(
                    label="⬇️ Download Finished Short Instantly",
                    data=file,
                    file_name="Automated_Short.mp4",
                    mime="video/mp4"
                )

        except Exception as error:
            st.error(f"A processing breakdown occurred: {error}")

st.markdown("---")
