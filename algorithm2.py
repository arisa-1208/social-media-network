import heapq
from collections import defaultdict

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
network.add_node("soobin", {"type": "user", "post_count": 8, "total_views": 350, "age": 25, "gender": "male"})
network.add_node("beomgyu", {"type": "user", "post_count": 15, "total_views": 800, "age": 25, "gender": "male"})
network.add_node("taehyun", {"type": "user", "post_count": 12, "total_views": 600, "age": 24, "gender": "male"})
network.add_node("yeonjun", {"type": "user", "post_count": 18, "total_views": 950, "age": 25, "gender": "male"})
network.add_node("kai", {"type": "user", "post_count": 5, "total_views": 200, "age": 24, "gender": "male"})

network.add_node("Post_S1", {"type": "post", "view_count": 120, "comment_count": 35})
network.add_node("Post_B1", {"type": "post", "view_count": 200, "comment_count": 45})
network.add_node("Post_Y1", {"type": "post", "view_count": 300, "comment_count": 60})

# Create directed edges showing authorship relationships
network.add_edge("soobin", "Post_S1", {"connection": "created"})
network.add_edge("beomgyu", "Post_B1", {"connection": "created"})
network.add_edge("yeonjun", "Post_Y1", {"connection": "created"})

# Calculate user interestingness based on activity metrics
def calculate_interest_score(user_data):
    # Extract relevant metrics with default values
    post_activity = user_data.get("post_count", 0)
    view_activity = user_data.get("total_views", 0)
    return post_activity + view_activity  # Combined activity score

# Identify most interesting users using priority queue
def find_top_interesting_users(network, num_users=3):
    user_scores = []  # Priority queue for ranking
    
    # Examine each node in the network
    for node_id in network.all_nodes():
        node_info = network.node_attributes(node_id)
        if node_info and node_info.get("type") == "user":  # Process only user nodes
            interest_score = calculate_interest_score(node_info)
            heapq.heappush(user_scores, (-interest_score, node_id))  # Use negative for max-heap
    
    # Extract top-ranked users
    most_interesting = []
    for _ in range(min(num_users, len(user_scores))):
        if user_scores:
            score, user_id = heapq.heappop(user_scores)
            most_interesting.append(user_id)
    
    return most_interesting

# Execute analysis and display results
interesting_users = find_top_interesting_users(network)
print("Most Interesting Users:", interesting_users)
