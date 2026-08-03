import os
import json
import time
import re
import uuid
from google import genai
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
from PIL import Image

load_dotenv()

def parse_vtt(vtt_path):
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = content.split('\n\n')
    transcript = ""
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 2 and '-->' in lines[1]:
            time_line = lines[1]
            text = " ".join(lines[2:])
            text = re.sub(r'<[^>]+>', '', text)
            transcript += f"[{time_line.split(' ')[0]}] {text}\n"
        elif len(lines) >= 2 and '-->' in lines[0]:
            time_line = lines[0]
            text = " ".join(lines[1:])
            text = re.sub(r'<[^>]+>', '', text)
            transcript += f"[{time_line.split(' ')[0]}] {text}\n"
    return transcript

def transcribe_audio_fallback(video_path):
    print("No VTT found. Running local faster-whisper fallback...")
    from faster_whisper import WhisperModel
    
    temp_audio = f"temp_fallback_{uuid.uuid4().hex}.wav"
    try:
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(temp_audio, logger=None)
        clip.close()
        
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(temp_audio, word_timestamps=False)
        
        transcript = ""
        for s in segments:
            m, sec = divmod(int(s.start), 60)
            h, m = divmod(m, 60)
            transcript += f"[{h:02d}:{m:02d}:{sec:02d}.000] {s.text}\n"
            
        return transcript
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

def find_best_clip(video_path, vtt_path=None):
    """
    Uses Gemini SDK to analyze the TEXT transcript to save costs,
    and a single frame screenshot to determine speaker position.
    """
    if not video_path or not os.path.exists(video_path):
        print("Video path invalid.")
        return 0.0, 60.0, "Powerful leadership insight! 💡\n\n#leadership #growth", "center"
        
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # 1. Get Transcript
    transcript = ""
    if vtt_path and os.path.exists(vtt_path):
        print(f"Parsing subtitle file {vtt_path}...")
        try:
            transcript = parse_vtt(vtt_path)
        except Exception as e:
            print(f"VTT Parsing failed: {e}")
    
    if not transcript.strip():
        transcript = transcribe_audio_fallback(video_path)
        
    if len(transcript) > 500000:
        transcript = transcript[:500000]
        
    print("Asking Gemini to find the best clip from transcript...")
    prompt = f"""
    You are an expert short-form video editor for Instagram Reels. 
    Read the following video transcript.
    Find the most engaging, viral, and insightful continuous segment that is between 30 and 60 seconds long.
    It should have a strong hook at the beginning and a satisfying conclusion.
    
    Respond ONLY with a JSON object in this EXACT format:
    {{"start_time": <start_second_as_int>, "end_time": <end_second_as_int>, "reason": "<brief_reason>", "instagram_caption": "<a highly detailed, engaging caption with a hook and 5-8 relevant hashtags based EXACTLY on what was said>"}}
    
    TRANSCRIPT:
    {transcript}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt]
        )
        
        text_resp = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_resp)
        
        start = float(data.get('start_time', 0))
        end = float(data.get('end_time', 60))
        caption = data.get('instagram_caption', "Powerful leadership insight! 💡\n\n#leadership #growth #motivation")
        reason = data.get('reason', '')
        
        if end - start > 90:
            end = start + 60
    except Exception as e:
        print(f"Error during transcript analysis: {e}. Defaulting to first 60s.")
        start, end = 0.0, 60.0
        caption = "Powerful leadership insight! 💡\n\n#leadership #growth #motivation"
        reason = "Fallback"
        
    # 2. Extract screenshot and ask Gemini Vision for speaker position
    print(f"Extracting screenshot at {start}s to determine speaker position...")
    try:
        clip = VideoFileClip(video_path)
        frame = clip.get_frame(start)
        clip.close()
        
        img = Image.fromarray(frame)
        
        img_prompt = "Look at this frame from a video. Where is the primary person/speaker located in this specific frame? Answer with ONLY ONE WORD: 'left', 'center', or 'right'."
        
        pos_resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, img_prompt]
        )
        
        speaker_pos = pos_resp.text.strip().lower()
        if 'left' in speaker_pos: speaker_pos = 'left'
        elif 'right' in speaker_pos: speaker_pos = 'right'
        else: speaker_pos = 'center'
    except Exception as e:
        print(f"Failed to detect speaker position: {e}")
        speaker_pos = 'center'
        
    print(f"Found clip from {start}s to {end}s. Speaker is: {speaker_pos}. Reason: {reason}")
    
    return start, end, caption, speaker_pos

if __name__ == "__main__":
    pass
