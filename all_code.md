# All Code (one file)

## Mini Project - Task 1: task1_data_collection.py

```python
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
```

## Mini Project - Task 2: task2_data_processing.py

```python
import pandas as pd
import glob

json_file = glob.glob("data/trends_*.json")[0]

df = pd.read_json(json_file)

print(f"Loaded {len(df)} stories from {json_file}")

df = df.drop_duplicates(subset="post_id")

print(f"After removing duplicates: {len(df)}")

df = df.dropna(subset=["post_id", "title", "score"])
print(f"After removing nulls: {len(df)}")

df["score"] = pd.to_numeric(df["score"], errors="coerce")
df["num_comments"] = pd.to_numeric(df["num_comments"], errors="coerce")

df = df[df["score"] >= 5]

print(f"After removing low scores: {len(df)}")

df["title"] = df["title"].str.strip()

df["score"] = df["score"].fillna(0).astype(int)
df["num_comments"] = df["num_comments"].fillna(0).astype(int)

output_file = "data/trends_clean.csv"
df.to_csv(output_file, index=False)

print(f"\nSaved {len(df)} rows to {output_file}")

print("\nStories per category:")
print(df["category"].value_counts())
```

## Mini Project - Task 3: task3_analysis.py

```python
import pandas as pd
import numpy as np

df = pd.read_csv("data/trends_clean.csv")

print(f"Loaded data: {df.shape}")

print("\nFirst 5 rows:")
print(df.head())

average_score = df["score"].mean()
average_comments = df["num_comments"].mean()

print(f"Average score: {average_score}")
print(f"Average comments: {average_comments}")

scores = df["score"].to_numpy()

mean_score = np.mean(scores)
median_score = np.median(scores)
std_score = np.std(scores)

print(f"\n--- Numpy stats ---")
print(f"Mean score : {mean_score}")
print(f"Median score : {median_score}")
print(f"Std deviation : {std_score}")
print(f"Max score : {np.max(scores)}")
print(f"Min score : {np.min(scores)}")

category_counts = df["category"].value_counts()
most_category = category_counts.idxmax()
most_category_count = category_counts.max()

print(f"\nMost stories in : {most_category} ({most_category_count} stories)")

most_commented_index = df["num_comments"].idxmax()
most_commented_title = df.loc[most_commented_index, "title"]
most_commented_count = df.loc[most_commented_index, "num_comments"]

print(f'\nMost commented story : "{most_commented_title}" - {most_commented_count} comments')

df["engagement"] = df["num_comments"] / (df["score"] + 1)

df["is_popular"] = df["score"] > average_score

output_file = "data/trends_analysed.csv"
df.to_csv(output_file, index=False)

print(f"\nSaved to {output_file}")
```

## Mini Project - Task 4: task4_visualise.py

```python
import pandas as pd
import matplotlib.pyplot as plt
import os

df = pd.read_csv("data/trends_analysed.csv")

os.makedirs("outputs", exist_ok=True)

top_stories = df.nlargest(10, "score").copy()

top_stories["short_title"] = top_stories["title"].apply(
    lambda title: title[:50] + "..." if len(title) > 50 else title
)

plt.figure(figsize=(10,6))
plt.barh(top_stories["short_title"], top_stories["score"])
plt.xlabel("Score")
plt.ylabel("Story Title")
plt.title("Top 10 Stories by Score")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("outputs/chart1_top_stories.png")
plt.show()
plt.close()

category_counts = df["category"].value_counts()

plt.figure(figsize=(8,5))
plt.bar(category_counts.index, category_counts.values,
color=["red", "blue", "green", "orange", "purple"])
plt.xlabel("category")
plt.ylabel("Number of Stories")
plt.title("Stories per Category")
plt.tight_layout()
plt.savefig("outputs/chart2_categories.png")
plt.show()
plt.close()

popular = df[df["is_popular"] == True]
not_popular = df[df["is_popular"] == False]

plt.figure(figsize=(8,5))

plt.scatter(
popular["score"],
popular["num_comments"],
color="red",
label="Popular"
)
plt.scatter(
not_popular["score"],
not_popular["num_comments"],
color="blue",
label="Not Popular"
)

plt.xlabel("score")
plt.ylabel("Number of Comments")
plt.title("Score vs Comments")
plt.tight_layout()
plt.savefig("outputs/chart3_scatter.png")
plt.show()
plt.close()

print("All 3 charts saved successfully!")
```

## Chat History: chat_history.py

```python
def fake_reply(messages):
    n_user = sum(1 for m in messages if m["role"] == "user")
    return {"content": f"Reply {n_user}", "finish_reason": "stop"}

def start_history(system_text):
    return [{"role": "system", "content": system_text}]

def chat_turn(history, user_text, reply_fn):
    history.append({"role": "user", "content": user_text})
    reply = reply_fn(history)
    history.append({"role": "assistant", "content": reply["content"]})
    return reply["content"], reply["finish_reason"]

def build_payload(history, model, max_tokens):
    return {
        "model": model,
        "messages": history,
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }

history = start_history("You are a helpful assistant")
for text in ["Hello", "What are your hours?", "Thanks"]:
    content, finish = chat_turn(history, text, fake_reply)
    print(content, finish, len(history))   # lengths 3, 5, 7

# The API is stateless: every call is independent, so all earlier messages are appended to
# the list and sent again. The tokens sent, and so the cost, grow every turn, and the
# history is limited by the context window.
```

## Loan Default Question: Model Answer

1. Logistic regression: 5 combinations. Decision tree: 4 × 3 = 12 combinations. With 5 folds: 5 × 5 = 25 and 12 × 5 = 60 models, 85 in total. A decision tree has no n_estimators because it consists of only one tree.

2. 2,000 / 5 = 400 applicants per fold; 200 defaulters / 5 = 40 defaulters per fold (10 percent in each). Stratified k-fold maintains the class distribution in every fold. Plain k-fold could produce folds with too few or too many defaulters, so validation scores would not be representative of an imbalanced dataset.

3. Means: X = (0.84 + 0.85 + 0.83 + 0.84 + 0.84) / 5 = 0.84; Y = (0.90 + 0.72 + 0.88 + 0.70 + 0.85) / 5 = 0.81; Z = 0.78. X has the highest mean and the lowest spread, so choose X. Candidate Y has a training mean of 0.99 but a lower mean and a wide spread across folds, which indicates overfitting and instability.

4. collections_status_after_default leaks the target: it is recorded after the default, so it is not available at prediction time yet is correlated with the target. It gives artificially high accuracy that collapses in deployment; compare performance with and without the feature to confirm. Remove it, and any similar post-event variable, before the train-test split so that all inputs are available at prediction time, using domain knowledge to verify each feature.
