import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def parse_vtt(file_path):
    """Parses a VTT file into a more compact format for the LLM."""
    if not file_path or not os.path.exists(file_path):
        return None
        
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Basic VTT parsing
    # Format: HH:MM:SS.mmm --> HH:MM:SS.mmm
    blocks = content.split('\n\n')
    
    transcript_text = ""
    last_text = ""
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 2:
            time_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', lines[0])
            if not time_match and len(lines) >= 3:
                # Sometimes there's an ID line first
                time_match = re.search(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})', lines[1])
                text = " ".join(lines[2:]).strip()
            elif time_match:
                text = " ".join(lines[1:]).strip()
            else:
                continue
                
            if time_match:
                # Remove html tags like <c>
                text = re.sub(r'<[^>]+>', '', text)
                if text != last_text and text: # skip duplicates which are common in auto-subs
                    start_str = time_match.group(1)
                    # Convert to seconds
                    h, m, s = start_str.split(':')
                    s, ms = s.split('.')
                    total_seconds = int(h) * 3600 + int(m) * 60 + int(s)
                    
                    transcript_text += f"[{total_seconds}] {text}\n"
                    last_text = text
                    
    return transcript_text

def find_best_clip(vtt_path):
    """
    Uses Gemini to analyze the transcript and find the most engaging 30-60 second clip.
    Returns the start and end time in seconds.
    """
    transcript = parse_vtt(vtt_path)
    if not transcript:
        print("No transcript available to analyze. Defaulting to first 60 seconds.")
        return 0.0, 60.0
        
    prompt = f"""
    You are an expert short-form video editor for Instagram Reels. 
    Analyze the following video transcript which contains timestamps in seconds like [10].
    Find the most engaging, viral, and insightful continuous segment that is between 30 and 60 seconds long.
    It should have a strong hook at the beginning and a satisfying conclusion.
    
    Respond ONLY with a JSON object in this format:
    {{"start_time": <start_second_as_int>, "end_time": <end_second_as_int>, "reason": "<brief_reason>", "instagram_caption": "<a highly detailed, engaging caption with a hook and 5-8 relevant hashtags based EXACTLY on what was said>"}}
    
    Transcript:
    {transcript[:30000]} # Limit to first ~30k chars to avoid token limits just in case
    """
    
    try:
        # Try newer models first
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
        except Exception:
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(prompt)
            except Exception:
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                response = model.generate_content(prompt)
                
        text_resp = response.text
        
        # Clean up markdown JSON blocks if present
        text_resp = text_resp.replace('```json', '').replace('```', '').strip()
        data = json.loads(text_resp)
        
        start = float(data.get('start_time', 0))
        end = float(data.get('end_time', 60))
        caption = data.get('instagram_caption', "Powerful leadership insight! 💡\n\n#leadership #growth #motivation")
        
        # Ensure it's not too long
        if end - start > 90:
            end = start + 60
            
        print(f"Found clip from {start}s to {end}s. Reason: {data.get('reason')}")
        return start, end, caption
    except Exception as e:
        print(f"Error during LLM analysis: {e}. Defaulting to first 60s.")
        return 0.0, 60.0, "Powerful leadership insight! 💡\n\n#leadership #growth #motivation"

if __name__ == "__main__":
    # Test script
    pass
