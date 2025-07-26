import google.generativeai as genai
import time

class GeminiClient:
    def __init__(self, api_key: str):
        print("\nInitializing Gemini Client...")
        print(f"API Key (first 4 chars): {api_key[:4]}...")
        
        # Configure the API
        try:
            genai.configure(api_key=api_key)
            print("Successfully configured API key")
        except Exception as e:
            print(f"Error configuring API key: {e}")
            raise Exception(f"Failed to configure API key: {e}")
        
        # First verify we can connect to the API
        try:
            # Explicitly try to list models to verify API connection
            model_list = list(genai.list_models())  # Force evaluation of generator
            print(f"\nSuccessfully connected to API. Found {len(model_list)} models.")
            
            print("\nAvailable models from API:")
            for model in model_list:
                print(f"- {model.name}")
                print(f"  Supported methods: {', '.join(model.supported_generation_methods)}")
            
            # Filter for models that support text generation
            self.models = []
            for model in model_list:
                if "generateContent" in model.supported_generation_methods:
                    self.models.append(model.name)
                    print(f"\nAdding supported model: {model.name}")
            
            if not self.models:
                print("\nNo models with generateContent found, using default model")
                self.models = ["gemini-pro"]
            
            print(f"\nFinal model list: {self.models}")
            
        except Exception as e:
            print(f"\nError accessing API: {str(e)}")
            print("Using default model as fallback")
            self.models = ["gemini-pro"]
            
        self.current_model_index = 0
        self.initialize_model()
        
    def initialize_model(self):
        if not self.models:
            raise Exception("No models configured in the client")
        
        print("\nStarting model initialization...")
        last_error = None
        
        for index, model_name in enumerate(self.models):
            print(f"\nTrying model {index + 1} of {len(self.models)}: {model_name}")
            
            try:
                # Create the model instance
                print(f"Creating instance of {model_name}...")
                self.model = genai.GenerativeModel(model_name)
                
                # Try a simple generation to verify it works
                print("Testing model with simple generation...")
                test_prompt = "Say 'test' in one word."
                generation = self.model.generate_content(test_prompt, safety_settings=[])
                
                # If we get here, the model is working
                print(f"✓ Successfully initialized model: {model_name}")
                print(f"✓ Test generation successful")
                self.current_model_index = index
                return
                
            except Exception as e:
                error_msg = str(e)
                print(f"\nError initializing {model_name}:")
                print(f"- Error type: {type(e).__name__}")
                print(f"- Error message: {error_msg}")
                
                if "401" in error_msg:
                    raise Exception("API key unauthorized. Please check your API key.")
                elif "403" in error_msg:
                    raise Exception("API access forbidden. Please check if the Gemini API is enabled in your Google Cloud project.")
                elif "404" in error_msg:
                    print("Model not found, will try next model if available")
                else:
                    print(f"Unexpected error: {error_msg}")
                
                last_error = e
                continue
                
        # If we get here, all models failed
        error_message = (
            f"Failed to initialize any models. Last error: {last_error}\n"
            "Please ensure:\n"
            "1. Your API key is correct\n"
            "2. The Gemini API is enabled in your Google Cloud project\n"
            "3. Your project has billing enabled\n"
            "4. You have accepted the Terms of Service"
        )
        raise Exception(error_message)
            
    def try_next_model(self):
        """Try to initialize the next available model"""
        next_index = (self.current_model_index + 1) % len(self.models)
        if next_index != self.current_model_index:
            self.current_model_index = next_index
            self.initialize_model()
        
    def generate_text(self, prompt: str, max_retries=3) -> str:
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:  # Rate limit error
                    retry_info = "Please wait a minute and try again. The free tier limit is 50 requests per day."
                    print(f"Rate limit exceeded: {retry_info}")
                    if attempt < max_retries - 1:
                        time.sleep(60)  # Wait 60 seconds before retry
                        continue
                    return f"Sorry, I've hit my rate limit. {retry_info}"
                else:
                    print(f"Gemini API Error: {e}")
                    return "Sorry, I couldn't process that request due to an API error."
        return "Sorry, I couldn't process that request due to an API error."
