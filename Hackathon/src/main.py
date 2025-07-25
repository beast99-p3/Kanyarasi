
import os, asyncio
from dotenv import load_dotenv
from planner import Planner
from executor import Executor
from memory import MemoryManager
from llm_client import GeminiClient

async def run_agent(goal: str):
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not found in .env file.")
    llm = GeminiClient(api_key=key)
    memory = MemoryManager()
    tools = {"search": lambda q: f"Search results for '{q}'..."}
    executor = Executor(llm, tools)
    planner = Planner(llm)
    plan = planner.plan(goal)
    memory.add_log(f"Goal: {goal}\nPlan: {[t['task'] for t in plan]}")
    results = [executor.execute(task) for task in plan]
    for i, task in enumerate(plan):
        memory.add_log(f"Executed task '{task['task']}': {results[i]}")
    summary = f"Based on the following results, provide a final, comprehensive answer to the user's goal: '{goal}'.\n\nResults:\n" + "\n".join(f"- {r}" for r in results)
    final_response = llm.generate_text(summary)
    memory.add_log(f"Final response generated: {final_response}")
    return plan, results, final_response

def cli_main():
    print("🤖 Agentic AI Assistant (CLI Mode)")
    print("Enter 'quit' to exit.")
    while True:
        goal = input("You: ")
        if goal.lower() == 'quit': break
        try:
            plan, _, final_response = asyncio.run(run_agent(goal))
            print("\n📋 My Plan:")
            for t in plan: print(f"- {t['task']}")
            print(f"\n✅ Final Answer:\n{final_response}\n")
        except Exception as e:
            print(f"\n🔥 An error occurred: {e}\n")

if __name__ == "__main__": cli_main()
