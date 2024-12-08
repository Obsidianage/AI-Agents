import litellm
from dotenv import load_dotenv
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
import pdfplumber
from docx import Document
import gradio as gr
load_dotenv()

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

llm = "gemini/gemini-1.5-flash-exp-0827"

tool = SerperDevTool()

cv_analysis_agent = Agent(
    role= "CV Analyzer",
    goal='Analyze the given CV and extract key skills and experiences and make improvements if needed for portfolio creation.',
    verbose = True,
    memory = True,
    backstory=(
        "As a CV Analyzer, you are skilled in identifiying key information"
        "from resumes to aid in building effective portolios."
        "You can add releveant skills and job responsibilities evaluating the whole CV."
    ),
    tools=[tool],
    llm = llm,
    allow_delegation=True
)

# Create the Portfolio Generation Agent
portfolio_generation_agent = Agent(
    role='Portfolio Generator',
    goal='Generate a beautiful static HTML/CSS/JS landing portfolio webpage based on CV analysis.',
    verbose=True,
    memory=True,
    backstory=(
        "As a Portfolio Generator, you craft engaging web pages with effective functionalities and color combinations "
        "to showcase individual talents and experiences with the best user experience."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False
)


cv_analysis_taks = Task(
    description=(
        "Analyze the provided {cv} and identify key skills, experiences, "
        "and accomplishments. Highlight notable projects and educational background."
    ),
    expected_output='A summary of skills experiences, and projects formatted for a portfolio.',
    tools=[tool],
    agent=cv_analysis_agent,
)

# writing task 
portfolio_task = Task(
    description=( "Generate a static HTML/CSS/JS landing portfolio with a name as header in top, navbar for different sections, beautiful and responsive design. "
        "Ensure that the layout is clean, with sections for skills, projects, experiences, certifications, publications, and contact details if present in the CV. "
        "Include a footer that does not overlap with the content. "
        "Use a modern color palette and incorporate CSS frameworks if necessary, "
        "but provide everything embedded in the HTML file. "
        "The output should be a complete HTML document starting from <html> to </html>, ready to deploy."
    ),
    expected_output=' A complete HTML/CSS/JS code content only for a portfolio website in a single html file', 
    tools=[tool],
    agent=portfolio_generation_agent,
    output_file='portfolio.html'

)


def read_cv_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    cv_content = ""
    
    if ext =='.pdf':
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                cv_content+= page.extract_text()
    elif ext == '.docx':
        doc = Document(filepath)
        for para in doc.paragraphs:
            cv_content+= para.text + "\n"

    else:
        raise ValueError("unsupported file format")
    

    return cv_content.strip()

crew = Crew(
    agents=[cv_analysis_agent,portfolio_generation_agent],
    tasks=[cv_analysis_taks,portfolio_task],
    process=Process.sequential,
)


import re


def process_cv(file):
    try:
        cv_file_content = read_cv_file(file.name)
        result = crew.kickoff(inputs={'cv': cv_file_content})

        # Print the entire result object to explore its contents (for debugging)
        print(result)

        # Convert the result to string
        html_output = str(result)

        # Use replace to remove '''html''' and ''' from the output
        clean_html_output = html_output.replace("'''html'''", '').replace("'''", '').strip()

        return clean_html_output  # Return the cleaned HTML
    except Exception as e:
        return f"Error: {e}"

# Gradio UI using Blocks
with gr.Blocks() as iface:
    gr.Markdown("# CV-2-HTML AI Enhanced Portfolio Website Generation")
    gr.Markdown("Upload your CV in PDF or DOCX format to analyze its content and generate a portfolio.")

    # File input for uploading CV
    cv_input = gr.File(label="Upload your CV (.pdf or .docx)")

    # Output textbox for generated HTML
    output_textbox = gr.Textbox(label="Generated HTML", lines=20, placeholder="Your generated HTML will appear here...", interactive=True)

    # Process button
    process_button = gr.Button("Generate Portfolio")

    # Define the button actions
    process_button.click(fn=process_cv, inputs=cv_input, outputs=output_textbox)

# Launch the Gradio interface
iface.launch()
    