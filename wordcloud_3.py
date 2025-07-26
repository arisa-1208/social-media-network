# Author: Arisa Nakai
# wordcloud.py 
from data import User

# Standard libraries
from wordcloud import WordCloud 
import matplotlib.pyplot as plt

# --- Setup Sample Users ---
emily = User(username="emily_jones", real_name="Emily Jones", age=24, gender="F", region="West")
jake = User(username="jake_miller", real_name="Jake Miller", age=22, gender="M", region="East")
samantha = User(username="samantha_lee", real_name="Samantha Lee", age=23, gender="F", region="North")
david = User(username="david_kim", real_name="David Kim", age=25, gender="M", region="South")

users = [emily, jake, samantha, david]

# --- Connections ---
emily.connect_user("jake_miller", "friend")
emily.connect_user("samantha_lee", "follower")
jake.connect_user("david_kim", "follower")

# --- Posts ---
post1 = emily.make_post(post_id="p1", content="Social media filters are fun, but they also affect how we see ourselves.")
post2 = samantha.make_post(post_id="p2", content="Is anyone else finding it hard to focus lately with all these notifications?")
post3 = david.make_post(post_id="p3", content="I'm learning about how social networks spread information. Super cool stuff!")
post4 = jake.make_post(post_id="p4", content="Why is social media so addictive? I open one app and an hour disappears!")

posts = [post1, post2, post3, post4]

# --- Comments ---
comment1 = jake.comment_on_a_post(comment_id="c1", post_obj=post1, content="Totally agree! It's hard to ignore how much filters change things.")
comment2 = emily.comment_on_a_post(comment_id="c2", post_obj=post4, content="That’s so real. I always lose time scrolling!")

# --- Begin Analysis ---
print("---  Task 3 Analysis (Arisa) ---")

# --- 1. User Network Density ---
print("\n--- User Network Density (Number of Direct Connections) ---")
user_connections = [(user.username, user.real_name, len(user.connections)) for user in users]
user_connections.sort(key=lambda x: x[2], reverse=True)

for i, (uname, name, count) in enumerate(user_connections, 1):
    print(f"{i}. @{uname} ({name}): {count} connections")

# --- 2. Post Discussion Activity ---
print("\n--- Post Discussion Activity (Number of Comments) ---")
posts_sorted = sorted(posts, key=lambda p: len(p.comments), reverse=True)
for i, post in enumerate(posts_sorted, 1):
    snippet = post.content[:50] + ("..." if len(post.content) > 50 else "")
    print(f"{i}. Post ID: {post.id} by @{post.author_username}: {len(post.comments)} comments")
    print(f"   Content Snippet: \"{snippet}\"")

# --- 3. Word Cloud Visualization ---
print("\n--- Word Cloud of Post Content ---")
all_text = " ".join([post.content for post in posts])

# Create and display the word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("Word Cloud of All Posts")
plt.show()

print("\n--- Task 3 Analysis Completed ---")
