import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings={
                    "HARASSMENT": "block_none",
                    "HATE_SPEECH": "block_none",
                    "SEXUALLY_EXPLICIT": "block_none",
                    "DANGEROUS_CONTENT": "block_none"
                }
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Sorry, I couldn't process that request due to an API error."
