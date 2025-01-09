import json
from pathlib import Path
from typing import Iterator
import hashlib
import webbrowser

from pydantic import BaseModel, Field

from phi.agent import Agent, RunResponse
# from phi.model.groq import Groq
from phi.model.google import Gemini
from phi.run.response import RunEvent
from phi.storage.workflow.sqlite import SqlWorkflowStorage
from phi.utils.log import logger
from phi.utils.pprint import pprint_run_response
from phi.workflow import Workflow

import os
from dotenv import load_dotenv

load_dotenv()

os.environ["google_api_key"] = os.getenv("google_api_key")
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


def hash_string_sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def open_html_file(file_path: str | Path) -> None:
    path = Path(file_path).absolute().as_uri()
    webbrowser.open(path)

games_dir = Path(__file__).parent.joinpath("games")
games_dir.mkdir(parents=True, exist_ok=True)
game_output_path = games_dir/"game_output_file.html"
game_output_path.unlink(missing_ok=True)


class GameOutput(BaseModel):
    reasoning: str = Field(..., description="Explain your reasoning")
    code: str = Field(..., description="The html5 code for the game")
    instructions: str = Field(..., description="Instructions how to play the game")


class QAOutput(BaseModel):
    reasoning: str = Field(..., description="Explain your reasoning")
    correct: bool = Field(..., description = "Does the game pass your criteria?")

class GameGenerator(Workflow):
    description: str = "Generator for single-page HTML5 Games"

    game_developer: Agent = Agent(
        name="Game Developer Agent",
        description="You are a game developer who creates simple HTML5 Canvas games. Generate complete, working code with no placeholders.",
        # model=Groq(id="llama3-70b-8192"),
        model=Gemini(id="gemini-1.5-pro"),
        instructions=[
            "Create a working HTML5 game with these components:",
            "1. HTML: Canvas element and basic structure",
            "2. CSS: Simple styling for canvas and text",
            "3. JavaScript:",
            "   - Game objects (player, enemies)",
            "   - Basic movement and controls",
            "   - Simple collision detection",
            "   - Score and lives tracking",
            "   - Game states (start, play, end)",
            "Format your response as valid JSON with:",
            "- reasoning: Explain your implementation",
            "- code: Complete HTML file with all code",
            "- instructions: How to play the game"
        ],
        response_model=GameOutput,
        add_chat_history_to_messages=True,
        num_history_messages=2,
    )

    qa_agent: Agent = Agent(
        name="QA Agent",
        description="You are a game QA engineer who tests simple HTML5 games for completeness and functionality.",
        # model=Groq(id="llama3-70b-8192"),
        model=Gemini(id="gemini-1.5-pro"),
        instructions=[
            "Check if the game code includes:",
            "1. Basic Features:",
            "   - Canvas setup and rendering",
            "   - Player movement with arrow keys",
            "   - Enemy spawning and movement",
            "   - Collision detection",
            "2. Game Elements:",
            "   - Score display",
            "   - Lives system",
            "   - Start and end screens",
            "Format response as JSON with:",
            "- reasoning: List what works and what's missing",
            "- correct: true if all features work, false if any are missing"
        ],
        response_model=QAOutput,
        add_chat_history_to_messages=True,
        num_history_messages=2,
    )

    def run(self, game_description: str) -> Iterator[RunResponse]:
        logger.info(f"Game Description: {game_description}")
        max_attempts = 3
        attempt = 0
        previous_code = ""
        previous_feedback = ""
        
        while attempt < max_attempts:
            attempt += 1
            logger.info(f"Attempt {attempt} of {max_attempts}")
            
            # Enhance description with previous attempt info
            if previous_code and previous_feedback:
                enhanced_description = {
                    "original_description": game_description,
                    "previous_code": previous_code,
                    "qa_feedback": previous_feedback,
                    "instructions": "Analyze the previous code and QA feedback. Keep working parts and improve the identified issues. Ensure the response is valid JSON matching the GameOutput model."
                }
                game_output = self.game_developer.run(json.dumps(enhanced_description, indent=2))
            else:
                game_output = self.game_developer.run(game_description)
            
            if not game_output or not game_output.content or not isinstance(game_output.content, GameOutput):
                logger.warning(f"Invalid game output format on attempt {attempt}")
                if attempt == max_attempts:
                    yield RunResponse(
                        run_id=self.run_id,
                        event=RunEvent.workflow_completed,
                        content="Failed to generate valid game output after maximum attempts."
                    )
                    return
                continue
            
            game_code = game_output.content.code
            logger.info(f"Game Code Generated - Attempt {attempt}")
            
            # Store current code for next iteration
            previous_code = game_code
            
            # QA Check with context
            qa_input = {
                "attempt_number": attempt,
                "game_description": game_description,
                "game_code": game_code,
                "previous_feedback": previous_feedback if previous_feedback else "First attempt"
            }
            
            qa_output = self.qa_agent.run(json.dumps(qa_input, indent=2))
            
            if not qa_output or not qa_output.content or not isinstance(qa_output.content, QAOutput):
                logger.warning(f"Invalid QA output format on attempt {attempt}")
                if attempt == max_attempts:
                    yield RunResponse(
                        run_id=self.run_id,
                        event=RunEvent.workflow_completed,
                        content="QA check failed to provide valid output after maximum attempts."
                    )
                    return
                continue
            
            # Store current feedback for next iteration
            previous_feedback = qa_output.content.reasoning
            
            logger.info(f"QA Result - Attempt {attempt}: {qa_output.content.correct}")
            
            if qa_output.content.correct:
                game_output_path.write_text(game_code)
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content=f"Game successfully generated after {attempt} attempts!\n\n{game_output.content.instructions}"
                )
                return
            elif attempt == max_attempts:
                logger.warning("Maximum attempts reached. Saving last version.")
                game_output_path.write_text(game_code)
                yield RunResponse(
                    run_id=self.run_id,
                    event=RunEvent.workflow_completed,
                    content=f"Game generated with potential issues after {max_attempts} attempts.\nQA notes:\n{qa_output.content.reasoning}\n\n{game_output.content.instructions}"
                )
                return
        
        yield RunResponse(
            run_id=self.run_id,
            event=RunEvent.workflow_completed,
            content=f"Failed to generate perfect game after {max_attempts} attempts."
        )
        
if __name__ == "__main__":
    from rich.prompt import Prompt

    game_description = Prompt.ask(
            "[bold]Describe the game you want to make (keep it simple)[/bold]\n✨",
            default="Create a simple space shooter game with these features:\n"
                   "1. Basic Game:\n"
                   "- Blue triangle spaceship at bottom of screen\n"
                   "- Arrow keys to move left/right\n"
                   "- Spacebar to shoot\n"
                   "- Red circles as asteroids falling from top\n\n"
                   "2. Game Rules:\n"
                   "- Hit asteroids for 10 points each\n"
                   "- Three lives\n"
                   "- Game over when lives are gone\n\n"
                   "3. Technical:\n"
                   "- Canvas: 800x600 pixels\n"
                   "- Simple collision detection\n"
                   "- Score display in top-left\n"
                   "- Lives display in top-right\n"
                   "- Start and Game Over screens"
        )
    
    hash_of_description = hash_string_sha256(game_description)

    game_generator = GameGenerator(
        session_id=f"game-gen-{hash_of_description}",
        storage=SqlWorkflowStorage(
            table_name = "game_generator_workflows",
            db_file="tmp/workflows.db",
        ),
    )


    result: Iterator[RunResponse] = game_generator.run(game_description=game_description)


    pprint_run_response(result)

    if game_output_path.exists():
        open_html_file(game_output_path)
