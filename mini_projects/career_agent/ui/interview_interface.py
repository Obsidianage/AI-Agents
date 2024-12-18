import gradio as gr
from agents.interview_agent import InterviewAgent
from config.settings import INTERVIEW_QUESTIONS_MESSAGE, MOCK_INTERVIEW_MESSAGE

def create_interview_interface():
    interview_agent = InterviewAgent(INTERVIEW_QUESTIONS_MESSAGE)
    mock_interview_agent = InterviewAgent(MOCK_INTERVIEW_MESSAGE)
    
    with gr.Tab("Interview Preparation"):
        with gr.Tab("Interview Questions"):
            question_input = gr.Textbox(label="What type of interview questions would you like?", lines=3)
            question_output = gr.Markdown(label="Interview Questions")
            question_button = gr.Button("Get Questions")
            question_button.click(interview_agent.get_interview_questions, inputs=[question_input], outputs=[question_output])
            
        with gr.Tab("Mock Interview"):
            chatbot = gr.Chatbot(type="messages")
            msg = gr.Textbox(label="Your Response")
            clear = gr.Button("Clear")
            
            def respond(message, history):
                bot_message = mock_interview_agent.mock_interview(message)
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": bot_message})
                return "", history
            
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            clear.click(lambda: None, None, chatbot, queue=False) 