# This approach does not utilize docker instead uses ChromaDB locally, which is different from the provided documentation of PhiData.

from phi.agent import Agent
from phi.model.google import Gemini
from phi.knowledge.pdf import PDFKnowledgeBase
from phi.vectordb.chroma import ChromaDb

# we had to import GeminiEmbedder as by default phi uses OpenAI embedder.
from phi.embedder.google import GeminiEmbedder
import os
from dotenv import load_dotenv

load_dotenv()

os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')

pdf_path = "Attention_paper.pdf"
vector_db_path = "vector_db"

if not os.path.exists(vector_db_path):
    os.makedirs(vector_db_path)
    print(f"Created vector database directory at {vector_db_path}")

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found at {pdf_path}")
print(f"PDF file found at {pdf_path}")

# Create GeminiEmbedder with the specified model and task type
embedder = GeminiEmbedder(
    model="models/embedding-001",
    task_type="retrieval_document",
    api_key=os.getenv('GOOGLE_API_KEY')
)

# We need to manually add the embedder parameter to the database, as by default it assumes OpenAI embedder.
knowledge_base = PDFKnowledgeBase(
    path=pdf_path,
    vector_db=ChromaDb(
        collection="attention_paper",
        path=vector_db_path,
        embedder=embedder
    )
)

print("Loading knowledge base...")
knowledge_base.load(upsert=True)
print("Knowledge base loaded successfully")

agent = Agent(
    model=Gemini(id="gemini-1.5-pro"), 
    knowledge_base=knowledge_base,
    add_context=True,
    search_knowledge=False,
    markdown=True,
    debug_mode=True,
    description="You are an expert at analyzing academic papers. You have access to the content of a paper about Attention mechanisms.",
    instructions=[
        "Always search the knowledge base before answering questions",
        "Provide concise answers based on the content found",
        "If you can't find specific information, say so explicitly"
    ]
    # there is this "tool_choice" parameter in Agent class, which can be used to specify if the tool
    # should be used or not, if we want to force the agent to use the tool, we can do that too.
    # By default, it is on 'auto' mode, which means the agent will decide if the tool should be used or not.

)

# For Agentic RAG, we need to set search_knowledge to True.
# And add read_chat_history to True.


agent.print_response("What is this paper about? Give a brief summary.", stream=True)


"""
# Output of the above code:

┏━ Message ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                                 ┃
┃ What is this paper about? Give a brief summary.                                 ┃
┃                                                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┏━ Response (6.7s) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                                                 ┃
┃ This paper explores attention mechanisms in the context of neural networks,     ┃
┃ specifically within the Transformer model architecture. It details how          ┃
┃ attention functions map queries and key-value pairs to outputs, which are       ┃
┃ weighted sums. The paper also visualizes attention, demonstrating its ability   ┃
┃ to handle long-distance dependencies and resolve anaphora.  The authors analyze ┃
┃ different attention heads within the model, showing they learn distinct tasks   ┃
┃ related to sentence structure.                                                  ┃
┃                                                                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

"""