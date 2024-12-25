"""
PhiData documentation:

Writing your own Tools
For more control, write your own python functions and add them as tools to an Agent. For example, here’s how to add a get_top_hackernews_stories tool to an Agent.

"""

import json
import httpx
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo

import os
from dotenv import load_dotenv

import feedparser

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

def get_top_hackernews_stories(num_stories: int = 10) -> str:
    """User this function to get the top stories from Hacker News.
    
    Args:
        num_stories (int): Number of stores to return. Defaults to 10.

    Returns:
        str: JSON string of the top stories.
    """
    # Fetch top story IDs
    response = httpx.get('https://hacker-news.firebaseio.com/v0/topstories.json')
    story_ids = response.json()

    # Fetch story details
    stories = []
    for story_id in story_ids[:num_stories]:
        story_response = httpx.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
        story = story_response.json()
        if "text" in story:
            story.pop("text", None)
        stories.append(story)
    return json.dumps(stories)

def get_huggingface_blog_posts(num_posts: int = 2) -> str:
    """Get recent blog posts from Hugging Face's blog.
    
    Args:
        num_posts (int): Number of blog posts to return. Defaults to 2.

    Returns:
        str: JSON string containing recent blog posts with title and link.
    """
    # Fetch RSS feed
    feed = feedparser.parse('https://huggingface.co/blog/feed.xml')
    
    # Process blog posts
    posts = []
    for entry in feed.entries[:num_posts]:
        post = {
            'title': entry.title,
            'link': entry.link,
        }
        posts.append(post)
    
    return json.dumps(posts, indent=2)

agent = Agent(
    model=Gemini(id="gemini-1.5-pro"),
    description="This agent is designed to fetch and summarize Hugging Face blog posts. It first gets the blog posts, then uses DuckDuckGo to search for their content, and finally provides a summary.",
    tools=[
        get_huggingface_blog_posts,
        DuckDuckGo()
    ],
    instructions=[
        "1. Use get_huggingface_blog_posts to get the latest blog posts",
        "2. For each blog post URL returned, use DuckDuckGo to search for its content using 'site:url', Search using only link and not the title",
        "3. Do Not produce summary or any text unless you search the web for the content",
        "4. Combine the information and provide a comprehensive summary of each blog post",
    ],
    show_tool_calls=True,
    markdown=True,
    debug_mode=True
)

agent.print_response("Get the latest Hugging Face blog posts and summarize their content.", stream=True)


# Although this code is not working as expected, it is a good starting point for writing your own tools.
# The problem is that DuckDuckGO is not able to search the web for the content of the blog posts.
# It is only able to search the web for the title of the blog posts.
# So, we need to use a different tool to search the web for the content of the blog posts.
