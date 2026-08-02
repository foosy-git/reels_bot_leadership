import os
import yt_dlp
import random
import imageio_ffmpeg

def get_latest_video(search_query, max_results=10, download_dir="downloads"):
    """
    Searches YouTube for a query and downloads a video along with its subtitles.
    Picks a random one from the top results.
    """
    os.makedirs(download_dir, exist_ok=True)
    
    # yt-dlp options for downloading
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),
        'writeautomaticsub': True,  # Download auto-generated subs
        'subtitleslangs': ['en'],    # English
        'skip_download': False,      # We want the video
        'noplaylist': True,
        'quiet': False,
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(), # Point to the python-installed ffmpeg
        'username': 'oauth2', # REQUIRED: Cookies are dead on headless servers
        'extractor_args': {'youtube': {'player_client': ['tv', 'android']}} # TV and Android do not require PO Tokens or JS runtimes
    }
    
    # Just search to get IDs first
    search_opts = {
        'extract_flat': True,
        'force_generic_extractor': True,
        'quiet': True
    }
    
    print(f"Searching for '{search_query}'...")
    with yt_dlp.YoutubeDL(search_opts) as ydl:
        result = ydl.extract_info(f"ytsearch{max_results}:{search_query}", download=False)
        if 'entries' not in result or not result['entries']:
            print("No videos found.")
            return None
        
        # Pick a random video from the recent results
        video = random.choice(result['entries'])
        video_url = video.get('url') or f"https://www.youtube.com/watch?v={video.get('id')}"
        video_id = video.get('id')
        print(f"Selected video: {video.get('title')} ({video_url})")
        
    print("Downloading video and subtitles...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
        
    video_path = os.path.join(download_dir, f"{video_id}.mp4")
    vtt_path = os.path.join(download_dir, f"{video_id}.en.vtt")
    
    if not os.path.exists(vtt_path):
        print("Warning: No English subtitles found.")
        vtt_path = None
        
    return video_path, vtt_path, video.get('title')

if __name__ == "__main__":
    v_path, s_path, title = get_latest_video("Simon Sinek", max_results=5)
    print(v_path, s_path)
