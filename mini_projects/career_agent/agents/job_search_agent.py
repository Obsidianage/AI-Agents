from .base_agent import BaseAgent
from langchain.agents import create_tool_calling_agent, AgentExecutor
from utils.file_handler import save_file

class JobSearch(BaseAgent):
    def __init__(self, system_message):
        super().__init__(system_message)
        self.agent = create_tool_calling_agent(self.model, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def find_jobs(self, user_input):
        response = self.agent_executor.invoke({
            "input": user_input,
            "chat_history": self.chat_history,
            "agent_scratchpad": ""
        })
        path = save_file(str(response.get('output')).replace("```markdown", "").strip(), 'Job_search')
        with open(path, 'r', encoding='utf-8') as f:
            return f.read() 