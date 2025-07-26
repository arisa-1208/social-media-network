# Author: Arisa Nakai
from datetime import datetime

# --- Comment Class ---
# Each comment has an ID, author, text content, and a timestamp.
class Comment:
    def __init__(self, comment_id, author_username, content, timestamp=None):
        self.id = comment_id  # Unique ID for each comment so we can tell them apart
        self.author_username = author_username  # The username of the person who made the comment
        self.content = content  # The actual comment text
        self.timestamp = timestamp if timestamp is not None else datetime.now()  # If no time is passed in, just use now
        self.author = None  # This will later link to the actual User object who made the comment

# --- Post Class ---
# Represents one post someone makes. Can have comments and track who viewed it.
class Post:
    def __init__(self, post_id, author_username, content, timestamp=None):
        self.id = post_id  # Unique ID for the post
        self.author_username = author_username  # Who posted it
        self.content = content  # What the post says (just text)
        self.timestamp = timestamp if timestamp is not None else datetime.now()  # Use now if not provided

        self.comments = []  # A list that stores all the Comment objects for this post
        self.views = []  # A list of (username, time) pairs of people who looked at this post

        self.author = None  # Just like with comments, we’ll later link this to the actual User object

    # This lets us record whenever someone looks at this post.
    def add_view(self, viewer_username, timestamp=None):
        self.views.append((viewer_username, timestamp if timestamp is not None else datetime.now()))

    # This adds a Comment object to the post.
    def add_comment(self, comment_obj):
        self.comments.append(comment_obj)

# --- User Class ---
# Represents one person in the social network.
class User:
    def __init__(self, username, real_name=None, age=None, gender=None, region=None):
        self.username = username  # Unique ID for the user (@handle)
        self.real_name = real_name  # Optional: full name
        self.age = age  # Optional: age
        self.gender = gender  # Optional: gender
        self.region = region  # Optional: where they’re from

        # These are all lists that help track what this user does:
        self.connections = []  # Who they’re connected to (like friends/followers), stored as (type, username)
        self.posts = []  # Posts they made
        self.viewed_posts = []  # Posts they’ve looked at
        self.comments_authored = []  # Comments they’ve written

    # Connect this user to another one — like sending a friend request
    def connect_user(self, target_username, relationship_type):
        self.connections.append((relationship_type, target_username))

    # Let this user make a new post
    def make_post(self, post_id, content, timestamp=None):
        new_post = Post(post_id=post_id, author_username=self.username, content=content, timestamp=timestamp)
        new_post.author = self  # Link the post back to the person who made it
        self.posts.append(new_post)  # Add it to their list of posts
        return new_post  # Return it in case we want to use it right away

    # Simulate this user looking at a post (like scrolling past it or clicking it)
    def view_a_post(self, post_obj, timestamp=None):
        self.viewed_posts.append(post_obj)  # Track it in the user's profile
        post_obj.add_view(self.username, timestamp)  # And also mark the view on the post side

    # Simulate writing a comment on someone’s post.
    def comment_on_a_post(self, comment_id, post_obj, content, timestamp=None):
        new_comment = Comment(comment_id=comment_id, author_username=self.username, content=content, timestamp=timestamp)
        new_comment.author = self  # Link the comment back to the person who made it
        self.comments_authored.append(new_comment)  # Add it to the list of all comments by this user
        post_obj.add_comment(new_comment)  # Add the comment to the post itself
        return new_comment  # Return the comment object so we can use it later if needed
