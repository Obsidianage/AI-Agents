"""
WORKFLOW TUTORIAL: Blog Post Generator

This example demonstrates how to build a workflow that:
1. Searches for articles on a topic
2. Generates a blog post from those articles
3. Caches results for future use

Key Concepts:
- Workflows: Multi-step processes with state management
- Pydantic Models: For data validation and structure
- Agents: Specialized AI workers for specific tasks
- Caching: Storing results for reuse

Architecture Overview:
1. Data Models (Input/Output structures)
2. Agents (Workers that perform tasks)
3. Workflow (Orchestrator that manages the process)
4. Storage (Caching and persistence layer)
"""

### Step 1: Import Required Libraries ###
# Core Python libraries
import json  
from typing import Optional, Iterator  

# Data modeling
from pydantic import BaseModel, Field  

# Phi framework components
from phi.model.google import Gemini  
from phi.agent import Agent  
from phi.workflow import Workflow, RunResponse, RunEvent  
from phi.storage.workflow.sqlite import SqlWorkflowStorage  
from phi.tools.duckduckgo import DuckDuckGo 
from phi.utils.pprint import pprint_run_response 
from phi.utils.log import logger 
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


### Step 2: Define Data Models ###
# Purpose: Create structured data formats for:
# - Input validation
# - Type safety
# - Clear documentation
# - Consistent data handling

class NewsArticle(BaseModel):
    """
    Represents a single news article.
    
    Fields:
    - title: The article's headline
    - url: Where to find the article
    - summary: Brief overview of content (optional)
    
    Usage:
    article = NewsArticle(
        title="Breaking News",
        url="https://example.com",
        summary="A brief summary..."
    )
    """
    title: str = Field(
        ...,  # ... means required
        description="Title of the article."
    )
    url: str = Field(
        ...,
        description="Link to the article."
    )
    summary: Optional[str] = Field(
        ...,
        description="Summary of the article if available"
    )

class SearchResults(BaseModel):
    """
    Container for multiple NewsArticle objects.
    
    Purpose:
    - Groups related articles
    - Ensures list contains valid NewsArticle objects
    - Used as output format for searcher agent
    
    Usage:
    results = SearchResults(articles=[article1, article2])
    """
    articles: list[NewsArticle]

### Step 3: Create Workflow ###
class BlogpostGenerator(Workflow):
    """
    A workflow that generates blog posts from web articles.
    
    Components:
    1. Searcher Agent: Finds relevant articles
    2. Writer Agent: Creates blog post from articles
    3. Run Method: Orchestrates the process
    4. Caching: Stores results for reuse
    
    Flow:
    1. Check cache for existing post
    2. If not found:
       a. Search for articles
       b. Generate blog post
       c. Cache result
    3. Return post (from cache or newly generated)
    """

    # Agent 1: Searcher
    searcher: Agent = Agent(
        model=Gemini(id="gemini-1.5-pro"),
        tools=[DuckDuckGo()],  # Provides web search capability
        instructions=[
            "Given a topic, search for 20 articles and return the 5 most relevant articles.",
            "Focus on recent and authoritative sources.",
            "Ensure articles are directly relevant to the topic."
        ],
        response_model=SearchResults,  # Enforces structured output
    )

    # TODO: Add Writer Agent
    # Key Components Needed:
    # 1. Instructions:
    #    - Format requirements (sections, structure)
    #    - Style guidelines (NYT-worthy)
    #    - Source attribution rules
    # 2. No response_model needed (free-form text output)
    # 3. Consider adding temperature/creativity settings

    writer: Agent = Agent(
        model=Gemini(id="gemini-1.5-pro"),
        instructions=[
            "You will be provided with a topic and a list of top articles on that topic.",
            "Carefully read each article and generate a New York Times worthy blog post on that topic.",
            "Break the blog post into sections and provide key takeaways at the end.",
            "Make sure the title is catchy and engaging.",
            "Always provide sources, do not make up information or sources.",
        ],
    )





    def run(self, topic: str, use_cache: bool = True) -> Iterator[RunResponse]:
        """run method for the workflow

        Args:
            topic: The topic to search for
            use_cache: Whether to use cached results
        
        Returns:
            Iterator[RunResponse]: A stream of responses from the workflow
        """
        logger.info(f"Generating blog post for topic: {topic}") #logger.info is a function that logs a message to the console

        # Use the cached blog post if use_cache is True
        if use_cache and "blog_post" in self.session_state: #self.session_state is a dictionary that stores the state of the workflow
            logger.info("Checking if cached blog post is available...")
            for cached_blog_post in self.session_state["blog_post"]: #self.session_state["blog_post"] is a list of dictionaries that store the cached blog posts
                if cached_blog_post["topic"] == topic: #cached_blog_post["topic"] is the topic of the cached blog post
                    logger.info("Found cached blog post.")
                    yield RunResponse( #yield is a keyword that returns a value from a function 
                        # in this case, it returns a RunResponse object which is a response from the workflow
                        run_id=self.run_id, #self.run_id is the id of the run
                        event = RunEvent.workflow_completed, #RunEvent.workflow_completed is an event that indicates the workflow has completed
                        content = cached_blog_post["blog_post"], #cached_blog_post["blog_post"] is the blog post that is being returned
                    )
                    return 
        
        # Setp 1: search the web for articles on the topic
        num_tries = 0
        search_results:Optional[SearchResults]= None
        # Run until we get a valid search results
        while search_results is None and num_tries < 3:
            try:
                num_tries+=1
                searcher_response:RunResponse = self.searcher.run(topic)
                if(
                    searcher_response
                    and searcher_response.content
                    and isinstance(searcher_response.content,SearchResults)
                ):
                    logger.info(f"Searcher found{len(searcher_response.content.articles)} articles.")
                    search_results = searcher_response.content
                else:
                    logger.warning("Searcher response invalid, trying again...")
            except Exception as e:
                logger.warning(f"Error during search: {e}")
        
        # If no search_results are found , end the workflow
        if search_results is None or len(search_results.articles) == 0:
            yield RunResponse(run_id=self.run_id, event=RunEvent.workflow_completed, content=f"Sorry, could not find any articles on the topic: {topic}")
            return
        

        # step 2: Write a log post
        logger.info("Writing blog post...")
        # Prepare the input for the writer
        writer_input = {
            "topic":topic,
            "articles":[v.model_dump() for v in search_results.articles],
        }

        # Run the writer and yield the response
        yield from self.writer.run(json.dumps(writer_input, indent=4), stream=True)

        # Save the blog post in session state for future runs
        if "blog_post" not in self.session_state:
            self.session_state["blog_post"] = []
        self.session_state["blog_post"].append({
            "topic":topic,
            "blog_post":self.writer.run_response.content,
        })


topic = "Narndra Modi a fraud leader"

# Create a workflow instance
generate_blog_post = BlogpostGenerator(
    session_id = f"generate-blog-post-on-{topic}",
    storage=SqlWorkflowStorage(
        table_name="generate_blog_post_workflows",
        db_file="peripherals/workflows.db",
    ),
)

# Run workflow
blog_post: Iterator[RunResponse] = generate_blog_post.run(topic=topic, use_cache=True)


# Print the blog post
pprint_run_response(blog_post, markdown=True)
