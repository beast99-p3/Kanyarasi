"""
Main application entry point.
"""

import os
from dotenv import load_dotenv
from planner import Planner
from executor import Executor
from memory import MemoryManager
from llm_client import GeminiClient

async def run_agent(goal: str):
    """
    Runs the agentic AI application for a given goal.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in a .env file.")

    # Initialize components
    llm_client = GeminiClient(api_key=gemini_api_key)
    planner = Planner(llm_client)
    # Define some dummy tools for the executor
    tools = {
        "search": lambda: "This is a dummy search result."
    }
    executor = Executor(llm_client, tools)
    memory = MemoryManager()

    # 1. Plan
    plan = planner.plan(goal)
    
    # 2. Execute
    results = []
    for task in plan:
        result = executor.execute(task)
        results.append(result)
        memory.add_log(f"Executed task '{task['task']}', result: {result}")

    # 3. Generate final response
    final_prompt = f"Based on the following results, provide a final answer to the user's goal: '{goal}'.\n\nResults:\n" + "\n".join(results)
    final_response = llm_client.generate_text(final_prompt)
    memory.add_log(f"Final response: {final_response}")

    return plan, results, final_response

def main():
    """
    Main function to run the agentic AI application from the command line.
    """
    print("Agentic AI Assistant")
    print("Enter 'quit' to exit.")

    while True:
        goal = input("You: ")
        if goal.lower() == 'quit':
            break
        
        import asyncio
        plan, results, final_response = asyncio.run(run_agent(goal))

        print(f"Agent: I have a plan:")
        for task in plan:
            print(f"- {task['task']}")

        print(f"Agent: Executed tasks and got results.")

        print(f"Agent: {final_response}")


if __name__ == "__main__":
    main()
