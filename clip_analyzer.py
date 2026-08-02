import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def find_best_clip(video_path):
    """
    Uses Gemini File API to upload the raw video and analyze it.
    Finds the most engaging 30-60 second clip.
    Returns the start and end time in seconds, and an instagram caption.
    """
    if not video_path or not os.path.exists(video_path):
        print("Video path invalid.")
        return 0.0, 60.0, "Powerful leadership insight! 💡\n\n#leadership #growth"
        
    print(f"Uploading {video_path} to Gemini for native video analysis...")
    
    try:
        # Upload the video file
        video_file = genai.upload_file(path=video_path)
        
        # Wait for Gemini to process the video (can take a minute or two)
        print("Waiting for Gemini to process the video...")
        while video_file.state.name == 'PROCESSING':
            print('.', end='', flush=True)
            time.sleep(10)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == 'FAILED':
            print("\nGemini video processing failed.")
            return 0.0, 60.0, "Powerful leadership insight! 💡\n\n#leadership #growth"
            
        print("\nVideo processed successfully. Analyzing...")
        
        prompt = """
        You are an expert short-form video editor for Instagram Reels. 
        Watch this entire video.
        Find the most engaging, viral, and insightful continuous segment that is between 30 and 60 seconds long.
        It should have a strong hook at the beginning and a satisfying conclusion.
        
        Respond ONLY with a JSON object in this EXACT format:
        {"start_time": <start_second_as_int>, "end_time": <end_second_as_int>, "reason": "<brief_reason>", "instagram_caption": "<a highly detailed, engaging caption with a hook and 5-8 relevant hashtags based EXACTLY on what was said>"}
        """
        
        # We use gemini-1.5-pro for video understanding as it is highly capable
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        response = model.generate_content([video_file, prompt])
        
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
        
        # Clean up the file from Google's servers
        genai.delete_file(video_file.name)
        
        return start, end, caption
        
    except Exception as e:
        print(f"Error during LLM video analysis: {e}. Defaulting to first 60s.")
        return 0.0, 60.0, "Powerful leadership insight! 💡\n\n#leadership #growth #motivation"

if __name__ == "__main__":
    pass
