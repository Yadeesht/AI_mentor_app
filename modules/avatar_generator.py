import requests
import time

HEYGEN_API_KEY = "ZWRkNTE3MDE5OGI1NGI1ZGJlNWE2ZTUwMDBkNjI1YTYtMTc1MDU3NTk0NQ==" 

DEFAULT_AVATAR_ID = "Oxana_standing_sofa_side"
DEFAULT_VOICE_ID = "e0ab1a13ed5f4fe9b1fd65cff2159a2f"
DEFAULT_AVATAR_STYLE = "normal"  

def generate_video(script, avatar_id=DEFAULT_AVATAR_ID, voice_id=DEFAULT_VOICE_ID, avatar_style=DEFAULT_AVATAR_STYLE, speed=1.0):
    url = "https://api.heygen.com/v2/video/generate"
    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": avatar_style
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id,
                    "speed": speed
                }
            }
        ],
        "dimension": {"width": 1280, "height": 720}
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-Api-Key": HEYGEN_API_KEY
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Failed to start video generation: {response.text}")
        return None
    data = response.json()
    video_id = None
    if "data" in data and data["data"] and "video_id" in data["data"]:
        video_id = data["data"]["video_id"]
    elif "video_id" in data:
        video_id = data["video_id"]
    elif "id" in data:
        video_id = data["id"]
    if not video_id:
        print(f"No video ID returned: {data}")
        return None

    status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    for _ in range(30):
        status_resp = requests.get(status_url, headers=headers)
        if status_resp.status_code != 200:
            print(f"Failed to get video status: {status_resp.text}")
            return None
        status_data = status_resp.json()
        data = status_data.get("data", {})
        if data.get("status") == "completed":
            print("DEBUG: Video URL from HeyGen:", data.get("video_url"))
            return data.get("video_url")
        elif data.get("status") == "failed":
            print(f"Video generation failed: {data}")
            return None
        time.sleep(6)
    print("Video generation timed out.")
    return None

