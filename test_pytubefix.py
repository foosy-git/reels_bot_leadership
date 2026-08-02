from pytubefix import YouTube

url = "https://www.youtube.com/watch?v=BJ16i5QFT0U"

# Test download video with ANDROID client
try:
    print("Testing video download with ANDROID client...")
    yt = YouTube(url, client='ANDROID')
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    print("Found video:", video)
    if video:
        video.download(output_path='downloads', filename='test_android.mp4')
        print("Video downloaded.")
except Exception as e:
    print("Video download error:", e)
