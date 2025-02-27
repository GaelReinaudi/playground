from crewai import Agent, Task, Crew, Process
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from dotenv import load_dotenv
import os

# Load environment variables from root directory
load_dotenv(dotenv_path='../../.env')

def search_web(query: str) -> str:
    """Search the web for information about a given query."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

class PersonalAssistantCrew:
    def __init__(self):
        # Initialize tools
        self.search_tool = Tool(
            name="web_search",
            func=search_web,
            description="Search the web for information about a given query"
        )

        # Create the team of agents
        self.researcher = Agent(
            role='Research Specialist',
            goal='Find and analyze information accurately',
            backstory="""You are an expert researcher with a keen eye for detail and 
            the ability to quickly find and verify information. You have years of 
            experience in data analysis and fact-checking.""",
            verbose=True,
            allow_delegation=True,
            tools=[self.search_tool]
        )

        self.writer = Agent(
            role='Communication Expert',
            goal='Craft clear, engaging, and personalized responses',
            backstory="""You are a skilled communicator with expertise in writing 
            and interpersonal communication. You excel at adapting your tone and 
            style to match the context and audience.""",
            verbose=True,
            allow_delegation=True
        )

        self.assistant = Agent(
            role='Personal Assistant Manager',
            goal='Coordinate tasks and maintain personal context',
            backstory="""You are a highly organized personal assistant with excellent 
            management skills. You maintain context of conversations and user preferences,
            and coordinate other team members to provide the best possible assistance.""",
            verbose=True,
            allow_delegation=True
        )

    def handle_request(self, user_input, context=None):
        # Define tasks for the crew
        research_task = Task(
            description=f"""Research relevant information for: {user_input}
            Consider any context provided: {context if context else 'No additional context'}
            Focus on finding accurate and relevant information.""",
            agent=self.researcher,
            expected_output="Detailed research findings about the query"
        )

        response_task = Task(
            description=f"""Create a personalized response based on the research.
            Use the research findings to craft a helpful and engaging response.
            Maintain a consistent and appropriate tone.""",
            agent=self.writer,
            expected_output="Personalized and well-crafted response"
        )

        coordination_task = Task(
            description=f"""Coordinate the final response and maintain context.
            Ensure the response addresses the user's needs and aligns with any previous
            interactions or preferences.""",
            agent=self.assistant,
            expected_output="Final coordinated response with context"
        )

        # Create and run the crew
        crew = Crew(
            agents=[self.researcher, self.writer, self.assistant],
            tasks=[research_task, response_task, coordination_task],
            verbose=True,
            process=Process.sequential
        )

        result = crew.kickoff()
        return result

# Example usage
if __name__ == "__main__":
    assistant = PersonalAssistantCrew()
    
    # Example interaction
    user_query = "Can you help me plan a healthy meal for dinner?"
    context = "User is vegetarian and prefers Mediterranean cuisine"
    
    print("Starting the personal assistant...")
    print(f"Query: {user_query}")
    print(f"Context: {context}")
    
    response = assistant.handle_request(user_query, context)
    print("\nResponse:")
    print(response) 