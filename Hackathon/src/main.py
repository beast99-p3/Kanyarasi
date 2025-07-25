"""
Main application entry point.
"""

import os
from dotenv import load_dotenv
from planner import Planner
from executor import Executor
from memory import MemoryManager
from llm_client import GeminiClient

def main():
    """
    Main function to run the agentic AI application.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found. Please set it in a .env file.")
        return

    # Initialize components
    llm_client = GeminiClient(api_key=gemini_api_key)
    planner = Planner(llm_client)
    # Define some dummy tools for the executor
    tools = {
        "search": lambda: "This is a dummy search result."
    }
    executor = Executor(llm_client, tools)
    memory = MemoryManager()

    print("Agentic AI Assistant")
    print("Enter 'quit' to exit.")

    while True:
        goal = input("You: ")
        if goal.lower() == 'quit':
            break

        # 1. Plan
        plan = planner.plan(goal)
        print(f"Agent: I have a plan:")
        for task in plan:
            print(f"- {task['task']}")

        # 2. Execute
        results = []
        for task in plan:
            result = executor.execute(task)
            results.append(result)
            print(f"Agent: Executed task '{task['task']}', result: {result}")
            memory.add_log(f"Executed task '{task['task']}', result: {result}")


        # 3. Generate final response
        final_prompt = f"Based on the following results, provide a final answer to the user's goal: '{goal}'.\n\nResults:\n" + "\n".join(results)
        final_response = llm_client.generate_text(final_prompt)

        print(f"Agent: {final_response}")
        memory.add_log(f"Final response: {final_response}")

if __name__ == "__main__":
    main()
