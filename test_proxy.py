import requests
import random

def get_proxies():
    url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all"
    try:
        r = requests.get(url, timeout=10)
        proxies = r.text.strip().split('\r\n')
        if proxies and proxies[0]:
            print(f"Found {len(proxies)} proxies.")
            return proxies
    except Exception as e:
        print("Error fetching proxies:", e)
    return []

proxies = get_proxies()
if proxies:
    print("Sample:", random.sample(proxies, 5))
