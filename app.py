import streamlit as st
import os

# Import our custom standalone tool modules
import downloader
import audio_mixer
import caption_engine
import video_compiler

st.set_page_config(page_title="AI Multi-Platform Shorts Engine", layout="centered")

st.title("🎬 AI Shorts Automation Dashboard")
st.write("Clean video text, balance audio, and generate colorful safe-zone captions via URL link or direct file manager upload.")
st.markdown("---")

st.subheader("1. Input Materials")

# --- HYBRID DUAL-INPUT DESIGN ---
st.write("👉 **Choose ONE method to provide your video footage:**")
youtube_url = st.text_input("Method A: Paste Link (YouTube, TikTok, Instagram, etc.):", placeholder="https://...")
raw_video_file = st.file_uploader("Method B: Or Upload Video File Directly (MP4/MOV):", type=["mp4", "mov"])

st.markdown("---")
st.write("👉 **Provide your replacement audio tracks:**")
voiceover_file = st.file_uploader("Upload New Voiceover (MP3/WAV):", type=["mp3", "wav"])
music_file = st.file_uploader("Upload Background Music (MP3/WAV):", type=["mp3", "wav"])

st.markdown("---")

if st.button("🚀 START FULL AUTO-PROCESS", type="primary"):
    # Enforce strict input checks
    if not youtube_url and not raw_video_file:
        st.error("Please paste a link OR upload a video file first!")
    elif not voiceover_file or not music_file:
        st.error("Please upload BOTH audio files (Voiceover and Background Music) first!")
    else:
        status = st.empty()
        
        # Build clean absolute workspace environments
        base_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_dir = os.path.join(base_dir, "workspace")
        os.makedirs(workspace_dir, exist_ok=True)
        
        raw_vid = os.path.join(workspace_dir, "raw.mp4")
        vo_path = os.path.join(workspace_dir, "vo.mp3")
        bg_path = os.path.join(workspace_dir, "bg.mp3")
        mixed_audio = os.path.join(workspace_dir, "mixed.mp3")
        ass_subs = os.path.join(workspace_dir, "subs.ass")
        final_output = os.path.join(workspace_dir, "final_render.mp4")

        try:
            # Refresh workspace and purge residual renders
            for f in [raw_vid, vo_path, bg_path, mixed_audio, ass_subs, final_output]:
                if os.path.exists(f): os.remove(f)

            # Instantly lock user audio tracks into server filesystem
            with open(vo_path, "wb") as f: f.write(voiceover_file.getbuffer())
            with open(bg_path, "wb") as f: f.write(music_file.getbuffer())

            # --- ROUTING STEP: DETECT INPUT MATERIAL METHOD ---
            if raw_video_file is not None:
                status.info("⏳ Processing your uploaded file manager video stream...")
                with open(raw_vid, "wb") as f: 
                    f.write(raw_video_file.getbuffer())
            else:
                status.info("⏳ Activating advanced multi-platform client bypass scraper...")
                download_success = downloader.download_youtube_short(youtube_url, raw_vid)
                if not download_success or not os.path.exists(raw_vid):
                    raise Exception("The web scraper client was blocked by the platform firewalls. Please upload the raw MP4 file directly using Method B.")

            # --- MODULE STEP 1: MEASURE TIMELINES ---
            status.info("⏳ Mapping audio track milestones...")
            vo_duration = audio_mixer.get_audio_duration(vo_path)

            # --- MODULE STEP 2: PROFESSIONAL MIXING ---
            status.info("⏳ Mixing balanced soundscapes (VO at 100% / BG Music at 7%)...")
            audio_mixer.mix_audio_tracks(vo_path, bg_path, mixed_audio)

            # --- MODULE STEP 3: SPEECH SPECTRUM TRANSCRIPTION ---
            status.info("⏳ AI Engine analyzing vocal tracks for word-level captions...")
            caption_engine.generate_karaoke_captions(vo_path, ass_subs)

            # --- MODULE STEP 4: ANTI-COPYRIGHT FILM TRANSFORMATION ---
            status.info("⏳ Slicing margins, modifying metadata, and burning dynamic captions...")
            video_compiler.compile_final_short(raw_vid, mixed_audio, ass_subs, vo_duration, final_output)

            status.success("🎉 Video processing and cleaning complete!")
            
            # --- OUTPUT AND DOWNLOAD DELIVERY LAYER ---
            st.subheader("2. Final Result")
            with open(final_output, "rb") as file:
                video_bytes = file.read()
                st.video(video_bytes)
                
                st.download_button(
                    label="⬇️ Download Finished Short Instantly",
                    data=video_bytes,
                    file_name="Automated_Clean_Short.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )

        except Exception as error:
            st.error(f"A processing breakdown occurred: {error}")

st.markdown("---")
