from typing import Dict, Any
from .memory import AgentMemory
from .tools import AgentTools

class Agent:
    """
    Agentic AI Agent that generates a comprehensive chatbot development plan.
    """
    
    def __init__(self, llm_client):
        self.llm = llm_client
        self.memory = AgentMemory()
        self.tools = AgentTools()

    def _generate_plan(self, goal: str) -> list[str]:
        """Acts as the 'Planner' to break down the goal into steps."""
        prompt = f"""
        As an expert AI project manager, your task is to create a high-level, strategic plan to achieve the following goal.
        Break down the goal into a numbered list of 4-6 actionable sub-tasks. Each sub-task should be a clear, concise step.
        Do not explain the steps, just provide the list.

        **Goal:** {goal}

        **Example Output:**
        1. Design the NLU and Intent/Entity Schema
        2. Develop the Core Dialog Management and State Tracking
        3. Implement Response Generation with Gemini API
        4. Design and Build the Knowledge Base
        5. Plan the Deployment and CI/CD Pipeline
        """
        response = self.llm.generate_text(prompt)
        # Parse the numbered list into a Python list
        plan = [line.strip().split('. ', 1)[1] for line in response.split('\n') if '. ' in line]
        return plan

    def _execute_step(self, step: str, goal: str) -> str:
        """Acts as the 'Executor' to generate detailed content for a single step."""
        prompt = f"""
        As a world-class AI architect, your task is to provide an exceptionally detailed, professional-grade implementation plan for the following sub-task.
        Your output must be exhaustive, technically precise, and formatted in clean Markdown. Provide code snippets, examples, and justifications.

        **Overall Goal:** {goal}
        **Current Sub-Task to Execute:** {step}

        Provide a comprehensive breakdown covering the following where applicable:
        - **A. In-Depth Sub-Tasks:** Break this step down even further.
        - **B. Professional Tool Recommendations:** Justify choices (e.g., spaCy vs. NLTK, FastAPI vs. Flask, Pinecone vs. FAISS).
        - **C. Actionable Implementation Details:** Provide directory structures, data schemas, and robust pseudo-code or Python snippets.
        - **D. Concrete Examples:** Show how to handle a sample input or what a sample output should look like.
        """
        return self.llm.generate_text(prompt)

    def _generate_conclusion(self, goal: str, plan_steps: list[str], execution_results: list[str]) -> str:
        """Generates a concluding summary of the development plan."""
        results_text = ""
        for i, (step, result) in enumerate(zip(plan_steps, execution_results)):
            results_text += f"### Step {i+1}: {step}\n{result}\n\n"

        prompt = f"""
        As a senior AI project lead, your task is to write a concise executive summary and conclusion for the following development plan.
        Do not repeat the plan verbatim. Instead, synthesize the key insights, highlight the overall strategy, and provide final recommendations.

        **Overall Goal:** {goal}

        **Completed Plan Details:**
        {results_text}

        **Your Summary Should Include:**
        1.  **Executive Summary:** A brief overview of the project's scope and the proposed solution.
        2.  **Key Strategic Decisions:** Highlight the most important choices made in the plan (e.g., choice of NLU engine, deployment platform).
        3.  **Next Steps:** Recommend the immediate next actions for the development team.
        4.  **Final Outlook:** A concluding statement on the project's potential for success.
        """
        return self.llm.generate_text(prompt)

    def process_goal(self, goal: str) -> Dict[str, Any]:
        """
        Generates a detailed development plan by simulating a Planner-Executor-Summarizer workflow.
        """
        try:
            # 1. Planner: Generate the high-level plan
            plan_steps = self._generate_plan(goal)
            
            if not plan_steps:
                raise ValueError("The planner did not return any steps. The response may have been blocked or empty.")

            # 2. Executor: Execute each step to get detailed results
            execution_results = []
            for step in plan_steps:
                result_for_step = self._execute_step(step, goal)
                execution_results.append(result_for_step)

            # 3. Summarizer: Generate a final conclusion
            final_answer = self._generate_conclusion(goal, plan_steps, execution_results)

            # Store the interaction in memory
            self.memory.add_interaction("user", goal)
            self.memory.add_interaction("agent", final_answer)

            return {
                "goal": goal,
                "plan": plan_steps,
                "results": execution_results,
                "response": final_answer,
                "memory": self.memory.get_recent_interactions()
            }

        except Exception as e:
            # Fallback in case of an API or other error
            return {
                "goal": goal,
                "plan": ["An error occurred during planning."],
                "results": [f"Error details: {str(e)}"],
                "response": "Sorry, I was unable to generate a development plan. Please check the API key and try again.",
                "memory": []
            }
