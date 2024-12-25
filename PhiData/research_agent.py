from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.utils.pprint import pprint_run_response
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    tools=[DuckDuckGo(), Newspaper4k()],
    description="You are a senior NYT researcher writing an article on a topic.",
    instructions=[
        "For a given topic, search for the top 2 links.",
        "Then read each URL and extract the article text, if a URL isn't available, ignore it.",
        "Analyse and prepare an NYT worthy article based on the information.",
        "Don't use Bing",
    ],
    markdown = True,
    show_tool_calls=True,
    add_datetime_to_instructions=True,
    debug_mode=True,
)

response: RunResponse = agent.run("AI agents in 2025 News")
pprint_run_response(response,markdown=True)
print(response.tools)
