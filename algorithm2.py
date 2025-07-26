import heapq
from collections import defaultdict

"""
Author: Michaela Gillan

This algorithm determines "interesting" users based off various factors including post counts, total views, location, etc.

"""

# Directed graph implementation with adjacency list representation
class SocialGraph:
    def __init__(self):
        self.node_data = {}
        self.adjacency_list = defaultdict(list)
    
    def add_node(self, node_id, attributes):
        self.node_data[node_id] = attributes
    
    def add_edge(self, source, target, relationship):
        self.adjacency_list[source].append((target, relationship))
    
    def all_nodes(self):
        return list(self.node_data.keys())
    
    def node_attributes(self, node_id):
        return self.node_data.get(node_id)

# Initialize the social network graph
network = SocialGraph()

# Add user and post nodes with their attributes
network.add_node("soobin", {"type": "user", "post_count": 8, "total_views": 350, "age": 25, "gender": "male", 
                           "location": "Seoul", "comment_count": 45, "reading_level": "medium"})
network.add_node("beomgyu", {"type": "user", "post_count": 15, "total_views": 800, "age": 25, "gender": "male", 
                            "location": "Daegu", "comment_count": 30, "reading_level": "high"})
network.add_node("taehyun", {"type": "user", "post_count": 12, "total_views": 600, "age": 24, "gender": "male", 
                            "location": "Seoul", "comment_count": 55, "reading_level": "high"})
network.add_node("yeonjun", {"type": "user", "post_count": 18, "total_views": 950, "age": 25, "gender": "male", 
                            "location": "Bundang", "comment_count": 75, "reading_level": "medium"})
network.add_node("kai", {"type": "user", "post_count": 5, "total_views": 200, "age": 24, "gender": "male", 
                        "location": "Seoul", "comment_count": 20, "reading_level": "low"})

network.add_node("Post_S1", {"type": "post", "view_count": 120, "comment_count": 35, "reading_level": "medium"})
network.add_node("Post_B1", {"type": "post", "view_count": 200, "comment_count": 45, "reading_level": "high"})
network.add_node("Post_Y1", {"type": "post", "view_count": 300, "comment_count": 60, "reading_level": "medium"})

# Create directed edges showing authorship and viewing relationships
network.add_edge("soobin", "Post_S1", {"connection": "created"})
network.add_edge("beomgyu", "Post_B1", {"connection": "created"})
network.add_edge("yeonjun", "Post_Y1", {"connection": "created"})
# Add viewing relationships
network.add_edge("taehyun", "Post_S1", {"connection": "viewed"})
network.add_edge("kai", "Post_B1", {"connection": "viewed"})

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

# Multi-attribute filtering system
def filter_users_by_attributes(network, attribute_filters):
    filtered_users = []
    
    for node_id in network.all_nodes():
        node_data = network.node_attributes(node_id)
        if node_data and node_data.get("type") == "user":
            matches_all_filters = True
            
            # Check each attribute filter
            for attr, value in attribute_filters.items():
                if node_data.get(attr) != value:
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
    
    # Extract top users
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

# Visualization data generator
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

# Example usage demonstrating potential analysis

# Example 1: Find users with high post counts
print("=== Example 1: Users with High Post Activity ===")
criteria1 = {
    "post_count_preference": "high",
    "post_weight": 2,
    "view_weight": 0.1
}
high_posters = find_interesting_users_interactive(network, criteria1, num_users=3)
for i, user in enumerate(high_posters, 1):
    print(f"{i}. {user['user_id']} (Score: {user['score']:.1f}, Posts: {user['data']['post_count']})")

# Example 2: Find users from Seoul with high reading levels
print("\n=== Example 2: Seoul Users with High Reading Levels ===")
criteria2 = {
    "reading_level_preference": "high",
    "reading_weight": 10,
    "comment_preference": "high",
    "comment_weight": 1
}
attribute_filter = {"location": "Seoul"}
seoul_readers = find_interesting_users_interactive(network, criteria2, attribute_filter, num_users=3)
for i, user in enumerate(seoul_readers, 1):
    print(f"{i}. {user['user_id']} (Score: {user['score']:.1f}, Location: {user['data']['location']}, Reading: {user['data']['reading_level']})")

# Example 3: Find users with low activity (possibly new users)
print("\n=== Example 3: Low Activity Users (New Users) ===")
criteria3 = {
    "post_count_preference": "low",
    "post_weight": 2,
    "comment_preference": "low",
    "comment_weight": 1
}
low_activity = find_interesting_users_interactive(network, criteria3, num_users=3)
for i, user in enumerate(low_activity, 1):
    print(f"{i}. {user['user_id']} (Score: {user['score']:.1f}, Posts: {user['data']['post_count']}, Comments: {user['data']['comment_count']})")

# Generate visualization data
print("\n=== Visualization Data ===")
viz_data = generate_visualization_data(network, high_posters)
print(f"Generated {len(viz_data['nodes'])} nodes and {len(viz_data['edges'])} edges")
print(f"Highlighted users: {[user['user_id'] for user in viz_data['highlighted_users']]}")
print(f"Node types: {set(node['type'] for node in viz_data['nodes'])}")
print(f"Edge relationships: {set(edge['relationship'] for edge in viz_data['edges'])}")
