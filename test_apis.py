import requests

def test_invidious():
    url = "https://vid.puffyan.us/api/v1/videos/BJ16i5QFT0U"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        formats = data.get("formatStreams", [])
        if formats:
            print("Invidious SUCCESS. Found formats.")
            return True
    except Exception as e:
        print("Invidious Failed:", e)
    return False

def test_cobalt():
    instances = ["https://cobalt.qck.earth", "https://api.cobalt.tools", "https://cobalt-api.kwiatektv.com"]
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    data = {"url": "https://www.youtube.com/watch?v=BJ16i5QFT0U"}
    
    for inst in instances:
        try:
            r = requests.post(f"{inst}/api/json", json=data, headers=headers, timeout=5)
            if r.status_code == 200:
                print(f"Cobalt SUCCESS on {inst}")
                return True
            else:
                print(f"Cobalt {inst} returned {r.status_code}")
        except Exception as e:
            print(f"Cobalt {inst} Failed: {e}")
    return False

test_invidious()
test_cobalt()
