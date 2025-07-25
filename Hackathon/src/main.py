"""Main entry point for the agentic application."""

import os
import asyncio
from dotenv import load_dotenv
from planner import Planner
from executor import Executor
from memory import MemoryManager
from llm_client import GeminiClient

async def run_agent(goal: str):
    """
    Initializes and runs the agent to achieve a specific goal.
    
    This function orchestrates the planning, execution, and response generation.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")

    # Initialize all the necessary components
    llm_client = GeminiClient(api_key=gemini_api_key)
    memory = MemoryManager()
    
    # The executor is where you can define and connect tools.
    # For now, we have a placeholder.
    tools = {
        "search": lambda q: f"Search results for '{q}'..."
    }
    executor = Executor(llm_client, tools)
    planner = Planner(llm_client)

    # 1. Create a plan to achieve the goal
    plan = planner.plan(goal)
    memory.add_log(f"Goal: {goal}\nPlan: {[task['task'] for task in plan]}")

    # 2. Execute the plan task by task
    results = []
    for task in plan:
        result = executor.execute(task)
        results.append(result)
        memory.add_log(f"Executed task '{task['task']}': {result}")

    # 3. Generate a final, consolidated response
    summary_prompt = (
        f"Based on the following results, provide a final, comprehensive answer to the user's goal: '{goal}'.\n\n"
        f"Results:\n" + "\n".join(f"- {res}" for res in results)
    )
    final_response = llm_client.generate_text(summary_prompt)
    memory.add_log(f"Final response generated: {final_response}")

    return plan, results, final_response

def cli_main():
    """Provides a command-line interface for interacting with the agent."""
    print("🤖 Agentic AI Assistant (CLI Mode)")
    print("Enter 'quit' to exit.")

    while True:
        goal = input("You: ")
        if goal.lower() == 'quit':
            break
        
        try:
            plan, _, final_response = asyncio.run(run_agent(goal))

            print("\n📋 My Plan:")
            for task in plan:
                print(f"- {task['task']}")

            print(f"\n✅ Final Answer:\n{final_response}\n")
        except Exception as e:
            print(f"\n🔥 An error occurred: {e}\n")

if __name__ == "__main__":
    cli_main()
