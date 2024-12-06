from crewai import Crew,Process
from tasks import research_task,write_task
from agents import news_researcher, news_writer

## Forming the code

crew=Crew(
    agents = [news_researcher,news_writer],
    task=[research_task,write_task],
    process=Process.sequential,

)

result = crew.kickoff(inputs= {'topic':'AI in Gaming'})
print(result)