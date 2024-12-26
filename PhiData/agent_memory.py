from phi.agent import Agent
from phi.model.google import Gemini

# Google Gemini is unable to handle fast requests.
# So we use Groq instead.
from phi.model.groq import Groq
from rich.pretty import pprint
from dotenv import load_dotenv
import os

load_dotenv()

# os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["groq_api_key"] = os.getenv("groq_api_key")

agent = Agent(
    model=Groq(id="llama3-8b-8192"),
    # model=Gemini(id="gemini-1.5-flash"),
    add_chat_history_to_messages=True,
    num_history_responses=3,
    description="You are a helpful assistant that can answer questions and help with tasks.",
)

# run
agent.print_response("share a 2 sentence horror story",stream=True)

# Print the msg in memory
pprint([m.model_dump(include={"role","content"}) for m in agent.memory.messages])
# the above code is saying store only the role and content of the messages in memory.
# m is the message object, and we are using model_dump to convert the message object to a dictionary.

# Ask follow up question
agent.print_response("What was my last question?", stream=True)
# print the msg in memory
pprint([m.model_dump(include={"role","content"}) for m in agent.memory.messages])
