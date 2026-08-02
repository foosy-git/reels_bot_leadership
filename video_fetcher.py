import os
import yt_dlp
import random
import imageio_ffmpeg
import time

# Required for Datacenter Bot Bypass Mode B
os.environ["YT_DLP_POT_PROVIDER_URL"] = "http://127.0.0.1:4416"

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
        'js_runtimes': {'node': {}}, # Enable PO Token generation
        'remote_components': ['ejs:github'],
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
            video_id = info.get('id', 'unknown')
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
        print(f"Failed to download video: {e}")
        return None, None, None

if __name__ == "__main__":
    v, s, t = get_latest_video("John Maxwell", max_results=5)
    print(v, s, t)

