# ============================================================================
# FILE: src/audio/speech_to_text.py
# Speech-to-text conversion for voice input
# ============================================================================

import speech_recognition as sr
import logging
from typing import Dict, Optional
import tempfile
import os

logger = logging.getLogger(__name__)

class SpeechToTextProcessor:
    """Convert speech to text using various engines"""
    
    def __init__(self, language: str = "en-US"):
        self.recognizer = sr.Recognizer()
        self.language = language
        
        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("✅ Speech recognition initialized with microphone")
        except Exception as e:
            logger.warning(f"Microphone initialization failed: {e}")
            self.microphone = None
    
    def transcribe_audio_file(self, audio_file_path: str) -> Dict:
        """Transcribe audio file to text"""
        
        try:
            # Load audio file
            with sr.AudioFile(audio_file_path) as source:
                audio_data = self.recognizer.record(source)
            
            # Transcribe using multiple engines for reliability
            results = {}
            
            # Try Google Speech Recognition (free tier)
            try:
                text = self.recognizer.recognize_google(audio_data, language=self.language)
                results["google"] = {
                    "text": text,
                    "confidence": 0.8,  # Google doesn't provide confidence
                    "engine": "google"
                }
            except sr.UnknownValueError:
                results["google"] = {"error": "Could not understand audio"}
            except sr.RequestError as e:
                results["google"] = {"error": f"Google API error: {e}"}
            
            # Try offline Sphinx as fallback
            try:
                text = self.recognizer.recognize_sphinx(audio_data)
                results["sphinx"] = {
                    "text": text,
                    "confidence": 0.6,  # Lower confidence for offline
                    "engine": "sphinx"
                }
            except sr.UnknownValueError:
                results["sphinx"] = {"error": "Could not understand audio"}
            except sr.RequestError as e:
                results["sphinx"] = {"error": f"Sphinx error: {e}"}
            
            # Return best result
            best_result = self._select_best_transcription(results)
            
            return {
                "success": best_result is not None,
                "text": best_result["text"] if best_result else "",
                "confidence": best_result["confidence"] if best_result else 0.0,
                "engine_used": best_result["engine"] if best_result else "none",
                "all_results": results
            }
            
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return {
                "success": False,
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def transcribe_live_audio(self, duration: float = 5.0) -> Dict:
        """Transcribe live audio from microphone"""
        
        if not self.microphone:
            return {
                "success": False,
                "error": "Microphone not available"
            }
        
        try:
            with self.microphone as source:
                logger.info(f"🎤 Listening for {duration} seconds...")
                audio_data = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            # Transcribe
            try:
                text = self.recognizer.recognize_google(audio_data, language=self.language)
                return {
                    "success": True,
                    "text": text,
                    "confidence": 0.8,
                    "engine_used": "google"
                }
            except sr.UnknownValueError:
                return {
                    "success": False,
                    "text": "",
                    "error": "Could not understand audio"
                }
            except sr.RequestError as e:
                # Fallback to offline
                try:
                    text = self.recognizer.recognize_sphinx(audio_data)
                    return {
                        "success": True,
                        "text": text,
                        "confidence": 0.6,
                        "engine_used": "sphinx"
                    }
                except:
                    return {
                        "success": False,
                        "text": "",
                        "error": f"All recognition engines failed: {e}"
                    }
                    
        except Exception as e:
            logger.error(f"Live audio transcription failed: {e}")
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }
    
    def _select_best_transcription(self, results: Dict) -> Optional[Dict]:
        """Select the best transcription from multiple engines"""
        
        # Priority order: Google > Sphinx
        engines = ["google", "sphinx"]
        
        for engine in engines:
            if engine in results and "text" in results[engine]:
                result = results[engine]
                # Only return if we have actual text
                if result["text"].strip():
                    return result
        
        return None
