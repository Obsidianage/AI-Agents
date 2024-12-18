import gradio as gr
from agents.learning_agent import LearningResourceAgent
from config.settings import TUTORIAL_SYSTEM_MESSAGE, QUERY_SYSTEM_MESSAGE

def create_learning_interface():
    learning_agent = LearningResourceAgent(TUTORIAL_SYSTEM_MESSAGE)
    query_agent = LearningResourceAgent(QUERY_SYSTEM_MESSAGE)
    
    def handle_tutorial(query):
        return learning_agent.tutorial_agent(query)
    
    def handle_query(query):
        return query_agent.query_bot(query)
    
    with gr.Tab("Learning Resources"):
        with gr.Tab("Tutorial Generator"):
            tutorial_input = gr.Textbox(label="What would you like to learn about?", lines=3)
            tutorial_output = gr.Markdown(label="Generated Tutorial")
            tutorial_button = gr.Button("Generate Tutorial")
            tutorial_button.click(handle_tutorial, inputs=[tutorial_input], outputs=[tutorial_output])
            
        with gr.Tab("Q&A Bot"):
            chatbot = gr.Chatbot(type="messages")
            msg = gr.Textbox(label="Ask a question")
            clear = gr.Button("Clear")
            
            def respond(message, history):
                bot_message = handle_query(message)
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": bot_message})
                return "", history
            
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            clear.click(lambda: None, None, chatbot, queue=False) 