import requests
import time
import json
import os
from datetime import datetime

url = "https://hacker-news.firebaseio.com/v0/topstories.json"
headers = {"User-Agent": "TrendPulse/1.0"}

categories = {
    "technology": ["AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM"],
    "worldnews": ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports": ["NFL", "FIFA", "sport", "game", "team", "player", "league", "championship"],
    "science": ["research", "study", "space", "physics", "biology", "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming"]
}

stories = []

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    story_ids = response.json()[:500]
except Exception as e:
    print("Failed to fetch top story IDs:", e)
    story_ids = []

for category, keywords in categories.items():
    category_count = 0

    for story_id in story_ids:
        if category_count >= 25:
            break

        story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"

        try:
            story_response = requests.get(story_url, headers=headers)
            story_response.raise_for_status()
            story_data = story_response.json()
        except Exception as e:
            print(f"Failed to fetch story {story_id}: {e}")
            continue

        title = story_data.get("title", "")

        if any(keyword.lower() in title.lower() for keyword in keywords):
            story = {
                "post_id": story_data.get("id"),
                "title": title,
                "category": category,
                "score": story_data.get("score", 0),
                "num_comments": story_data.get("descendants", 0),
                "author": story_data.get("by"),
                "collected_at": datetime.now().isoformat()
            }
            stories.append(story)
            category_count += 1

    time.sleep(2)

os.makedirs("data", exist_ok=True)

date_string = datetime.now().strftime("%Y%m%d")
filename = f"data/trends_{date_string}.json"

with open(filename, "w", encoding="utf-8") as file:
    json.dump(stories, file, indent=4, ensure_ascii=False)

print(f"Collected {len(stories)} stories. Saved to {filename}")
