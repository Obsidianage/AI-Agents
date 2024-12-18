import gradio as gr
from agents.job_search_agent import JobSearch
from config.settings import JOB_SEARCH_MESSAGE

def create_job_search_interface():
    job_search = JobSearch(JOB_SEARCH_MESSAGE)
    
    with gr.Tab("Job Search"):
        job_input = gr.Textbox(label="Enter job title and location (e.g., 'AI Engineer in San Francisco')")
        job_output = gr.Markdown(label="Job Listings")
        job_button = gr.Button("Search Jobs")
        job_button.click(job_search.find_jobs, inputs=[job_input], outputs=[job_output]) 