import google.generativeai as genai
import time

class GeminiClient:
    def __init__(self, api_key: str):
        print("\nInitializing Gemini Client...")
        print(f"API Key (first 4 chars): {api_key[:4]}...")
        
        # Track API usage for free tier
        self.daily_requests = 0
        self.last_request_time = 0
        self.free_tier_limit = 50  # Free tier daily limit
        self.request_cooldown = 1.2  # Cooldown to respect 1 req/sec limit (60 req/min)
        
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
        # Enforce a cooldown to respect rate limits (e.g., 60 requests/minute)
        time_since_last_request = time.time() - self.last_request_time
        if time_since_last_request < self.request_cooldown:
            wait_time = self.request_cooldown - time_since_last_request
            print(f"Cooldown active. Waiting for {wait_time:.2f} seconds...")
            time.sleep(wait_time)

        # Check daily limit before proceeding
        if self.daily_requests >= self.free_tier_limit:
            return (
                "⚠️ Daily free tier limit reached (50 requests/day). "
                "Please wait for the quota to reset or upgrade to a paid tier."
            )

        for attempt in range(max_retries):
            try:
                # Minimal delay between retries
                if attempt > 0:
                    time.sleep(0.1)
                
                current_time = time.time()
                
                # Configure model for longer output
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 2048,
                    },
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    ]
                )
                
                # Update tracking on successful request
                self.last_request_time = current_time
                self.daily_requests += 1
                
                # Log usage info to console for debugging, but don't return it to the agent
                remaining = self.free_tier_limit - self.daily_requests
                print(f"📊 Free tier usage: {self.daily_requests}/{self.free_tier_limit} requests today. {remaining} requests remaining.")
                
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg:  # Rate limit error
                    retry_info = (
                        "Rate limit reached. The free tier has the following limits:\n"
                        "- 50 requests per day\n"
                        "- 1 request per second\n"
                        f"Current usage: {self.daily_requests}/{self.free_tier_limit} requests today."
                    )
                    print(f"Rate limit exceeded: {retry_info}")
                    if attempt < max_retries - 1:
                        # Wait longer on rate limit error before retrying
                        wait_on_error = (attempt + 1) * 2
                        print(f"Waiting for {wait_on_error} seconds before retrying...")
                        time.sleep(wait_on_error)
                        continue
                    return f"⚠️ {retry_info}"
                else:
                    print(f"Gemini API Error: {e}")
                    return "Sorry, I couldn't process that request due to an API error."
                    
        return "Sorry, I couldn't process that request. Please try again in a few minutes."
