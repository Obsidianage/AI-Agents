from phi.agent import Agent
# from phi.model.openai import OpenAIChat
from phi.model.groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

task = (
    "Discuss the concept of 'The Ship of Theseus' and its implications on the notions of identity and change. "
    "Present arguments for and against the idea that an object that has had all of its components replaced remains "
    "fundamentally the same object. Conclude with your own reasoned position on the matter."
)

reasoning_agent = Agent(model=Groq(id="llama-3.3-70b-versatile"), reasoning=True, markdown=True, structured_outputs=True)
reasoning_agent.print_response(task, stream=True, show_full_reasoning=True)