from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_community.tools import DuckDuckGoSearchResults

class BaseAgent:
    def __init__(self, system_message):
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
        self.prompt = self.create_agent_prompt(system_message)
        self.tools = [DuckDuckGoSearchResults()]
        self.chat_history = []

    def create_agent_prompt(self, system_message: str):
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{agent_scratchpad}")
        ])

    def trim_conversation(self, messages):
        """Trims conversation history to retain only the latest messages."""
        max_messages = 10
        return messages[-max_messages:] if len(messages) > max_messages else messages 