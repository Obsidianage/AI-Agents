import gradio as gr
from agents.resume_agent import ResumeMaker
from config.settings import RESUME_SYSTEM_MESSAGE

def create_resume_interface():
    resume_maker = ResumeMaker(RESUME_SYSTEM_MESSAGE)
    
    with gr.Tab("Resume Maker"):
        resume_input = gr.Textbox(label="Enter your details (skills, experience, education, etc.)", lines=10)
        resume_output = gr.Markdown(label="Generated Resume")
        resume_button = gr.Button("Generate Resume")
        resume_button.click(resume_maker.create_resume, inputs=[resume_input], outputs=[resume_output]) 