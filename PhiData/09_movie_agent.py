from typing import List
from rich.pretty import pprint
from pydantic import BaseModel, Field
from phi.agent import Agent, RunResponse
from phi.model.google import Gemini

import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

class MovieScript(BaseModel):
    setting: str = Field(..., description="Provide a nice setting for a blockbuster movie.")
    ending: str = Field(..., description="Ending of the movie. If not available, provide a happy ending.")
    genre: str = Field(..., description="Genre of the movie. If not available, provide a genre.")
    name:str = Field(...,description="Give a name to this movie")
    characters: List[str] = Field(..., description="Name of the characters in the movie. If not available, provide a list of characters.")
    storyLine: str = Field(..., description="3 sentence storyline for the movie. Make it exciting, romantic and horror.")


# Agent that uses Json Mode
json_mode_agent= Agent(
    model=Gemini(id="gemini-1.5-pro"),
    description="You write movie scripts",
    response_model=MovieScript,
)

structured_output_agent= Agent(
    model=Gemini(id="gemini-1.5-pro"),
    description="You write movie scripts",
    response_model=MovieScript,
    structured_output=True,
)

# Get the response in a variable
# json_mode_agent.print_response("Dead City")
# structured_output_agent.print_response("Dead City")


# Get the response in a variable
json_mode_response: RunResponse = json_mode_agent.run("New York")
pprint(json_mode_response.content)
structured_output_response: RunResponse = structured_output_agent.run("New York")
pprint(structured_output_response.content)