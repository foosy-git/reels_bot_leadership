import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Required environment variables:
# IG_USER_ID = The Instagram Business/Creator Account ID
# IG_ACCESS_TOKEN = The Facebook Graph API Access Token (Long-lived)

def upload_to_temp_host(local_path):
    """
    Facebook Graph API requires a public URL for the video. 
    If you are running locally, we upload it to uguu.se for Instagram to fetch.
    """
    print("Uploading video to a temporary public host (uguu.se) for Instagram to fetch...")
    url = "https://uguu.se/upload.php"
    
    with open(local_path, 'rb') as f:
        files = {'files[]': f}
        response = requests.post(url, files=files)
        
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and len(data.get("files", [])) > 0:
            public_url = data["files"][0]["url"]
            print(f"Temporary public URL: {public_url}")
            return public_url
    
    raise Exception(f"Failed to upload to temp host: Status {response.status_code}, {response.text}")

def post_reel(local_video_path, caption):
    """
    Publishes an Instagram Reel using the Facebook Graph API.
    """
    ig_user_id = os.getenv("IG_USER_ID")
    access_token = os.getenv("IG_ACCESS_TOKEN")
    
    if not ig_user_id or not access_token:
        print("Skipping Instagram Upload: IG_USER_ID or IG_ACCESS_TOKEN not set in .env")
        return False
        
    # 1. Get a public URL for the video
    video_url = upload_to_temp_host(local_video_path)
    
    print("Step 1: Creating Media Container...")
    container_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
    payload = {
        'media_type': 'REELS',
        'video_url': video_url,
        'caption': caption,
        'access_token': access_token
    }
    
    response = requests.post(container_url, data=payload)
    if response.status_code != 200:
        print(f"Error creating container: {response.text}")
        return False
        
    creation_id = response.json().get('id')
    print(f"Container created with ID: {creation_id}. Waiting for processing...")
    
    # 2. Wait for Instagram to process the video from the URL
    status_url = f"https://graph.facebook.com/v20.0/{creation_id}?fields=status_code&access_token={access_token}"
    
    max_retries = 10
    for i in range(max_retries):
        time.sleep(10) # wait 10 seconds between checks
        status_response = requests.get(status_url)
        if status_response.status_code == 200:
            status = status_response.json().get('status_code')
            if status == 'FINISHED':
                print("Processing complete!")
                break
            elif status == 'ERROR':
                print("Error during video processing on Instagram's side.")
                return False
            else:
                print(f"Status: {status}... waiting.")
        else:
            print("Failed to check status.")
            return False
            
    # 3. Publish the Container
    print("Step 3: Publishing the Reel...")
    publish_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
    publish_payload = {
        'creation_id': creation_id,
        'access_token': access_token
    }
    
    pub_response = requests.post(publish_url, data=publish_payload)
    if pub_response.status_code == 200:
        print("Reel published successfully!")
        return True
    else:
        print(f"Error publishing reel: {pub_response.text}")
        return False

if __name__ == "__main__":
    pass
