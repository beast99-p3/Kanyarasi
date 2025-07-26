import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Use the recommended gemini-1.5-flash model
        model_name = "models/gemini-1.5-flash"
        print(f"Using model: {model_name}")
        self.model = genai.GenerativeModel(model_name)
        
    def generate_text(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Sorry, I couldn't process that request due to an API error."
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "Sorry, I couldn't process that request due to an API error."
