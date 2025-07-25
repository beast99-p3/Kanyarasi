"""A dedicated client for interacting with the Google Gemini API."""

import google.generativeai as genai

class GeminiClient:
    """Handles all communication with the Google Gemini model."""
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        # It's good practice to specify the model. 'gemini-pro' is a solid choice.
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_text(self, prompt: str) -> str:
        """
        Generates text content using the configured Gemini model.

        Args:
            prompt: The input prompt to send to the model.

        Returns:
            The generated text as a string.
        """
        try:
            response = self.model.generate_content(prompt)
            # Using .text is a quick way to get the primary text content.
            # For more complex responses, you might inspect other parts of the response object.
            return response.text
        except Exception as e:
            # Basic error handling to ensure the app doesn't crash on an API error.
            print(f"Gemini API Error: {e}")
            return f"Sorry, I couldn't process that request due to an API error."
