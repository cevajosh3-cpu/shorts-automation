from faster_whisper import WhisperModel

def generate_karaoke_captions(vo_path, ass_output_path):
    """Transcribes audio word-by-word and writes a multi-color ASS file."""
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, info = model.transcribe(vo_path, word_timestamps=True)
    
    colors = [
        "&H00FFFFFF",  # Pure White
        "&H0000FFFF",  # Bright Yellow
        "&H0000FF00",  # Neon Green
        "&H000000FF",  # Red
        "&H00FF80FF"   # Pink
    ]
    
    with open(ass_output_path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n")
        f.write("[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        # Impact Font, Alignment 2, MarginV 850 locks text in the safe center-middle zone of shorts
        f.write("Style: MultiColor,Impact,85,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,2,2,10,10,850,1\n\n")
        f.write("[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        
        color_index = 0
        for segment in segments:
            for word in segment.words:
                start_time = f"0:{int(word.start//60)}:{int(word.start%60):02d}.{int((word.start%1)*100):02d}"
                end_time = f"0:{int(word.end//60)}:{int(word.end%60):02d}.{int((word.end%1)*100):02d}"
                clean_word = word.word.strip().upper()
                
                chosen_color = colors[color_index % len(colors)]
                color_index += 1
                
                f.write(f"Dialogue: 0,{start_time},{end_time},MultiColor,,0,0,0,,{{\\c{chosen_color}}}{clean_word}\n")
    return True
