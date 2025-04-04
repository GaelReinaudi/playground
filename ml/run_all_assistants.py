import asyncio
import io
import os
import sys
from contextlib import redirect_stdout
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the assistants
from crewai_assistant.personal_assistant import PersonalAssistantCrew
from langgraph_assistant.personal_assistant import EmailAssistant as LangGraphAssistant
from metagpt_assistant.personal_assistant import PersonalAssistant as MetaGPTAssistant


def create_log_directory():
    """Create a logs directory if it doesn't exist."""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir


async def run_all_assistants():
    log_dir = create_log_directory()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Test queries
    test_queries = [
        ("Can you help me plan a healthy meal for dinner?", "User is vegetarian and prefers Mediterranean cuisine"),
        ("I need help organizing my weekly schedule and setting priorities.", None),
        ("I need help developing a workout routine that fits my busy schedule. I prefer morning workouts and have about 30 minutes available.", None)
    ]

    # Run CrewAI Assistant
    print("Running CrewAI Assistant...")
    crew_assistant = PersonalAssistantCrew()
    with open(os.path.join(log_dir, f'crewai_output_{timestamp}.txt'), 'w') as f:
        for query, context in test_queries:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Query: {query}\n")
            f.write(f"Context: {context}\n")
            f.write(f"{'=' * 80}\n\n")

            # Capture stdout and write to file
            output = io.StringIO()
            with redirect_stdout(output):
                response = crew_assistant.handle_request(query, context)

            f.write(output.getvalue())
            f.write("\nResponse:\n")
            f.write(str(response))
            f.write("\n")

    # Run LangGraph Assistant
    print("Running LangGraph Assistant...")
    lang_assistant = LangGraphAssistant()
    with open(os.path.join(log_dir, f'langgraph_output_{timestamp}.txt'), 'w') as f:
        for query, _ in test_queries:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Query: {query}\n")
            f.write(f"{'=' * 80}\n\n")

            # Capture stdout and write to file
            output = io.StringIO()
            with redirect_stdout(output):
                response = lang_assistant.handle_request(query)

            f.write(output.getvalue())
            f.write("\nResponse:\n")
            f.write(str(response))
            f.write("\n")

    # Run MetaGPT Assistant
    print("Running MetaGPT Assistant...")
    meta_assistant = MetaGPTAssistant()
    with open(os.path.join(log_dir, f'metagpt_output_{timestamp}.txt'), 'w') as f:
        for query, _ in test_queries:
            f.write(f"\n{'=' * 80}\n")
            f.write(f"Query: {query}\n")
            f.write(f"{'=' * 80}\n\n")

            # Capture stdout and write to file
            output = io.StringIO()
            with redirect_stdout(output):
                response = await meta_assistant.process_request(query)

            f.write(output.getvalue())
            f.write("\nResponse:\n")
            f.write(str(response))
            f.write("\n")


if __name__ == "__main__":
    print("Starting all personal assistants...")
    asyncio.run(run_all_assistants())
    print("All assistants completed. Check the logs directory for outputs.")
