import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    def generate_text(self, prompt: str) -> str:
        try:
            return self.model.generate_content(prompt).text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Sorry, I couldn't process that request due to an API error."
