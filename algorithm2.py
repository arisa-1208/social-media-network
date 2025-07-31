import heapq
from collections import defaultdict
from datetime import datetime
from data import User, Post, Comment

"""
Author: Michaela Gillan

This algorithm determines "interesting" users based off various factors including post counts, total views, location, etc.

"""

# Social Graph implementation that works with data.py classes
class SocialGraph:
    def __init__(self):
        self.users = {}  # Dictionary of User objects
        self.posts = {}  # Dictionary of Post objects
        self.node_data = {}  # For compatibility with original algorithm
        self.adjacency_list = defaultdict(list)
    
    def add_user(self, user_obj):
        """Add a User object to the graph"""
        self.users[user_obj.username] = user_obj
        
        # Calculate metrics for the user
        user_metrics = self._calculate_user_metrics(user_obj)
        
        # Store in node_data format for algorithm compatibility
        self.node_data[user_obj.username] = {
            "type": "user",
            "post_count": len(user_obj.posts),
            "total_views": user_metrics['total_views'],
            "age": user_obj.age,
            "gender": user_obj.gender,
            "location": user_obj.region,
            "comment_count": len(user_obj.comments_authored),
            "reading_level": user_metrics['avg_reading_level'],
            "user_obj": user_obj  # Keep reference to original object
        }
    
    def add_post(self, post_obj):
        """Add a Post object to the graph"""
        self.posts[post_obj.id] = post_obj
        
        # Calculate post metrics
        post_metrics = self._calculate_post_metrics(post_obj)
        
        # Store in node_data format
        self.node_data[post_obj.id] = {
            "type": "post",
            "view_count": len(post_obj.views),
            "comment_count": len(post_obj.comments),
            "reading_level": post_metrics['reading_level'],
            "post_obj": post_obj
        }
        
        # Add authorship edge
        self.add_edge(post_obj.author_username, post_obj.id, {"connection": "created"})
        
        # Add viewing edges
        for viewer_username, _ in post_obj.views:
            self.add_edge(viewer_username, post_obj.id, {"connection": "viewed"})
    
    def _calculate_user_metrics(self, user_obj):
        """Calculate derived metrics for a user"""
        total_views = sum(len(post.views) for post in user_obj.posts)
        
        # Calculate average reading level of user's posts
        reading_levels = {"low": 1, "medium": 2, "high": 3}
        if user_obj.posts:
            avg_reading_numeric = sum(reading_levels.get(self._estimate_reading_level(post.content), 2) 
                                    for post in user_obj.posts) / len(user_obj.posts)
            # Convert back to string
            if avg_reading_numeric <= 1.5:
                avg_reading_level = "low"
            elif avg_reading_numeric <= 2.5:
                avg_reading_level = "medium"
            else:
                avg_reading_level = "high"
        else:
            avg_reading_level = "medium"
        
        return {
            'total_views': total_views,
            'avg_reading_level': avg_reading_level
        }
    
    def _calculate_post_metrics(self, post_obj):
        """Calculate derived metrics for a post"""
        reading_level = self._estimate_reading_level(post_obj.content)
        return {
            'reading_level': reading_level
        }
    
    def _estimate_reading_level(self, content):
        """Simple heuristic to estimate reading level based on content"""
        if not content:
            return "low"
        
        words = content.split()
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        if avg_word_length > 6:
            return "high"
        elif avg_word_length > 4:
            return "medium"
        else:
            return "low"
    
    def add_edge(self, source, target, relationship):
        self.adjacency_list[source].append((target, relationship))
    
    def all_nodes(self):
        return list(self.node_data.keys())
    
    def node_attributes(self, node_id):
        return self.node_data.get(node_id)
    
    def get_user_objects(self):
        """Return all User objects"""
        return self.users
    
    def get_post_objects(self):
        """Return all Post objects"""
        return self.posts

# Enhanced interestingness scoring with multiple criteria
def calculate_interest_score(user_data, criteria):
    score = 0
    
    # Post count scoring (high or low can be interesting)
    if criteria.get("post_count_preference") == "high":
        score += user_data.get("post_count", 0) * criteria.get("post_weight", 1)
    elif criteria.get("post_count_preference") == "low":
        score += (20 - user_data.get("post_count", 0)) * criteria.get("post_weight", 1)
    
    # Reading level scoring
    reading_levels = {"low": 1, "medium": 2, "high": 3}
    user_reading = reading_levels.get(user_data.get("reading_level", "medium"), 2)
    if criteria.get("reading_level_preference") == "high":
        score += user_reading * criteria.get("reading_weight", 1)
    elif criteria.get("reading_level_preference") == "low":
        score += (4 - user_reading) * criteria.get("reading_weight", 1)
    
    # Comment activity scoring
    if criteria.get("comment_preference") == "high":
        score += user_data.get("comment_count", 0) * criteria.get("comment_weight", 1)
    elif criteria.get("comment_preference") == "low":
        score += (100 - user_data.get("comment_count", 0)) * criteria.get("comment_weight", 1)
    
    # View activity scoring
    score += user_data.get("total_views", 0) * criteria.get("view_weight", 0.1)
    
    return max(0, score)

# Attribute filtering system
def filter_users_by_attributes(network, attribute_filters):
    filtered_users = []
    
    for node_id in network.all_nodes():
        node_data = network.node_attributes(node_id)
        if node_data and node_data.get("type") == "user":
            matches_all_filters = True
            
            # Check each attribute filter
            for attr, value in attribute_filters.items():
                if attr == "age_min" and node_data.get("age", 0) < value:
                    matches_all_filters = False
                    break
                elif attr == "age_max" and node_data.get("age", 100) > value:
                    matches_all_filters = False
                    break
                elif attr not in ["age_min", "age_max"] and node_data.get(attr) != value:
                    matches_all_filters = False
                    break
            
            if matches_all_filters:
                filtered_users.append((node_id, node_data))
    
    return filtered_users

# Interactive analysis function
def find_interesting_users_interactive(network, criteria, attribute_filters=None, num_users=3):
    # First filter by attributes if specified
    if attribute_filters:
        candidate_users = filter_users_by_attributes(network, attribute_filters)
    else:
        candidate_users = [(node_id, network.node_attributes(node_id)) 
                          for node_id in network.all_nodes() 
                          if network.node_attributes(node_id).get("type") == "user"]
    
    user_scores = []
    
    # Calculate scores for filtered users
    for user_id, user_data in candidate_users:
        interest_score = calculate_interest_score(user_data, criteria)
        heapq.heappush(user_scores, (-interest_score, user_id, user_data))
    
    # Get top users
    interesting_users = []
    for _ in range(min(num_users, len(user_scores))):
        if user_scores:
            neg_score, user_id, user_data = heapq.heappop(user_scores)
            interesting_users.append({
                "user_id": user_id,
                "score": -neg_score,
                "data": user_data
            })
    
    return interesting_users

# Function to create sample data using data.py classes
def create_sample_social_network():
    """Create a sample social network using data.py classes"""
    
    # Create users
    users = []

    soobin = User("soobin", "Choi Soobin", 25, "male", "Seoul")
    beomgyu = User("beomgyu", "Choi Beomgyu", 25, "male", "Daegu") 
    taehyun = User("taehyun", "Kang Taehyun", 24, "male", "Seoul")
    yeonjun = User("yeonjun", "Choi Yeonjun", 25, "male", "Bundang")
    kai = User("kai", "Huening Kai", 24, "male", "Seoul")
    
    anna = User("anna", "Anna Kim", 26, "female", "Seoul")
    jenny = User("jenny", "Jenny Park", 23, "female", "Busan")
    sarah = User("sarah", "Sarah Lee", 27, "female", "Seoul")
    mia = User("mia", "Mia Choi", 25, "female", "Daegu")
    
    users = [soobin, beomgyu, taehyun, yeonjun, kai, anna, jenny, sarah, mia]
    
    # Create posts with varying complexity to test reading level analysis
    post1 = soobin.make_post("post_s1", "Excited about our new song release!", datetime.now())
    post2 = beomgyu.make_post("post_b1", "Guitar practice session today.", datetime.now())
    post3 = yeonjun.make_post("post_y1", "Dance rehearsal was intense!", datetime.now())
    post4 = taehyun.make_post("post_t1", "Please support our new album!", datetime.now())
    post5 = kai.make_post("post_k1", "Just relaxing today.", datetime.now())
    post6 = anna.make_post("post_a1", "Experimenting with photography :)", datetime.now())
    post7 = jenny.make_post("post_j1", "Coffee and morning thoughts", datetime.now())
    post8 = sarah.make_post("post_s2", "Starting my social media journey <3", datetime.now())
    post9 = mia.make_post("post_m1", "Weekend vibes!", datetime.now())
    
    # Create additional posts for some users to create variety in post counts
    beomgyu.make_post("post_b2", "Getting better @ bass", datetime.now())
    beomgyu.make_post("post_b3", "Guitar maintenance tips", datetime.now())
    anna.make_post("post_a2", "Portrait photography workshop results", datetime.now())
    anna.make_post("post_a3", "Landscape photography :)", datetime.now())
    anna.make_post("post_a4", "Equipment review: camera lenses", datetime.now())
    sarah.make_post("post_s3", "coffee shops & rainy mornings", datetime.now())
    sarah.make_post("post_s4", "I think this cat likes me...", datetime.now())
    
    # Add viewing relationships to create engagement patterns
    # High-engagement users (view many posts)
    for user in [taehyun, anna, sarah]:  # These users view many posts
        for post in [post1, post2, post3, post4, post6, post8]:
            user.view_a_post(post)
    
    # Medium engagement users
    for user in [soobin, jenny, mia]:
        for post in [post1, post2, post6]:
            user.view_a_post(post)
    
    # Low engagement users
    kai.view_a_post(post1)
    yeonjun.view_a_post(post8)
    
    # Add comments to create comment activity patterns
    # High comment activity users
    taehyun.comment_on_a_post("comment_1", post1, "Great song! Can't wait to hear it.")
    anna.comment_on_a_post("comment_2", post1, "So excited for this!")
    anna.comment_on_a_post("comment_3", post2, "Your guitar skills are amazing!")
    anna.comment_on_a_post("comment_4", post4, "Very informative vocal techniques!")
    sarah.comment_on_a_post("comment_5", post4, "Very informative, thanks for sharing!")
    sarah.comment_on_a_post("comment_6", post6, "Beautiful photography work!")
    sarah.comment_on_a_post("comment_7", post8, "Excellent analysis!")
    
    # Medium comment activity
    jenny.comment_on_a_post("comment_8", post2, "Nice guitar work!")
    mia.comment_on_a_post("comment_9", post1, "Love this!")
    soobin.comment_on_a_post("comment_10", post6, "Amazing photos!")
    
    # Add more comments to create distinct activity levels
    for i in range(11, 16):
        anna.comment_on_a_post(f"comment_{i}", post8, f"Great insights #{i-10}!")
    
    for i in range(16, 20):
        sarah.comment_on_a_post(f"comment_{i}", post2, f"Interesting point #{i-15}!")
    
    # Create connections between users
    soobin.connect_user("beomgyu", "friend")
    soobin.connect_user("taehyun", "friend")
    beomgyu.connect_user("yeonjun", "friend")
    anna.connect_user("sarah", "friend")
    jenny.connect_user("anna", "friend")
    mia.connect_user("jenny", "friend")
    
    return users

# Generate visualization data (for potential future use)
def generate_visualization_data(network, interesting_users):
    nodes = []
    edges = []
    
    # Add all nodes with highlighting for interesting users
    interesting_ids = [user["user_id"] for user in interesting_users]
    max_score = max([user["score"] for user in interesting_users]) if interesting_users else 1
    
    for node_id in network.all_nodes():
        node_data = network.node_attributes(node_id)
        is_interesting = node_id in interesting_ids
        
        if is_interesting:
            user_score = next(user["score"] for user in interesting_users if user["user_id"] == node_id)
            node_size = 10 + (user_score / max_score) * 20  # Scale size by score
        else:
            node_size = 5 if node_data.get("type") == "post" else 8
        
        nodes.append({
            "id": node_id,
            "type": node_data.get("type", "unknown"),
            "size": node_size,
            "color": "#FF6B6B" if is_interesting else ("#4ECDC4" if node_data.get("type") == "user" else "#45B7D1"),
            "highlighted": is_interesting,
            "attributes": node_data
        })
    
    # Add edges
    for source_id in network.all_nodes():
        for target_id, edge_data in network.adjacency_list[source_id]:
            edges.append({
                "source": source_id,
                "target": target_id,
                "relationship": edge_data.get("connection", "unknown"),
                "color": "#FF6B6B" if edge_data.get("connection") == "created" else "#DDD"
            })
    
    return {"nodes": nodes, "edges": edges, "highlighted_users": interesting_users}

# Main execution and demonstration
if __name__ == "__main__":
    print("=== Creating Social Network from data.py classes ===")
    
    # Create sample data
    users = create_sample_social_network()
    
    # Initialize the social graph
    network = SocialGraph()
    
    # Add all users to the graph
    for user in users:
        network.add_user(user)
        # Add all posts from this user
        for post in user.posts:
            network.add_post(post)
    
    print(f"Network created with {len(network.users)} users and {len(network.posts)} posts")
    print(f"Total nodes: {len(network.all_nodes())}")
    
    # Example 1: Find users with high post activity
    print("\n=== Example 1: Users with High Post Activity ===")
    criteria1 = {
        "post_count_preference": "high",
        "post_weight": 2,
        "view_weight": 0.1
    }
    high_posters = find_interesting_users_interactive(network, criteria1, num_users=3)
    for i, user in enumerate(high_posters, 1):
        user_obj = network.users[user['user_id']]
        print(f"{i}. {user_obj.real_name} (@{user['user_id']}) - Score: {user['score']:.1f}")
        print(f"   Posts: {user['data']['post_count']}, Views: {user['data']['total_views']}")
    
    # Example 2: Find female users with high reading levels (as requested in requirements)
    print("\n=== Example 2: Female Users with High Reading Levels ===")
    criteria2 = {
        "reading_level_preference": "high",
        "reading_weight": 10,
        "comment_preference": "high",
        "comment_weight": 1
    }
    attribute_filter = {"gender": "female"}
    female_readers = find_interesting_users_interactive(network, criteria2, attribute_filter, num_users=3)
    for i, user in enumerate(female_readers, 1):
        user_obj = network.users[user['user_id']]
        print(f"{i}. {user_obj.real_name} (@{user['user_id']}) - Score: {user['score']:.1f}")
        print(f"   Gender: {user['data']['gender']}, Reading Level: {user['data']['reading_level']}")
        print(f"   Comments: {user['data']['comment_count']}, Location: {user['data']['location']}")
    
    # Example 3: Find Seoul users aged 24-26 with high activity
    print("\n=== Example 3: Seoul Users (24-26) with High Activity ===")
    criteria3 = {
        "post_count_preference": "high",
        "post_weight": 1,
        "comment_preference": "high", 
        "comment_weight": 2,
        "view_weight": 0.2
    }
    attribute_filter = {"location": "Seoul", "age_min": 24, "age_max": 26}
    seoul_active = find_interesting_users_interactive(network, criteria3, attribute_filter, num_users=5)
    for i, user in enumerate(seoul_active, 1):
        user_obj = network.users[user['user_id']]
        print(f"{i}. {user_obj.real_name} (@{user['user_id']}) - Score: {user['score']:.1f}")
        print(f"   Age: {user_obj.age}, Location: {user['data']['location']}")
        print(f"   Posts: {user['data']['post_count']}, Comments: {user['data']['comment_count']}")
    
    # Example 4: Find users with low activity (potentially new or inactive users)
    print("\n=== Example 4: Low Activity Users (New/Inactive Users) ===")
    criteria4 = {
        "post_count_preference": "low",
        "post_weight": 2,
        "comment_preference": "low",
        "comment_weight": 1
    }
    low_activity = find_interesting_users_interactive(network, criteria4, num_users=3)
    for i, user in enumerate(low_activity, 1):
        user_obj = network.users[user['user_id']]
        print(f"{i}. {user_obj.real_name} (@{user['user_id']}) - Score: {user['score']:.1f}")
        print(f"   Posts: {user['data']['post_count']}, Comments: {user['data']['comment_count']}")
    
    # Example 5: Multi-criteria analysis - Female users from Seoul with high engagement
    print("\n=== Example 5: Female Seoul Users with High Engagement ===")
    criteria5 = {
        "post_count_preference": "high",
        "post_weight": 1,
        "reading_level_preference": "high",
        "reading_weight": 2,
        "comment_preference": "high",
        "comment_weight": 3,
        "view_weight": 0.5
    }
    attribute_filter = {"gender": "female", "location": "Seoul"}
    female_seoul_engaged = find_interesting_users_interactive(network, criteria5, attribute_filter, num_users=3)
    for i, user in enumerate(female_seoul_engaged, 1):
        user_obj = network.users[user['user_id']]
        print(f"{i}. {user_obj.real_name} (@{user['user_id']}) - Score: {user['score']:.1f}")
        print(f"   Gender: {user['data']['gender']}, Location: {user['data']['location']}")
        print(f"   Posts: {user['data']['post_count']}, Comments: {user['data']['comment_count']}, Reading Level: {user['data']['reading_level']}")
    
