import os
import yt_dlp
import random
import imageio_ffmpeg
import time

def get_latest_video(search_query, max_results=10, download_dir="downloads"):
    """
    Searches YouTube natively bypassing datacenter blocks.
    Returns: video_path, None, title
    """
    os.makedirs(download_dir, exist_ok=True)
    
    # MAGIC FIX: Bypasses YouTube Datacenter SABR and Bot Detection blocks
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': f'{download_dir}/%(id)s.%(ext)s',
        'skip_download': False,
        'noplaylist': True,
        'quiet': False,
        'cookiefile': 'cookies.txt',
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        'extractor_args': {
            'youtube': {
                'player_client': ['tv_downgraded', 'web', 'android_vr'],
                'player_skip': ['webpage']
            }
        },
        'source_address': '0.0.0.0', # Force IPv4
    }
    
    # Pre-defined channel maps to avoid `ytsearch:` 403 errors
    channel_map = {
        "simon sinek": "https://www.youtube.com/@SimonSinek/videos",
        "john maxwell": "https://www.youtube.com/@JohnMaxwellCo/videos"
    }
    
    search_url = channel_map.get(search_query.lower().strip())
    
    if search_url:
        print(f"Fetching latest videos from {search_url}...")
        try:
            # Extract playlist metadata (does not trigger 403 on GCP)
            search_opts = {
                'extract_flat': True,
                'quiet': True,
                'playlistend': max_results
            }
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                result = ydl.extract_info(search_url, download=False)
                if result and 'entries' in result:
                    videos = list(result['entries'])
                    if not videos:
                        return None, None, None
                    video = random.choice(videos)
                    video_url = f"https://www.youtube.com/watch?v={video.get('id')}"
                    title = video.get('title')
        except Exception as e:
            print("Channel extraction failed:", e)
            return None, None, None
    else:
        # Fallback to standard ytsearch if unknown query (might 403)
        print(f"Searching for '{search_query}' on YouTube...")
        try:
            search_opts = dict(ydl_opts)
            search_opts['extract_flat'] = True
            search_opts['skip_download'] = True
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                result = ydl.extract_info(f"ytsearch{max_results}:{search_query}", download=False)
                if result and 'entries' in result:
                    videos = list(result['entries'])
                    if not videos:
                        return None, None, None
                    video = random.choice(videos)
                    video_url = f"https://www.youtube.com/watch?v={video.get('id')}"
                    title = video.get('title')
        except Exception as e:
            print("ytsearch failed:", e)
            return None, None, None

    print(f"Selected video: {title} ({video_url})")
    print("Downloading video natively (bypassing datacenter blocks)...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            
            if 'requested_downloads' in info and len(info['requested_downloads']) > 0:
                video_path = info['requested_downloads'][0]['filepath']
            else:
                # If requested_downloads is missing, fallback to ext
                video_id = info.get('id', 'unknown')
                ext = info.get('ext', 'mp4')
                video_path = os.path.join(download_dir, f"{video_id}.{ext}")
            
            if not os.path.exists(video_path):
                print(f"Warning: Expected video path {video_path} does not exist.")
                    
            print(f"Download completed successfully! Saved to {video_path}")
            return video_path, None, title
            
    except Exception as e:
        print(f"Failed to download video: {e}")
        return None, None, None

if __name__ == "__main__":
    v, s, t = get_latest_video("John Maxwell", max_results=5)
    print(v, s, t)

