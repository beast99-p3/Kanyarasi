"""
LLM Client for Google Gemini
"""

import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_text(self, prompt: str) -> str:
        """
        Generates text using the Gemini API.

        Args:
            prompt: The input prompt.

        Returns:
            The generated text.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"An error occurred: {e}"
