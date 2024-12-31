# typer is a library for building CLI applications.
import typer
from typing import Optional, List
from phi.agent import Agent
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.chroma import ChromaDb
from phi.model.google import Gemini
from phi.embedder.google import GeminiEmbedder
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# we are using the embeddings from the gemini model as by default the phidata uses openai embeddings
# And we changed the database to chroma db as the default pgvector is not working with the gemini model
# There seem to be some dimentionality issues with the gemini model and I was unable to fix it 

"""The Problem:
pgvector requires the vector dimensions to be specified when creating the table
Once created, all vectors must match that dimension exactly
The table was created expecting 1536 dimensions (OpenAI's default)
But Gemini embeddings are 768 dimensions
This caused the "expected 1536 dimensions, not 768" error

What I tried:
Used ChromaDB which is more flexible
It automatically adapts to whatever dimensions the embedder provides
"""

embedder = GeminiEmbedder(
    model_name="models/embedding-001",
    task_type="retrieval_document",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# Initialize knowledge base with ChromaDB
knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=ChromaDb(
        collection="recipes",
        path="vector_db",
        embedder=embedder
    ),
)

# Load the knowledge base 
knowledge_base.load(upsert=True)
storage = SqlAgentStorage(db_file="agent_storage.db", table_name="pdf_agent")

def pdf_agent(new:bool = False, user:str = "user"):
    session_id:Optional[str] = None

    if not new:
        existing_sessions: List[str] = storage.get_all_session_ids(user)
        if len(existing_sessions) > 0:
            session_id = existing_sessions[0]

    agent = Agent(
        model=Gemini(model_name="gemini-1.5-pro"),
        session_id=session_id,
        user_id=user,
        knowledge_base=knowledge_base,
        storage=storage,
        show_tool_calls=True,
        read_chat_history=True,
    )
    
    if session_id is None:
        session_id = agent.session_id
        print(f"Started new session with id: {session_id}")
    else:
        print(f"Resumed session with id: {session_id}")

    agent.cli_app(markdown=True)

if __name__ == "__main__":
    typer.run(pdf_agent)
"""
# This approach is not storing the chat history in the database. 
# And when i rerun the code the model is not able to recall the previous chat history.
# I think using the default OpenAI embeddings is the best approach for now.
"""

