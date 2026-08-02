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
            print(f"Fetched {len(proxies)} free proxies for GCP bypass.")
            return proxies
    except Exception as e:
        print("Error fetching proxies:", e)
    return []

def get_latest_video(search_query, max_results=10, download_dir="downloads"):
    """
    Searches YouTube and downloads using public proxy rotation to bypass GCP blocks.
    Returns: video_path, None, title
    """
    os.makedirs(download_dir, exist_ok=True)
    
    ydl_opts_base = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),
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
    
    print(f"Searching for '{search_query}' on YouTube...")
    
    video = None
    try:
        # GCP is sometimes allowed to search without proxy
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            result = ydl.extract_info(f"ytsearch{max_results}:{search_query} speech", download=False)
            if result and 'entries' in result and result['entries']:
                video = random.choice(result['entries'])
    except Exception as e:
        pass
        
    proxies = get_free_proxies()
    random.shuffle(proxies)
    
    if not video:
        print("Direct search blocked. Attempting search with proxies...")
        for proxy_ip in proxies[:10]:
            proxy = f"http://{proxy_ip}"
            search_opts['proxy'] = proxy
            try:
                with yt_dlp.YoutubeDL(search_opts) as ydl:
                    result = ydl.extract_info(f"ytsearch{max_results}:{search_query} speech", download=False)
                    if result and 'entries' in result and result['entries']:
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
    title = video.get('title')
    print(f"Selected video: {title} ({video_url})")
    
    print("Downloading video (using proxy rotation to bypass Google Data Center block)...")
    download_success = False
    
    # Try direct first just in case GCP isn't blocked
    try:
        with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
            ydl.download([video_url])
            download_success = True
    except Exception:
        print("Direct download blocked. Falling back to proxy rotation...")
        
    if not download_success:
        for proxy_ip in proxies[:30]:
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
            except Exception:
                pass

    if not download_success:
        print("Failed to download video after trying 30 proxies.")
        return None, None, None

    video_path = os.path.join(download_dir, f"{video_id}.mp4")
    if not os.path.exists(video_path):
        files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
        files.sort(key=os.path.getctime, reverse=True)
        if files:
            video_path = files[0]
            
    return video_path, None, title

if __name__ == "__main__":
    v, s, t = get_latest_video("John Maxwell", max_results=5)
    print(v, s, t)
