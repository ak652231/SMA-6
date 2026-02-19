import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("YOUTUBE_API_KEY not found in .env")

def get_video_ids(channel_id, max_results=50):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "id",
        "channelId": channel_id,
        "maxResults": max_results,
        "order": "date",
        "type": "video",
        "key": API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return [i["id"]["videoId"] for i in r.json().get("items", [])]

def fetch_video_stats(video_ids):
    if not video_ids:
        return []

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()

    data = []
    for item in r.json().get("items", []):
        stats = item.get("statistics", {})
        data.append({
            "video_id": item["id"],
            "title": item["snippet"]["title"].strip(),
            "published_at": item["snippet"]["publishedAt"],
            "description": item["snippet"].get("description", ""),  # ⭐ ADDED
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0))
        })
    return data

def get_channel_country(channel_id):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "snippet",
        "id": channel_id,
        "key": API_KEY
    }
    r = requests.get(url, params=params)
    r.raise_for_status()

    items = r.json().get("items", [])
    if items:
        return items[0]["snippet"].get("country", "Unknown")
    return "Unknown"
    
