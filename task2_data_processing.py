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
