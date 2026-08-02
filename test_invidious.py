import requests

def get_working_invidious():
    try:
        r = requests.get("https://api.invidious.io/instances.json?sort_by=health")
        instances = r.json()
        for inst in instances:
            uri = inst[1].get("uri")
            api_type = inst[1].get("api")
            if uri and api_type:
                # Test the instance
                try:
                    test_url = f"{uri}/api/v1/videos/BJ16i5QFT0U"
                    headers = {"User-Agent": "Mozilla/5.0"}
                    test_r = requests.get(test_url, headers=headers, timeout=5)
                    if test_r.status_code == 200:
                        data = test_r.json()
                        formats = data.get("formatStreams", [])
                        if formats:
                            print(f"Working instance found: {uri}")
                            # Get the best 720p/1080p mp4
                            best_url = formats[-1].get("url")
                            print(f"Video URL: {best_url}")
                            return True
                except:
                    continue
    except Exception as e:
        print("Error getting instances:", e)
    return False

get_working_invidious()
