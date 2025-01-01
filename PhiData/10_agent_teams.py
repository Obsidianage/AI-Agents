from phi.agent import Agent
from phi.tools.hackernews import HackerNews
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.model.google import Gemini
# from phi.model.groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

# Get API key from .env file
api_key = os.getenv("GOOGLE_API_KEY")

# Create a single model instance to reuse
# groq_model = Groq(
#     model_name="llama3-8b-8192",
#     api_key=api_key
# )

gemini_model = Gemini(
    model_name="gemini-1.5-pro",
    api_key=api_key
)

hn_researcher = Agent(
    name="Hacker News Researcher",
    tools=[HackerNews()],
    model=gemini_model,
    role="Gets top 1 story from hackernews"
)

web_searcher = Agent(
    name="Web Searcher",
    role="Searches the web for information on a topic",
    tools=[DuckDuckGo()],
    model=gemini_model,
    add_datetime_to_instructions=True
)

article_reader = Agent(
    name="Article Reader",
    role="Reads articles from URLs.",
    tools=[Newspaper4k()],
    model=gemini_model
)

hn_team = Agent(
    name="Hacker News Team",
    model=gemini_model,
    team=[hn_researcher, web_searcher, article_reader],
    instructions=[
        "Follow these steps in order, waiting for each step to complete before moving to the next:",
        
        "1. First, get the top story from Hacker News:",
        "   - Use task_description='Get the top 1 story from Hacker News'",
        "   - Use expected_output='A list of the top 1 story with title and URL'",
        "   - Use additional_information='Include both title and URL for the story'",
        "   - After getting the story, proceed to step 2",
        
        "2. Next, read the story content:",
        "   - Take the URL from step 1",
        "   - Use task_description='Read and summarize the article at [paste the exact URL from step 1]'",
        "   - Use expected_output='A detailed summary of the article content'",
        "   - Use additional_information='Focus on key points and insights'",
        "   - After getting the summary, proceed to step 3",
        
        "3. Then, search for additional context:",
        "   - Take the title from step 1",
        "   - Use task_description='Search for additional information about [paste the exact title]'",
        "   - Use expected_output='Recent discussions and context about this topic'",
        "   - Use additional_information='Find related discussions and reactions'",
        "   - After getting the context, proceed to step 4",
        
        "4. Finally, write the article:",
        "   - Combine the story details from step 1",
        "   - Include the article summary from step 2",
        "   - Add the additional context from step 3",
        "   - Format it as a complete news article with introduction, body, and conclusion",
        
        "Important: You must complete ALL steps in order. Don't stop after step 1."
    ],
    show_tool_calls=True,
    markdown=True,
    add_chat_history_to_messages=True 
)

hn_team.print_response("Write an article about the top story on Hacker News. Make sure to include the story content and additional context.", stream=True)
