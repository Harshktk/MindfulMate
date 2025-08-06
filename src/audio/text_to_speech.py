# ============================================================================
# FILE: src/audio/text_to_speech.py  
# Text-to-speech conversion for voice output
# ============================================================================

import pyttsx3
import logging
from typing import Dict, Optional
import tempfile
import os

logger = logging.getLogger(__name__)

class TextToSpeechProcessor:
    """Convert text to speech for AI responses"""
    
    def __init__(self, voice_rate: int = 200, voice_volume: float = 0.8):
        try:
            self.engine = pyttsx3.init()
            self.voice_rate = voice_rate
            self.voice_volume = voice_volume
            
            # Configure voice properties
            self._configure_voice()
            
            logger.info("✅ Text-to-speech initialized")
            
        except Exception as e:
            logger.error(f"TTS initialization failed: {e}")
            self.engine = None
    
    def _configure_voice(self):
        """Configure voice properties for therapeutic tone"""
        
        if not self.engine:
            return
        
        try:
            # Set speech rate (slower for calm, therapeutic tone)
            self.engine.setProperty('rate', self.voice_rate)
            
            # Set volume
            self.engine.setProperty('volume', self.voice_volume)
            
            # Choose voice (prefer female voice for mental health context)
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find a female voice
                female_voice = None
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        female_voice = voice
                        break
                
                if female_voice:
                    self.engine.setProperty('voice', female_voice.id)
                    logger.info(f"Using voice: {female_voice.name}")
                else:
                    # Use first available voice
                    self.engine.setProperty('voice', voices[0].id)
                    logger.info(f"Using voice: {voices[0].name}")
            
        except Exception as e:
            logger.warning(f"Voice configuration warning: {e}")
    
    def speak_text(self, text: str, emotional_context: Dict = None) -> Dict:
        """Convert text to speech with emotional context"""
        
        if not self.engine:
            return {"success": False, "error": "TTS engine not available"}
        
        try:
            # Adjust speech properties based on emotional context
            if emotional_context:
                self._adjust_for_emotion(emotional_context)
            
            # Clean text for speech
            speech_text = self._prepare_text_for_speech(text)
            
            # Speak the text
            self.engine.say(speech_text)
            self.engine.runAndWait()
            
            return {
                "success": True,
                "text_spoken": speech_text,
                "emotional_adjustment": emotional_context is not None
            }
            
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_speech_to_file(self, text: str, output_path: str, 
                           emotional_context: Dict = None) -> Dict:
        """Save speech as audio file"""
        
        if not self.engine:
            return {"success": False, "error": "TTS engine not available"}
        
        try:
            # Adjust for emotion
            if emotional_context:
                self._adjust_for_emotion(emotional_context)
            
            # Prepare text
            speech_text = self._prepare_text_for_speech(text)
            
            # Save to file
            self.engine.save_to_file(speech_text, output_path)
            self.engine.runAndWait()
            
            return {
                "success": True,
                "output_file": output_path,
                "text_spoken": speech_text
            }
            
        except Exception as e:
            logger.error(f"Save speech to file failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _adjust_for_emotion(self, emotional_context: Dict):
        """Adjust speech properties based on detected emotion"""
        
        if not self.engine:
            return
        
        emotion = emotional_context.get('primary_emotion', 'calm')
        risk_level = emotional_context.get('risk_level', 'low')
        
        try:
            # Adjust rate based on emotion
            if emotion == 'anxious':
                # Slower, calmer speech for anxious users
                self.engine.setProperty('rate', max(self.voice_rate - 30, 150))
            elif emotion == 'depressed':
                # Slightly more energetic speech for depressed users
                self.engine.setProperty('rate', min(self.voice_rate + 20, 220))
            elif risk_level == 'crisis':
                # Very calm, steady speech for crisis
                self.engine.setProperty('rate', max(self.voice_rate - 50, 140))
            else:
                # Normal rate
                self.engine.setProperty('rate', self.voice_rate)
            
        except Exception as e:
            logger.warning(f"Could not adjust speech for emotion: {e}")
    
    def _prepare_text_for_speech(self, text: str) -> str:
        """Prepare text for natural speech synthesis"""
        
        # Remove or replace problematic characters
        speech_text = text.replace('"', '')
        speech_text = speech_text.replace('*', '')
        speech_text = speech_text.replace('_', '')
        
        # Add pauses for better flow
        speech_text = speech_text.replace('.', '. ')
        speech_text = speech_text.replace(',', ', ')
        speech_text = speech_text.replace('?', '? ')
        speech_text = speech_text.replace('!', '! ')
        
        # Clean up multiple spaces
        speech_text = ' '.join(speech_text.split())
        
        return speech_text
