import os
import time
import schedule
import random
from dotenv import load_dotenv

from youtube_fetcher import get_latest_video
from clip_analyzer import find_best_clip
from video_editor import edit_and_caption_video
from instagram_poster import post_reel

def run_bot():
    print(f"--- Starting Reels Bot at {time.ctime()} ---")
    
    # 1. Pick a creator
    creators = ["Simon Sinek", "John Maxwell"]
    creator = random.choice(creators)
    
    try:
        # 2. Fetch Video
        video_path, vtt_path, title = get_latest_video(creator, max_results=10)
        if not video_path:
            print("Failed to fetch video.")
            return
            
        # 3. Analyze for best clip
        start_time, end_time = find_best_clip(vtt_path)
        
        # 4. Edit Video
        output_file = f"final_reel_{int(time.time())}.mp4"
        edit_and_caption_video(video_path, start_time, end_time, output_file)
        
        # 5. Post to Instagram
        caption = f"Powerful insight from {creator}! 💡\n\n#leadership #motivation #{creator.replace(' ', '')} #shorts"
        post_reel(output_file, caption)
        
        # Clean up
        if os.path.exists(output_file):
            os.remove(output_file)
        if os.path.exists(video_path):
            os.remove(video_path)
        if vtt_path and os.path.exists(vtt_path):
            os.remove(vtt_path)
            
        print("--- Bot finished successfully ---")
        
    except Exception as e:
        print(f"An error occurred during the run: {e}")

if __name__ == "__main__":
    load_dotenv()
    
    # Run once immediately for testing
    print("Running initial test...")
    run_bot()
    
    # Schedule to run every 6 hours
    schedule.every(6).hours.do(run_bot)
    
    print("Bot is now running in background. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)
