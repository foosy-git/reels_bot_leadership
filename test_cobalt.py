import requests
import json

url = "https://www.youtube.com/watch?v=BJ16i5QFT0U"

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

data = {
    "url": url,
    "vCodec": "h264",
    "vQuality": "720",
    "isAudioOnly": False,
    "disableMetadata": True
}

try:
    print("Testing Cobalt API...")
    resp = requests.post("https://co.wuk.sh/api/json", json=data, headers=headers)
    print("Status:", resp.status_code)
    print("Response:", resp.text)
except Exception as e:
    print("Error:", e)
