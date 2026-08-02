import os
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from faster_whisper import WhisperModel

def crop_to_vertical(clip):
    """Crops a standard 16:9 video to 9:16 vertical format (center crop)."""
    w, h = clip.size
    target_ratio = 9 / 16
    
    # If the video is already vertical or close to it, just return
    if w / h <= target_ratio + 0.1:
        return clip
        
    target_w = int(h * target_ratio)
    x_center = w / 2
    
    # crop(x1, y1, x2, y2)
    return clip.crop(x1=x_center - target_w/2, y1=0, x2=x_center + target_w/2, y2=h)

def create_captions(audio_path):
    """
    Uses faster-whisper to generate short phrase-level timestamps (max 4 words).
    """
    print("Generating chunked captions with whisper...")
    # Use CPU by default to ensure it works everywhere, but int8 is fast
    model = WhisperModel("base", device="cpu", compute_type="int8")
    
    segments, info = model.transcribe(audio_path, word_timestamps=True)
    
    phrases = []
    chunk_size = 4 # Maximum words to show on screen at once
    
    for segment in segments:
        words = segment.words
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i+chunk_size]
            text = " ".join([w.word.strip() for w in chunk])
            phrases.append({
                "text": text,
                "start": chunk[0].start,
                "end": chunk[-1].end
            })
            
    return phrases

def create_text_image(text, font_size, max_width, max_height):
    """Creates a transparent image with wrapped text using Pillow."""
    try:
        font = ImageFont.truetype("impact.ttf", font_size)
    except IOError:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # Fallbacks for Linux
            linux_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf"
            ]
            font_loaded = False
            for lf in linux_fonts:
                if os.path.exists(lf):
                    font = ImageFont.truetype(lf, font_size)
                    font_loaded = True
                    break
            
            if not font_loaded:
                # If all else fails, use the default bitmap font (which will be tiny)
                print("WARNING: No TTF fonts found! Subtitles will be very small. Install fonts to fix this.")
                font = ImageFont.load_default()

    # Create dummy image to calculate text wrapping
    dummy_img = Image.new('RGBA', (1, 1))
    d = ImageDraw.Draw(dummy_img)
            
    # Wrap text manually
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = d.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
        
    wrapped_text = "\n".join(lines)
    
    # Calculate bounding box of the multiline text
    bbox = d.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Make the image canvas large enough to hold all the lines
    target_h = max(max_height, text_h + 20)
    img = Image.new('RGBA', (max_width, target_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    # Center text in the image box
    x = (max_width - text_w) / 2
    y = (target_h - text_h) / 2
    
    # Modern highly readable styling (Hormozi style)
    text_color = "#FFFF00" # Punchy yellow
    stroke_color = "black"
    # Stroke should scale with font size to always be visible (about 6% of font size)
    stroke_w = max(3, font_size // 12)
    
    # Draw main text with thick stroke
    d.multiline_text(
        (x, y), 
        wrapped_text, 
        font=font, 
        fill=text_color, 
        align="center",
        stroke_width=stroke_w,
        stroke_fill=stroke_color
    )
    
    return np.array(img)

def edit_and_caption_video(input_path, start_time, end_time, output_path):
    """
    Clips, crops, transcribes, and overlays captions on the video.
    """
    video = VideoFileClip(input_path)
    
    # Clamp end_time to the actual video duration to prevent out-of-bounds errors
    if end_time > video.duration:
        end_time = video.duration
        
    print(f"Loading video from {start_time} to {end_time} (Total Duration: {video.duration}s)...")
    video = video.subclip(start_time, end_time)
    
    # 1. Crop to Vertical
    video = crop_to_vertical(video)
    
    # 2. Extract Audio for transcription
    temp_audio = "temp_audio.wav"
    video.audio.write_audiofile(temp_audio, logger=None)
    
    # 3. Get Word-level timestamps
    words_data = create_captions(temp_audio)
    
    # 4. Create Text Clips for each word using Pillow
    print("Generating caption overlays (no ImageMagick required)...")
    w, h = video.size
    font_size = int(w * 0.18) # 18% width for huge, highly readable text
    
    subtitle_clips = []
    for word_info in words_data:
        start = word_info['start']
        end = word_info['end']
        duration = end - start
        
        # Ensure a minimum duration so it doesn't flicker too fast
        if duration < 0.1:
            duration = 0.1
            
        try:
            # Generate image with text using Pillow
            text_img = create_text_image(
                word_info['text'].upper(), # ALL CAPS for readability
                font_size, 
                int(w * 0.9), # Allow 90% width
                int(font_size * 3)
            )
            
            # Create an ImageClip from the numpy array
            txt_clip = ImageClip(text_img).set_duration(duration)
            
            # Position it at the center-bottom
            txt_clip = txt_clip.set_position(('center', h*0.7))
            txt_clip = txt_clip.set_start(start)
            
            subtitle_clips.append(txt_clip)
        except Exception as e:
            print(f"Failed to create TextClip for word '{word_info['text']}'. Error: {e}")
            break
            
    # 5. Composite video and subtitles
    if subtitle_clips:
        final_video = CompositeVideoClip([video] + subtitle_clips)
    else:
        final_video = video
        
    print(f"Exporting final reel to {output_path}...")
    # Fast rendering settings
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        fps=30,
        logger="bar", # Enable progress bar so it doesn't look stuck
        threads=1,
        preset="ultrafast"
    )
    
    # Cleanup
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
        
    video.close()
    if subtitle_clips:
        final_video.close()

if __name__ == "__main__":
    pass
