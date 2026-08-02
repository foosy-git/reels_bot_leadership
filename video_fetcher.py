import os
import yt_dlp
import random
import imageio_ffmpeg
import time

def get_latest_video(search_query, max_results=10, download_dir="downloads"):
    """
    Searches YouTube for a query and downloads a video.
    Returns: video_path, None, title
    """
    os.makedirs(download_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),
        'skip_download': False,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        'extractor_args': {'youtube': {'player_client': ['ios', 'android']}} # Ideal for residential IPs
    }
    
    search_opts = {
        'extract_flat': True,
        'force_generic_extractor': True,
        'quiet': True,
        'no_warnings': True
    }
    
    print(f"Searching for '{search_query}' on YouTube...")
    
    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            result = ydl.extract_info(f"ytsearch{max_results}:{search_query} speech", download=False)
            if not result or 'entries' not in result or not result['entries']:
                print("No videos found on YouTube.")
                return None, None, None
                
            video = random.choice(result['entries'])
            video_url = video.get('url')
            title = video.get('title')
            video_id = video.get('id')
            
            print(f"Selected video: {title} ({video_url})")
            print("Downloading video from YouTube...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_dl:
                ydl_dl.download([video_url])
                
            video_path = os.path.join(download_dir, f"{video_id}.mp4")
            
            if not os.path.exists(video_path):
                # Fallback: find the most recently created file in downloads
                files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
                files.sort(key=os.path.getctime, reverse=True)
                if files:
                    video_path = files[0]
                    
            print("Download completed successfully!")
            return video_path, None, title
            
    except Exception as e:
        print(f"Failed to fetch video: {e}")
        return None, None, None

if __name__ == "__main__":
    v, s, t = get_latest_video("John Maxwell", max_results=5)
    print(v, s, t)
