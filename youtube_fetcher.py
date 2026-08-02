import os
import yt_dlp
import random
import requests
import imageio_ffmpeg
import time

def get_free_proxies():
    """Fetches a list of free HTTP proxies from Proxyscrape."""
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all"
    try:
        r = requests.get(url, timeout=10)
        proxies = r.text.strip().split('\r\n')
        if proxies and proxies[0]:
            print(f"Fetched {len(proxies)} free proxies.")
            return proxies
    except Exception as e:
        print("Error fetching proxies:", e)
    return []

def get_latest_video(search_query, max_results=10, download_dir="downloads"):
    """
    Searches YouTube for a query and downloads a video along with its subtitles.
    Picks a random one from the top results. Uses public proxies to bypass IP blocks.
    """
    os.makedirs(download_dir, exist_ok=True)
    
    # Base yt-dlp options
    ydl_opts_base = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': False,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        'extractor_args': {'youtube': {'player_client': ['ios', 'android']}}
    }
    
    search_opts = {
        'extract_flat': True,
        'force_generic_extractor': True,
        'quiet': True,
        'no_warnings': True
    }
    
    print(f"Searching for '{search_query}'...")
    
    # 1. First try to get video IDs (usually works without proxy even on GCP)
    video = None
    try:
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            result = ydl.extract_info(f"ytsearch{max_results}:{search_query}", download=False)
            if 'entries' in result and result['entries']:
                video = random.choice(result['entries'])
    except Exception as e:
        print(f"Direct search failed: {e}")
        
    # 2. Try proxy for search if direct failed
    proxies = get_free_proxies()
    random.shuffle(proxies)
    
    if not video:
        print("Attempting search with proxies...")
        for proxy_ip in proxies[:10]: # Try up to 10 proxies
            proxy = f"http://{proxy_ip}"
            search_opts['proxy'] = proxy
            try:
                with yt_dlp.YoutubeDL(search_opts) as ydl:
                    result = ydl.extract_info(f"ytsearch{max_results}:{search_query}", download=False)
                    if 'entries' in result and result['entries']:
                        video = random.choice(result['entries'])
                        print(f"Search succeeded with proxy {proxy_ip}")
                        break
            except:
                continue

    if not video:
        print("No videos found after trying multiple proxies.")
        return None, None, None
        
    video_url = video.get('url') or f"https://www.youtube.com/watch?v={video.get('id')}"
    video_id = video.get('id')
    print(f"Selected video: {video.get('title')} ({video_url})")
    
    # 3. Download the video using proxies
    print("Downloading video and subtitles (this may take longer due to proxy speeds)...")
    
    download_success = False
    
    # Try direct first just in case
    try:
        with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
            ydl.download([video_url])
            download_success = True
    except Exception as e:
        print(f"Direct download blocked. Falling back to proxy rotation...")
        
    if not download_success:
        for proxy_ip in proxies[:30]: # Be persistent, try up to 30 proxies
            proxy = f"http://{proxy_ip}"
            ydl_opts = dict(ydl_opts_base)
            ydl_opts['proxy'] = proxy
            print(f"Trying proxy: {proxy_ip}...")
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url])
                download_success = True
                print("Download completed successfully!")
                break
            except Exception as e:
                # If we get blocked or timeout, it fails immediately and we try the next proxy
                pass

    if not download_success:
        print("Failed to download video after trying 30 proxies. Please try again later.")
        return None, None, None

    video_path = os.path.join(download_dir, f"{video_id}.mp4")
    vtt_path = os.path.join(download_dir, f"{video_id}.en.vtt")
    
    if not os.path.exists(vtt_path):
        print("Warning: No English subtitles found.")
        vtt_path = None
        
    return video_path, vtt_path, video.get('title')

if __name__ == "__main__":
    v_path, s_path, title = get_latest_video("Simon Sinek", max_results=5)
    print(v_path, s_path)
