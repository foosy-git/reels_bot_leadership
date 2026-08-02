import yt_dlp

url = "https://www.facebook.com/simonsinek/videos/present-with-charisma/1193404592470591/"

ydl_opts = {
    'writeautomaticsub': True,
    'writesubtitles': True,
    'subtitleslangs': ['en'],
    'outtmpl': 'downloads/test_fb.%(ext)s',
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
