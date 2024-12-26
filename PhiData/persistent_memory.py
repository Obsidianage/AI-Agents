"""In PhiData, Persistent memory (PMEM) is a type of memory that can store chat history even when the session is closed."""

import os
import json

from rich.console import Console
from rich.panel import Panel
from rich.json import JSON

from phi.agent import Agent
# from phi.model.google import Gemini
from phi.model.groq import Groq
from phi.storage.agent.sqlite import SqlAgentStorage
from dotenv import load_dotenv

load_dotenv()

# os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["groq_api_key"] = os.getenv("groq_api_key")

agent = Agent(
    # model=Gemini(id="gemini-1.5-flash"),
    model=Groq(id="llama3-8b-8192"),
    # Store agent sessions in a dadabase
    storage=SqlAgentStorage(
        db_file="persistent_memory.db",
        table_name="agent_memory",
    ),
    # set add_history_to_messages=True to add the previous messages to the memory
    add_history_to_messages=True,
    # Number of responses to keep in memory
    num_history_responses=3,
    # The session id is used to identify the session in the database
    # You can resume any session by providing the session id
    # session_id="xxxx-xxxx-xxxx-xxxx"
    # Description of the agent
    description="You are a helpful assistant that can answer questions and help with tasks.",
)

# console is used to print the response
# Instead of: print("Hello")
# You can do: console.print("Hello")  
# This allows for fancy formatting
console = Console()

def print_chat_history(agent):
    console.print(
        Panel(                       # Creates a bordered box in the terminal
            JSON(                    # Formats the data as pretty JSON
                json.dumps(
                    # converts chat messages (which is pydantic model) to a list of dictionaries
                    [m.model_dump(include={"role","content"}) for m in agent.memory.messages]
                ),
                indent=4
            ),
            # add a title to the panel showing the session_id
            title = f"Chat history for session_id: {agent.session_id}",
            expand=True,
        )
    )

"""
Expected output:
┌─────────────── Chat history for session_id: xxxx-xxxx-xxxx-xxxx ───────────────┐
│ [                                                                              │
│     {                                                                          │
│         "role": "user",                                                        │
│         "content": "share 2 sentence drag queen horror story"                  │
│     },                                                                         │
│     {                                                                          │
│         "role": "assistant",                                                   │
│         "content": "..."                                                       │
│     }                                                                          │
│ ]                                                                              │
└────────────────────────────────────────────────────────────────────────────────┘
"""

# Run the agent
agent.print_response("share 2 sentence drag queen horror story", stream=True)

# Print the chat history
print_chat_history(agent)

# Ask follow up question
agent.print_response("What was my last question?", stream=True)

# Print the chat history
print_chat_history(agent)


