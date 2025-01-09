import json
from typing import Optional, Iterator

from pydantic import BaseModel, Field

from phi.agent import Agent
from phi.model.groq import Groq
from phi.model.google import Gemini
from phi.tools.googlesearch import GoogleSearch
from phi.workflow import Workflow, RunResponse, RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.utils.pprint import pprint_run_response
from phi.utils.log import logger
import os

from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["google_api_key"] = os.getenv("google_api_key")

class IdeaClarification(BaseModel):
    originality: str = Field(..., description="Originality of the idea")
    mission: str = Field(..., description="Mission of the company")
    objectives: str = Field(..., description="Objectives of the company")


class MarketResearch(BaseModel):
    total_addressable_market:str = Field(..., description="Total addressable market (TAM).")
    serviceable_available_market:str = Field(...,description="Serviceable available market (SAM).")
    serviceable_obtainable_market:str = Field(...,description="Serviceable obtainable market (SOM).")
    target_customer_segments:str = Field(..., description="Target customer segments.")

    
class StartupIdeaValidator(Workflow):
    idea_clarifier_agent: Agent = Agent(
        # model = Groq(id="llama-3.3-70b-versatile"),
        model = Gemini(id="gemini-1.5-pro"),
        instructions=[
            "Given a user's startup idea, your goal is to refine that idea.",
            "Evaluate the originality of the idea by comparing it with existing concepts.",
            "Define the mission and objectives of the startup.",
            "IMPORTANT: All responses must be strings, not numbers or lists.",
            "Format your response exactly like this example:",
            '''{
                "originality": "Highly original with unique approach to...",
                "mission": "To revolutionize the way...",
                "objectives": "1. Achieve X, 2. Implement Y, 3. Develop Z..."
            }'''
        ],
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        response_model=IdeaClarification,
        structured_outputs=True,
        debug_mode=True,
    )

    market_research_agent: Agent = Agent(
        # model=Groq(id="llama-3.3-70b-versatile"),
        model=Gemini(id="gemini-1.5-pro"),
        tools=[GoogleSearch()],
        instructions=[
            "You are provided with a startup idea and the company's mission and objectives in JSON format.",
            "Estimate the total addressable market (TAM), serviceable available market (SAM), and serviceable obtainable market (SOM).",
            "Define target customer segments and their characteristics.",
            "Search the web for resources if you need to.",
            "Provide the response in JSON format with the following structure: {total_addressable_market, serviceable_available_market, serviceable_obtainable_market, target_customer_segments}",
        ],
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        response_model=MarketResearch,
        structured_outputs=True,
        debug_mode=True,
    )

    competitor_analysis_agent:Agent=Agent(
        # model=Groq(id="llama-3.3-70b-versatile"),
        model=Gemini(id="gemini-1.5-pro"),
        tools=[GoogleSearch()],
        instructions=[
            "You are provided with a startup idea and some market research related to the idea. ",
            "Identify existing competitors in the market. ",
            "Perform Strengths, Weaknesses, Opportunities, and Threats (SWOT) analysis for each competitor. ",
            "Assess the startup’s potential positioning relative to competitors.",
        ],
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        markdown=True,
        debug_mode=True,
    )

    report_agent:Agent=Agent(
        # model=Groq(id="llama3.3-70b-versatile"),
        model=Gemini(id="gemini-1.5-pro"),
        instructions=[
            "You are provided with a startup idea, its mission, objectives, market research, and competitor analysis. ",
            "Generate a comprehensive report summarizing the startup idea, its mission, objectives, market research, and competitor analysis. ",
            "Ensure the report is well-structured, informative, and actionable. ",
        ],
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        markdown=True,
        debug_mode=True,
    )

    def get_idea_clarification(self, startup_idea: str) -> Optional[IdeaClarification]:
        try:
            response: RunResponse = self.idea_clarifier_agent.run(
                f"""Please analyze this startup idea and provide a structured response:
                Startup Idea: {startup_idea}
                
                Provide your response in JSON format with string values only.
                Do not include markdown code blocks (```) in your response."""
            )

            if not response or not response.content:
                logger.warning("Empty Idea clarification response")
                return None
            
            # Clean the response of markdown code blocks
            content = response.content
            if isinstance(content, str):
                content = content.replace("```json", "").replace("```", "").strip()
                try:
                    data = json.loads(content)
                    return IdeaClarification(**data)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response")
                    return None
            
            if isinstance(response.content, IdeaClarification):
                return response.content
            
            logger.warning("Invalid response type")
            return None
            
        except Exception as e:
            logger.warning(f"Failed: {str(e)}")
            return None
   
   
    def get_market_research(self, startup_idea: str, idea_clarification: IdeaClarification) -> Optional[MarketResearch]:
        try:
            input_data = {
                "startup_idea": startup_idea,
                "originality": idea_clarification.originality,
                "mission": idea_clarification.mission,
                "objectives": idea_clarification.objectives
            }
            
            # Update instructions to ensure proper string format for target segments
            response: RunResponse = self.market_research_agent.run(
                f"""Analyze this startup information and provide market research:
                {json.dumps(input_data, indent=2)}
                
                Important:
                1. Do not include markdown code blocks (```) in your response
                2. Format target_customer_segments as a single string with segments separated by semicolons
                3. All values must be strings
                
                Example format:
                {{
                    "total_addressable_market": "Description of TAM...",
                    "serviceable_available_market": "Description of SAM...",
                    "serviceable_obtainable_market": "Description of SOM...",
                    "target_customer_segments": "Segment 1: [description]; Segment 2: [description]; Segment 3: [description]"
                }}"""
            )

            if not response or not response.content:
                logger.warning("Empty market research response")
                return None
            
            # Clean the response and handle string conversion
            content = response.content
            if isinstance(content, str):
                content = content.replace("```json", "").replace("```", "").strip()
                try:
                    data = json.loads(content)
                    # Ensure target_customer_segments is a string
                    if isinstance(data.get("target_customer_segments"), list):
                        segments = [f"{seg.get('segment_name', 'Unknown')}: {seg.get('characteristics', '')}" 
                                  for seg in data["target_customer_segments"]]
                        data["target_customer_segments"] = "; ".join(segments)
                    return MarketResearch(**data)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response")
                    return None
            
            if isinstance(response.content, MarketResearch):
                return response.content
            
            logger.warning("Invalid response type")
            return None
            
        except Exception as e:
            logger.warning(f"Failed: {str(e)}")
            return None
    
    def get_competitor_analysis(self, startup_idea:str, market_research:MarketResearch) -> Optional[str]:
        agent_input = {"startup_idea": startup_idea, **market_research.model_dump()}

        try:
            response: RunResponse = self.competitor_analysis_agent.run(json.dumps(agent_input, indent=4))

            # validation
            if not response or not response.content:
                logger.warning("Empty competitor analysis response")
            return response.content
        
        except Exception as e:
            logger.warning(f"Failed: {str(e)}")
        return None
    
    def run(self, startup_idea:str) -> Iterator[RunResponse]:
        logger.info(f"Generating a startup validation report for: {startup_idea}")

        idea_clarification: Optional[IdeaClarification] = self.get_idea_clarification(startup_idea)

        if idea_clarification is None:
            yield RunResponse(
                event=RunEvent.workflow_completed,
                content=f"Failed to generate a startup validation report for: {startup_idea}",
            )
            return
        
        market_research:Optional[MarketResearch] = self.get_market_research(startup_idea, idea_clarification)

        if market_research is None:
            yield RunResponse(
                event=RunEvent.workflow_completed,
                content=f"Failed to generate a startup validation report for: {startup_idea}",
            )
            return
        
        competitor_analysis: Optional[str] = self.get_competitor_analysis(startup_idea, market_research)

        final_response: RunResponse = self.report_agent.run(
            json.dumps(
                {
                    "startup_idea": startup_idea,
                    **idea_clarification.model_dump(),
                    **market_research.model_dump(),
                    "competitor_analysis": competitor_analysis,
                },
                indent=4,
            )
        )

        yield RunResponse(content=final_response.content, event=RunEvent.workflow_completed)


# Run the workflow if the script is executed directly
if __name__ == "__main__":
    from rich.prompt import Prompt

    # Get idea from user
    idea = Prompt.ask(
        "[bold]what is your startup idea?[/bold]\n",
        default="""An app known as project Ambience, which uses Ai to create Natural sounds mixes like thunder, rain, wind, etc. so that people can concentrate on their work, website link: https://app.projectambience.com/, website main page details: Project Ambience
Get deep work done with AI-tailored ambience mixes.
Tagline: AI-powered ambience spaces for focus, productivity, and relaxation.

Ambience Spaces
Focus: Block distractions, boost concentration, and enhance productivity.
Study: Stay motivated and absorb knowledge effortlessly.
Relax: Unwind with calming auditory spaces.
Sleep: Peaceful tones for restful sleep.
Backed by Neuroscience
Focus Retention: Improves focus by up to 40%.
Cortisol Levels: Optimized for relaxation and productivity.
Testimonials
"Listening to Nature Ambience helped me quit my music addiction. Lyrics are so distracting now!" – Zain, Co-Founder of Shoten.
"It helps me stay calm without haunting lyrics in my head." – Nura Zack, Interior Designer.
"Great for sleep, highly recommend it." – Shang Kang, Marketing Manager.
Pricing
Lifetime Free: $0
Access to Ambience Library, AI Generator, Pomodoro.
Up to 5 AI generations.
Add-On Plan: $5 One Time
Includes 50 AI generations and everything in Free.
Improve focus and productivity with Project Ambience.
Get Started Today!"""
    )

    # Convert the idea to a URL-safe string for use  in session_id
    url_safe_idea = idea.lower().replace(" ","-")

    startup_idea_validator = StartupIdeaValidator(
        description="Startup Idea Validator",
        session_id=f"validate-startup-idea-{url_safe_idea}",
        storage=SqlWorkflowStorage(
            table_name="validate_startup_ideas_workflow",
            db_file="tmp/workflows.db",
        ),
        debug_mode=True,
    )

    final_report: Iterator[RunResponse] = startup_idea_validator.run(startup_idea=idea)

    pprint_run_response(final_report, markdown=True)

