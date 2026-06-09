"""
Hugging Face Granite API Client
Handles communication with Hugging Face Inference API and IBM Granite models
"""

import os
from typing import Dict, List, Optional
from huggingface_hub import InferenceClient
from src.utils.config import load_config

class GraniteClient:
    """Client for IBM Granite LLM via Hugging Face Inference API with intelligent fallback"""
    
    def __init__(self):
        """Initialize Granite client with Hugging Face credentials"""
        self.config = load_config()
        self.model_id = self.config.granite_model_id
        self.token = self.config.huggingface_token
        self.demo_mode = False
        self.current_model = None
        self.inference_method = "chat_completion"  # Default to chat_completion
        
        # Validate configuration
        is_valid, error_msg = self.config.validate_huggingface_config()
        
        # Debug logging
        print(f"\n{'='*60}")
        print(f"🔧 Initializing IBM Granite Client via Hugging Face")
        print(f"{'='*60}")
        print(f"   Primary Model: {self.model_id}")
        print(f"   Token Present: {bool(self.token)}")
        if self.token:
            print(f"   Token Prefix: {self.token[:10]}...")
        
        model_info = self.config.get_granite_model_info()
        print(f"   Model Type: {model_info['model_type']}")
        print(f"   Is IBM Granite: {model_info['is_ibm']}")
        
        if not is_valid:
            print(f"\n❌ Configuration Error: {error_msg}")
            print(f"⚠️  Falling back to DEMO MODE - responses will be simulated")
            print(f"{'='*60}\n")
            self.demo_mode = True
            self.client = None
        else:
            try:
                # Initialize Hugging Face InferenceClient
                self.client = InferenceClient(token=self.token)
                print(f"✅ InferenceClient initialized successfully")
                
                # Try to initialize with primary model
                success = self._test_model_connection(self.model_id)
                
                if not success:
                    print(f"\n⚠️  Primary model not available, trying fallback models...")
                    # Try fallback models
                    for fallback_model in self.config.granite_fallback_models:
                        if fallback_model != self.model_id:
                            print(f"   Trying: {fallback_model}")
                            if self._test_model_connection(fallback_model):
                                self.model_id = fallback_model
                                self.current_model = fallback_model
                                print(f"✅ Successfully connected to: {fallback_model}")
                                break
                    else:
                        print(f"\n❌ No Granite models available via Inference API")
                        print(f"⚠️  Falling back to DEMO MODE")
                        self.demo_mode = True
                else:
                    self.current_model = self.model_id
                
                print(f"{'='*60}\n")
                
            except Exception as e:
                print(f"\n❌ Failed to initialize InferenceClient: {str(e)}")
                print(f"⚠️  Falling back to DEMO MODE")
                print(f"{'='*60}\n")
                self.demo_mode = True
                self.client = None
        
        # Default generation parameters optimized for chat models
        self.default_params = {
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.95,
        }
    
    def _test_model_connection(self, model_id: str) -> bool:
        """
        Test if a model is available via Inference API
        Tries chat_completion first, then text_generation as fallback
        
        Args:
            model_id: Model identifier to test
            
        Returns:
            True if model is available, False otherwise
        """
        # Check if client is initialized
        if self.client is None:
            print(f"   ✗ Client not initialized")
            return False
        
        print(f"\n   Testing model: {model_id}")
        
        # STEP 1: Try chat_completion FIRST (preferred for modern models, avoids StopIteration)
        try:
            print(f"   → Attempting chat_completion API...")
            response = self.client.chat_completion(
                messages=[{"role": "user", "content": "Hello"}],
                model=model_id,
                max_tokens=10
            )
            
            # Log response details
            if hasattr(response, '__dict__'):
                print(f"   ✓ Response received: {type(response).__name__}")
                if hasattr(response, 'choices') and response.choices:
                    print(f"   ✓ Choices count: {len(response.choices)}")
                    print(f"   ✓ Response content preview: {response.choices[0].message.content[:50] if response.choices[0].message.content else 'Empty'}")
            
            self.inference_method = "chat_completion"
            print(f"   ✅ SUCCESS: Model supports chat_completion API")
            return True
            
        except Exception as e1:
            # Print FULL exception message (DO NOT TRUNCATE)
            full_error_1 = str(e1)
            print(f"   ✗ chat_completion failed")
            print(f"   ✗ Full exception type: {type(e1).__name__}")
            print(f"   ✗ Full error message: {full_error_1}")
            
            # Log HTTP status code if available
            response = getattr(e1, 'response', None)
            if response is not None:
                status_code = getattr(response, 'status_code', None)
                if status_code is not None:
                    print(f"   ✗ HTTP Status Code: {status_code}")
                response_text = getattr(response, 'text', None)
                if response_text is not None:
                    print(f"   ✗ Response body: {response_text[:200]}")
            
            # Explain exactly why chat_completion failed
            error_lower_1 = full_error_1.lower()
            if "404" in full_error_1 or "not found" in error_lower_1:
                print(f"   ✗ REASON: Model '{model_id}' does not exist on Hugging Face")
            elif "401" in full_error_1 or "unauthorized" in error_lower_1 or "authentication" in error_lower_1:
                print(f"   ✗ REASON: Authentication failed - invalid or missing token")
            elif "403" in full_error_1 or "forbidden" in error_lower_1:
                print(f"   ✗ REASON: Access forbidden - model may be private or gated")
            elif "503" in full_error_1 or "service unavailable" in error_lower_1:
                print(f"   ✗ REASON: Service temporarily unavailable - model may be loading")
            elif "429" in full_error_1 or "rate limit" in error_lower_1:
                print(f"   ✗ REASON: Rate limit exceeded - too many requests")
            elif "not supported" in error_lower_1 or "not available" in error_lower_1:
                print(f"   ✗ REASON: chat_completion API not supported by this model")
            elif "timeout" in error_lower_1:
                print(f"   ✗ REASON: Request timeout - model may be cold starting")
            else:
                print(f"   ✗ REASON: Unknown error - see full error message above")
            
            # STEP 2: Try text_generation as fallback
            print(f"\n   → Attempting text_generation API as fallback...")
            try:
                response = self.client.text_generation(
                    prompt="Hello",
                    model=model_id,
                    max_new_tokens=10
                )
                
                # Log response details
                print(f"   ✓ Response received: {type(response).__name__}")
                if isinstance(response, str):
                    print(f"   ✓ Response preview: {response[:50]}")
                
                self.inference_method = "text_generation"
                print(f"   ✅ SUCCESS: Model supports text_generation API")
                return True
                
            except Exception as e2:
                # Print FULL exception message for text_generation (DO NOT TRUNCATE)
                full_error_2 = str(e2)
                print(f"   ✗ text_generation also failed")
                print(f"   ✗ Full exception type: {type(e2).__name__}")
                print(f"   ✗ Full error message: {full_error_2}")
                
                # Log HTTP status code if available
                response = getattr(e2, 'response', None)
                if response is not None:
                    status_code = getattr(response, 'status_code', None)
                    if status_code is not None:
                        print(f"   ✗ HTTP Status Code: {status_code}")
                    response_text = getattr(response, 'text', None)
                    if response_text is not None:
                        print(f"   ✗ Response body: {response_text[:200]}")
                
                # Explain exactly why text_generation failed
                error_lower_2 = full_error_2.lower()
                if "404" in full_error_2 or "not found" in error_lower_2:
                    print(f"   ✗ REASON: Model '{model_id}' does not exist on Hugging Face")
                elif "401" in full_error_2 or "unauthorized" in error_lower_2 or "authentication" in error_lower_2:
                    print(f"   ✗ REASON: Authentication failed - invalid or missing token")
                elif "403" in full_error_2 or "forbidden" in error_lower_2:
                    print(f"   ✗ REASON: Access forbidden - model may be private or gated")
                elif "503" in full_error_2 or "service unavailable" in error_lower_2:
                    print(f"   ✗ REASON: Service temporarily unavailable - model may be loading")
                elif "429" in full_error_2 or "rate limit" in error_lower_2:
                    print(f"   ✗ REASON: Rate limit exceeded - too many requests")
                elif "not supported" in error_lower_2 or "not available" in error_lower_2:
                    print(f"   ✗ REASON: text_generation API not supported by this model")
                elif "timeout" in error_lower_2:
                    print(f"   ✗ REASON: Request timeout - model may be cold starting")
                elif "stopiteration" in error_lower_2:
                    print(f"   ✗ REASON: StopIteration error - model returned empty response")
                else:
                    print(f"   ✗ REASON: Unknown error - see full error message above")
                
                print(f"\n   ❌ FINAL VERDICT: Model '{model_id}' is NOT available via either API")
                print(f"   ❌ Both chat_completion and text_generation failed")
                return False
    
    def _generate_demo_response(self, prompt: str) -> str:
        """
        Generate a demo response when API is unavailable
        
        Args:
            prompt: Input prompt
            
        Returns:
            Simulated football analysis response
        """
        # Extract context from prompt
        prompt_lower = prompt.lower()
        
        if "var" in prompt_lower or "video assistant referee" in prompt_lower:
            return """This VAR decision was reviewed carefully by the video assistant referee team. 
The officials examined multiple camera angles to ensure accuracy. Based on the available evidence 
and the Laws of the Game, the decision was made to maintain fairness and sporting integrity. 
VAR technology helps referees make more accurate decisions in critical match situations by providing 
additional perspectives that may not be visible to the on-field referee in real-time."""
        
        elif "momentum" in prompt_lower or "shift" in prompt_lower:
            return """The momentum shift in this period was influenced by several key tactical and psychological factors. 
The team's strategic adjustments, including increased pressing intensity and improved ball possession, 
created more attacking opportunities and territorial advantage. This change in momentum often occurs when 
teams make strategic substitutions or adapt their formation to exploit opponent weaknesses. The psychological 
impact of key events, such as goals or near-misses, also plays a crucial role in momentum changes, 
affecting player confidence and decision-making on the pitch."""
        
        elif "story" in prompt_lower or "match" in prompt_lower or "narrative" in prompt_lower:
            return """This was an exciting match that showcased the beautiful game at its finest. 
Both teams displayed tactical discipline and technical skill throughout the contest, creating 
an engaging spectacle for fans. The match featured several key moments that shifted the balance 
of play, with both sides creating scoring opportunities through well-executed attacking moves. 
The final result reflected the competitive nature of the game, with both teams giving their all 
for the full 90 minutes. Individual brilliance combined with team coordination made this a 
memorable encounter that highlighted the strategic depth of modern football."""
        
        elif "player" in prompt_lower or "performance" in prompt_lower:
            return """The player delivered a solid performance, contributing significantly to the team's efforts 
throughout the match. Their positioning, decision-making, and technical execution were key factors 
in the team's tactical approach. They showed good awareness both in attack and defense, making 
important contributions at crucial moments. Their work rate and ability to read the game demonstrated 
the qualities that separate good players from great ones. This type of consistent performance, 
combining technical skill with tactical intelligence, is essential for success at the highest level."""
        
        else:
            return """Based on the match context and tactical analysis, this situation demonstrates 
the complexity and strategic depth of modern football. Multiple factors including team formation, 
player positioning, game state, and tactical adjustments all contribute to the outcome. Understanding 
these elements helps fans appreciate the strategic depth of the sport and the split-second decisions 
made by players and coaches. The interplay between individual skill and team tactics creates the 
dynamic and unpredictable nature that makes football the world's most popular sport."""
    
    def generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate text using chat_completion API (avoids StopIteration errors)
        
        Args:
            prompt: Input prompt for generation
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        # Use demo mode if client is not available
        if self.demo_mode or self.client is None:
            print(f"🎭 Using DEMO MODE for generation")
            return self._generate_demo_response(prompt)
        
        try:
            # Update parameters if provided
            params = self.default_params.copy()
            if max_tokens:
                params["max_tokens"] = max_tokens
            if temperature:
                params["temperature"] = temperature
            
            print(f"🚀 Generating with model: {self.current_model}")
            print(f"   Method: chat_completion (avoids StopIteration)")
            print(f"   Prompt length: {len(prompt)} chars")
            
            # Always use chat_completion to avoid StopIteration errors
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat_completion(
                messages=messages,
                model=self.current_model,
                max_tokens=params.get("max_tokens", 500),
                temperature=params.get("temperature", 0.7),
                top_p=params.get("top_p", 0.95)
            )
            
            # Extract text from chat completion response
            if hasattr(response, 'choices') and len(response.choices) > 0:
                result = response.choices[0].message.content or ""
            else:
                result = str(response)
            
            # Ensure result is a string
            if result is None:
                result = ""
            
            print(f"✅ Generation successful ({len(result)} chars)")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Generation failed with model: {self.current_model}")
            print(f"   Full error: {error_msg}")
            
            # Provide helpful error messages
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                print(f"   ⚠️  Model '{self.current_model}' not found")
                print(f"   💡 The model may have been moved or renamed")
            elif "unauthorized" in error_msg.lower() or "token" in error_msg.lower():
                print(f"   ⚠️  Authentication failed")
                print(f"   💡 Check your HUGGINGFACE_TOKEN in .env")
            elif "rate limit" in error_msg.lower():
                print(f"   ⚠️  Rate limit exceeded")
                print(f"   💡 Please wait before trying again")
            elif "timeout" in error_msg.lower():
                print(f"   ⚠️  Request timeout")
                print(f"   💡 The model may be loading, try again")
            elif "stopiteration" in error_msg.lower():
                print(f"   ⚠️  StopIteration error (should not happen with chat_completion)")
                print(f"   💡 This indicates an API issue")
            
            # Fall back to demo mode for this request
            print(f"   🎭 Using DEMO MODE for this request\n")
            return self._generate_demo_response(prompt)
    
    def generate_with_context(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate response with system prompt and context using chat_completion
        
        Args:
            system_prompt: System instructions
            user_message: User query
            context: Additional context information
            
        Returns:
            Generated response
        """
        # Use demo mode if client is not available
        if self.demo_mode or self.client is None:
            print(f"🎭 Using DEMO MODE for generation with context")
            # Build a simple prompt for demo mode
            prompt = f"{system_prompt}\n\n{context or ''}\n\n{user_message}"
            return self._generate_demo_response(prompt)
        
        try:
            print(f"🚀 Generating with context using model: {self.current_model}")
            
            # Build messages for chat_completion with proper roles
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add context as a user message if provided
            if context:
                messages.append({
                    "role": "user", 
                    "content": f"Context:\n{context}"
                })
            
            # Add the actual user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            response = self.client.chat_completion(
                messages=messages,
                model=self.current_model,
                max_tokens=self.default_params.get("max_tokens", 500),
                temperature=self.default_params.get("temperature", 0.7),
                top_p=self.default_params.get("top_p", 0.95)
            )
            
            # Extract text from chat completion response
            if hasattr(response, 'choices') and len(response.choices) > 0:
                result = response.choices[0].message.content or ""
            else:
                result = str(response)
            
            if result is None:
                result = ""
            
            print(f"✅ Generation with context successful ({len(result)} chars)")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Generation with context failed")
            print(f"   Full error: {error_msg}")
            print(f"   🎭 Using DEMO MODE for this request\n")
            
            # Fallback to demo mode
            prompt = f"{system_prompt}\n\n{context or ''}\n\n{user_message}"
            return self._generate_demo_response(prompt)
    
    def explain_decision(
        self,
        decision_type: str,
        match_context: Dict,
        specific_event: Dict
    ) -> str:
        """
        Generate explanation for a specific match decision
        
        Args:
            decision_type: Type of decision (e.g., "VAR", "Momentum Shift")
            match_context: Overall match context
            specific_event: Specific event details
            
        Returns:
            Detailed explanation
        """
        system_prompt = f"""You are an expert football analyst providing clear, 
detailed explanations of {decision_type} decisions. Use the match context 
and event details to provide an educational explanation that helps fans 
understand the decision."""
        
        context = f"""Match: {match_context.get('teams', 'Unknown')}
Score: {match_context.get('score', 'Unknown')}
Time: {match_context.get('time', 'Unknown')}
Event: {specific_event.get('description', 'Unknown')}"""
        
        user_message = f"Explain this {decision_type} decision in detail."
        
        return self.generate_with_context(system_prompt, user_message, context)
    
    def get_model_info(self) -> Dict:
        """
        Get information about the current model configuration
        
        Returns:
            Dictionary with model information
        """
        return {
            "configured_model": self.model_id,
            "active_model": self.current_model,
            "inference_method": self.inference_method,
            "demo_mode": self.demo_mode,
            "is_granite": "granite" in (self.current_model or "").lower(),
            "provider": "Hugging Face Inference API" if not self.demo_mode else "Demo Mode"
        }

# Made with Bob
