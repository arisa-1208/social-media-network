import json
import heapq
from datetime import datetime

# Load social media data from JSON
with open("shared_data/social_network.json", "r") as file:
    data = json.load(file)

users = data["users"]

# Filters
include_keywords = {"social", "algorithms"}  
exclude_keywords = set()                     
user_filters = {"region": "California"}      
TOP_K = 3                                    

def compute_trending_score(post):
    """
    Trending score = (end_views - start_views) / time difference in hours
    If no views, assume minimal score (0).
    """
    views = post.get("views", [])
    if len(views) < 2:
        return 0.0 

    views_sorted = sorted(views, key=lambda x: datetime.fromisoformat(x["timestamp"]))
    start_time = datetime.fromisoformat(views_sorted[0]["timestamp"])
    end_time = datetime.fromisoformat(views_sorted[-1]["timestamp"])

    start_count = views_sorted[0]["count"]
    end_count = views_sorted[-1]["count"]

    hours = (end_time - start_time).total_seconds() / 3600
    return (end_count - start_count) / hours if hours > 0 else 0

def filter_users(users, filters):
    return [
        user for user in users
        if all(user.get(attr) == val for attr, val in filters.items())
    ]

def filter_posts(users, include_keywords, exclude_keywords):
    posts = []
    for user in users:
        for post in user.get("posts", []):
            text = post["content"].lower()
            if include_keywords and not any(word in text for word in include_keywords):
                continue
            if exclude_keywords and any(word in text for word in exclude_keywords):
                continue
            posts.append(post)
    return posts

def get_trending_posts(posts, k):
    heap = []
    for p in posts:
        score = compute_trending_score(p)
        heapq.heappush(heap, (-score, p["id"], p))
    trending = [heapq.heappop(heap)[2] for _ in range(min(k, len(heap)))]
    return trending


filtered_users = filter_users(users, user_filters)
filtered_posts = filter_posts(filtered_users, include_keywords, exclude_keywords)
top_trending = get_trending_posts(filtered_posts, TOP_K)

print("=== Top Trending Posts ===")
for post in top_trending:
    print(f"Post ID: {post['id']} | Content: {post['content']}")
