from phi.tools.duckduckgo import DuckDuckGo
from phi.agent import Agent
from phi.model.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

agent = Agent(
    model=Gemini(id="gemini-1.5-pro"),
    description="You are a web search agent.",
    tools=[DuckDuckGo()],
    show_tool_calls=True,
    markdown=True,
    instructions=[
        "You are a web search agent.",
        "You are given a query and you need to search the web for the most relevant information.",
        "Use DuckDuckGo to search the web.",
    ],
    debug_mode=True
)

agent.print_response("what did the president say about AI agents in 2025", stream=True)
# agent.print_response("what are some of the best huggingface blog posts currently? You can find them here: https://huggingface.co/blog/, Use DuckDuckGo to search the web.as its a tool provided to you to use internet.", stream=True)


# OUTPUT
"""
┏━ Message ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                         ┃
┃ what did the president say about AI agents in 2025                      ┃
┃                                                                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┏━ Response (6.4s) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                         ┃
┃ I cannot directly access real-time information, including specific      ┃
┃ statements made by presidents.  To find this information, I would need  ┃
┃ to perform a web search.  I can do that using the available             ┃
┃ default_api.  However, the API only provides access to DuckDuckGo       ┃
┃ search and news, and it does not specify whether the results will       ┃
┃ include information from 2025.  Therefore, I cannot guarantee I will    ┃
┃ find the answer.                                                        ┃
┃                                                                         ┃
┃ To attempt to answer your question, I'll use DuckDuckGo to search for   ┃
┃ news articles about presidential statements on AI agents in 2025.       ┃
┃                                                                         ┃
┃  • Running: duckduckgo_news(query=president AI agents 2025,             ┃
┃ Based on the news articles from December 2024, there is no direct       ┃
┃ mention of statements made by the president regarding AI agents in      ┃
┃ 2025.  However, several articles discuss predictions and expectations   ┃
┃ for AI agent technology in 2025 from various experts and companies.     ┃
┃ These articles highlight the potential transformative impact of AI      ┃
┃ agents across sectors like crypto and technology in general.            ┃
┃                                                                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""