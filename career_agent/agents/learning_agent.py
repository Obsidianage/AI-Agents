from .base_agent import BaseAgent
from langchain.agents import create_tool_calling_agent, AgentExecutor
from utils.file_handler import save_file

class LearningResourceAgent(BaseAgent):
    def tutorial_agent(self, user_input):
        agent = create_tool_calling_agent(self.model, self.tools, self.prompt)
        agent_executer = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        response = agent_executer.invoke({
            "input": user_input,
            "chat_history": self.chat_history,
            "agent_scratchpad": ""
        })
        path = save_file(str(response.get('output')).replace("```markdown", "").strip(), 'Tutorial')
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def query_bot(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history = self.trim_conversation(self.chat_history)
        response = self.model.invoke(self.chat_history)
        self.chat_history.append({"role": "assistant", "content": response.content})
        return response.content 