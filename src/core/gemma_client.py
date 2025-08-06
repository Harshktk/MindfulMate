# ============================================================================
# FILE: src/core/gemma_client.py
# Core Gemma 3n integration with your specific model
# ============================================================================

import ollama
import json
import logging
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class GemmaClient:
    """Core Gemma 3n client for MindfulMate"""
    
    def __init__(self, model_name: str = "gemma3n:e4b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.client = ollama.Client(host=host)
        self._verify_connection()
        
        # Response optimization based on use case
        self.response_configs = {
            "quick": {"temperature": 0.5, "max_tokens": 200},
            "therapeutic": {"temperature": 0.7, "max_tokens": 500},
            "crisis": {"temperature": 0.3, "max_tokens": 300},
            "analysis": {"temperature": 0.6, "max_tokens": 400}
        }
    
    def _verify_connection(self):
        """Verify connection to Ollama and model availability"""
        try:
            # Test basic connection first
            models_response = self.client.list()
            logger.info(f"Ollama response type: {type(models_response)}")
            
            # Handle ListResponse object from newer Ollama versions
            available_models = []
            
            if hasattr(models_response, 'models'):
                models = models_response.models
                for model in models:
                    # Extract model name from model object
                    if hasattr(model, 'name'):
                        available_models.append(model.name)
                    elif hasattr(model, 'model'):
                        available_models.append(model.model)
                    elif isinstance(model, dict) and 'name' in model:
                        available_models.append(model['name'])
                    elif isinstance(model, str):
                        available_models.append(model)
            
            logger.info(f"Available models: {available_models}")
            
            # Check if our model is available
            model_found = False
            actual_model_name = None
            
            # Try exact match first
            if self.model_name in available_models:
                actual_model_name = self.model_name
                model_found = True
            else:
                # Try to find any Gemma model
                for model in available_models:
                    if 'gemma' in str(model).lower():
                        actual_model_name = str(model)
                        model_found = True
                        logger.info(f"Using available Gemma model: {actual_model_name} instead of {self.model_name}")
                        self.model_name = actual_model_name  # Update to working model
                        break
            
            if not model_found:
                logger.error(f"No Gemma model found. Available: {available_models}")
                logger.error("Please install a Gemma model: ollama pull gemma:3n")
                raise ValueError(f"No Gemma model available. Available models: {available_models}")
            
            logger.info("[SUCCESS] Connected to {actual_model_name}")
            
            # Test generation with the working model
            test_response = self.client.generate(
                model=actual_model_name,
                prompt="Say 'Ready'",
                options={"temperature": 0.1}
            )
            
            # Handle different response formats
            if isinstance(test_response, dict) and 'response' in test_response:
                logger.info(f"✅ Model test successful: {test_response['response'].strip()}")
            elif hasattr(test_response, 'response'):
                logger.info(f"✅ Model test successful: {test_response.response.strip()}")
            else:
                logger.warning(f"Unexpected response format: {test_response}")
            
        except Exception as e:
            logger.error(f"❌ Gemma connection failed: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            if hasattr(e, 'args'):
                logger.error(f"Exception details: {e.args}")
            raise
    
    async def generate_therapeutic_response(self, user_input: str, 
                                          emotion_context: Dict,
                                          conversation_history: List[Dict] = None) -> Dict:
        """Generate therapeutic response with emotion awareness"""
        
        # Build therapeutic prompt
        prompt = self._build_therapeutic_prompt(user_input, emotion_context, conversation_history)
        
        # Choose appropriate config
        config_type = "crisis" if emotion_context.get("risk_level") == "crisis" else "therapeutic"
        
        try:
            response = await asyncio.to_thread(
                self._generate_with_config,
                prompt, 
                config_type
            )
            
            return self._parse_therapeutic_response(response)
            
        except Exception as e:
            logger.error(f"Therapeutic response generation failed: {e}")
            return self._fallback_therapeutic_response(emotion_context)
    
    async def analyze_emotion_from_text(self, text: str, context: Dict = None) -> Dict:
        """Analyze emotional content using Gemma 3n"""
        
        prompt = f"""
        You are an expert mental health AI analyzing emotional content.
        
        Text to analyze: "{text}"
        
        Context: {json.dumps(context) if context else "None"}
        
        Provide analysis as JSON:
        {{
            "primary_emotion": "anxious|depressed|stressed|angry|happy|calm|confused",
            "confidence": 0.85,
            "intensity": "low|medium|high",
            "risk_level": "low|medium|high|crisis",
            "crisis_indicators": ["list of concerning phrases"],
            "positive_indicators": ["list of positive elements"],
            "emotional_patterns": ["identified patterns"],
            "suggested_approach": "validation|cbt|behavioral_activation|crisis_intervention"
        }}
        
        Focus on:
        1. Accurate emotion identification
        2. Crisis risk assessment (suicidal ideation, self-harm)
        3. Cognitive patterns (catastrophizing, hopelessness)
        4. Therapeutic intervention needs
        """
        
        try:
            response = await asyncio.to_thread(
                self._generate_with_config,
                prompt,
                "analysis"
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Emotion analysis failed: {e}")
            return self._fallback_emotion_analysis()
    
    def _build_therapeutic_prompt(self, user_input: str, emotion_context: Dict, 
                                 conversation_history: List[Dict] = None) -> str:
        """Build context-aware therapeutic prompt"""
        
        # Recent conversation context
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-3:]  # Last 3 exchanges
            history_text = "\n".join([
                f"User: {h.get('user', '')}\nAssistant: {h.get('assistant', '')}"
                for h in recent_history
            ])
        
        # Emotion context
        emotion = emotion_context.get('primary_emotion', 'unknown')
        risk_level = emotion_context.get('risk_level', 'low')
        confidence = emotion_context.get('confidence', 0.0)
        
        prompt = f"""
You are MindfulMate, a compassionate AI mental health companion. The user is experiencing {emotion} and needs practical help.

CURRENT USER INPUT: {user_input}

EMOTIONAL CONTEXT:
- Detected emotion: {emotion} (confidence: {confidence:.2f})
- Risk level: {risk_level}

Provide a helpful response that:
1. Acknowledges their feelings with empathy
2. Offers a specific technique or suggestion to help
3. Asks a follow-up question to continue supporting them

For anxiety/stress: Suggest breathing exercises, grounding techniques, or stress management
For depression: Suggest behavioral activation, gentle activities, or reaching out
For requests for help: Provide specific, actionable techniques

Respond naturally and conversationally, not in JSON format. Focus on being helpful and supportive.
"""
        return prompt
    
    def _generate_with_config(self, prompt: str, config_type: str) -> str:
        """Generate response with specific configuration"""
        config = self.response_configs.get(config_type, self.response_configs["therapeutic"])
        
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options=config  # Remove format="json" as it may cause issues
            )
            
            # Handle different response formats
            if isinstance(response, dict) and 'response' in response:
                return response['response']
            elif hasattr(response, 'response'):
                return response.response
            else:
                logger.error(f"Unexpected response format: {response}")
                return str(response)
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def _parse_therapeutic_response(self, response_text: str) -> Dict:
        """Parse and validate therapeutic response"""
        
        # Since we're now using natural language responses instead of JSON,
        # create a structured response from the natural text
        
        # Clean the response text
        response_text = response_text.strip()
        
        # Determine suggested technique based on response content
        suggested_technique = "validation"
        if "breath" in response_text.lower():
            suggested_technique = "breathing_exercise"
        elif "ground" in response_text.lower() or "5 things" in response_text.lower():
            suggested_technique = "grounding_technique"
        elif "activity" in response_text.lower() or "do something" in response_text.lower():
            suggested_technique = "behavioral_activation"
        elif "crisis" in response_text.lower() or "help" in response_text.lower():
            suggested_technique = "crisis_intervention"
        
        # Check for crisis indicators
        professional_help_needed = any(word in response_text.lower() for word in 
                                     ["crisis", "professional", "therapist", "emergency"])
        
        return {
            "response": response_text,
            "suggested_technique": suggested_technique,
            "follow_up_question": None,  # Already included in response
            "check_in_time": "4hours",
            "professional_help_needed": professional_help_needed,
            "crisis_resources_provided": False
        }
    
    def _fallback_therapeutic_response(self, emotion_context: Dict) -> Dict:
        """Fallback response when generation fails"""
        emotion = emotion_context.get('primary_emotion', 'unknown')
        
        fallback_responses = {
            'anxious': "I can hear that you're feeling anxious. That must be really difficult. Let's try a quick breathing exercise: breathe in for 4 counts, hold for 4, then breathe out for 4. Would you like to try this together?",
            'depressed': "Thank you for sharing with me. It sounds like you're going through a tough time. Sometimes when we're feeling low, small activities can help. Is there one small thing you enjoyed doing before that we could think about?",
            'stressed': "It sounds like you're under a lot of pressure right now. Let's try a grounding technique: can you name 5 things you can see around you right now? This can help bring you back to the present moment.",
            'angry': "I can sense your frustration. Those feelings are valid. When we're angry, it can help to take some deep breaths or do some physical movement. What usually helps you when you're feeling this way?",
            'unknown': "I'm here to listen and support you. It sounds like you're going through something difficult. Can you tell me more about what's bothering you right now? Sometimes talking it through can help."
        }
        
        technique_mapping = {
            'anxious': 'breathing_exercise',
            'depressed': 'behavioral_activation',
            'stressed': 'grounding_technique',
            'angry': 'emotion_regulation',
            'unknown': 'validation'
        }
        
        return {
            "response": fallback_responses.get(emotion, fallback_responses['unknown']),
            "suggested_technique": technique_mapping.get(emotion, 'validation'),
            "follow_up_question": "What would be most helpful for you right now?",
            "check_in_time": "4hours",
            "professional_help_needed": emotion_context.get('risk_level') in ['high', 'crisis'],
            "crisis_resources_provided": False
        }
    
    def _fallback_emotion_analysis(self) -> Dict:
        """Fallback emotion analysis when detection fails"""
        return {
            "primary_emotion": "unknown",
            "confidence": 0.0,
            "intensity": "medium",
            "risk_level": "low",
            "crisis_indicators": [],
            "positive_indicators": [],
            "emotional_patterns": ["analysis_unavailable"],
            "suggested_approach": "validation"
        }
    
    def _get_default_value(self, field: str) -> str:
        """Get default value for missing response fields"""
        defaults = {
            "response": "I'm here to support you. Can you tell me more?",
            "suggested_technique": "validation",
            "follow_up_question": "How are you feeling right now?",
            "check_in_time": "4hours"
        }
        return defaults.get(field, "")