import os
import yt_dlp
import random
from duckduckgo_search import DDGS
import imageio_ffmpeg
import time

def get_latest_video(search_query, max_results=10, download_dir="downloads"):
    """
    Searches Facebook via DDG for a query and downloads a video.
    Returns: video_path, None (no vtt), title
    """
    os.makedirs(download_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),
        'skip_download': False,
        'noplaylist': True,
        'quiet': False,
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
    }
    
    print(f"Searching for '{search_query}' on Facebook...")
    
    try:
        results = DDGS().videos(f"{search_query} site:facebook.com", max_results=max_results)
    except Exception as e:
        print("DDGS search failed:", e)
        return None, None, None

    if not results:
        print("No videos found on Facebook.")
        return None, None, None
        
    # Filter to ensure we have facebook links
    fb_videos = [r for r in results if "facebook.com" in r.get('content', '')]
    if not fb_videos:
        fb_videos = results # fallback
        
    video = random.choice(fb_videos)
    video_url = video.get('content')
    title = video.get('title')
    
    print(f"Selected video: {title} ({video_url})")
    print("Downloading video from Facebook...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_id = info.get('id', 'unknown')
            video_path = os.path.join(download_dir, f"{video_id}.mp4")
            
            # Sometimes yt-dlp saves with a different extension if mp4 isn't strictly enforced
            # So we check what file was actually created
            if not os.path.exists(video_path):
                # Fallback: find the most recently created file in downloads
                files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
                files.sort(key=os.path.getctime, reverse=True)
                if files:
                    video_path = files[0]
                    
            print("Download completed successfully!")
            return video_path, None, title
            
    except Exception as e:
        print(f"Failed to download video: {e}")
        return None, None, None

if __name__ == "__main__":
    v, s, t = get_latest_video("John Maxwell", max_results=5)
    print(v, s, t)
