import gradio as gr
from dotenv import load_dotenv
import os
from ui.learning_interface import create_learning_interface
from ui.interview_interface import create_interview_interface
from ui.resume_interface import create_resume_interface
from ui.job_search_interface import create_job_search_interface

load_dotenv()

def main_ui():
    with gr.Blocks(title="Career Assistant Agent", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # Career Assistant Agent
        Your AI-powered career development companion
        """)
        
        create_learning_interface()
        create_interview_interface()
        create_resume_interface()
        create_job_search_interface()
    
    return demo

if __name__ == "__main__":
    app = main_ui()
    app.launch()
