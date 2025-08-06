# ============================================================================
# FILE: src/core/emotion_analyzer.py  
# Comprehensive emotion detection system
# ============================================================================

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EmotionState(Enum):
    """Supported emotional states"""
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    STRESSED = "stressed"
    ANGRY = "angry"
    HAPPY = "happy"
    CALM = "calm"
    CONFUSED = "confused"
    EXCITED = "excited"

class RiskLevel(Enum):
    """Mental health risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRISIS = "crisis"

@dataclass
class EmotionAnalysis:
    """Comprehensive emotion analysis result"""
    primary_emotion: EmotionState
    confidence: float
    risk_level: RiskLevel
    emotional_indicators: List[str]
    suggested_technique: str
    intensity: str
    patterns: List[str]

class VoiceEmotionAnalyzer:
    """Analyze emotions from voice characteristics"""
    
    def __init__(self):
        self.crisis_voice_patterns = {
            'very_low_energy': 0.2,
            'monotone_speech': 25,  # Low pitch variance
            'slow_speech': 100,     # Very slow WPM
            'long_pauses': 2.0      # Seconds
        }
    
    def analyze_voice_features(self, voice_features: Dict) -> EmotionAnalysis:
        """Analyze emotion from voice characteristics"""
        
        # Extract features with defaults
        pitch_mean = voice_features.get('pitch_mean', 150)
        pitch_variance = voice_features.get('pitch_variance', 50)
        speech_rate = voice_features.get('speech_rate', 150)  # WPM
        energy = voice_features.get('energy', 0.5)
        pause_duration = voice_features.get('avg_pause_duration', 0.5)
        
        # Calculate emotion scores
        emotion_scores = self._calculate_emotion_scores(
            pitch_mean, pitch_variance, speech_rate, energy, pause_duration
        )
        
        # Determine primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[primary_emotion]
        
        # Assess risk level
        risk_level = self._assess_voice_risk(emotion_scores, voice_features)
        
        # Generate indicators and suggestions
        indicators = self._generate_voice_indicators(voice_features)
        intensity = self._calculate_intensity(emotion_scores[primary_emotion])
        technique = self._suggest_voice_technique(primary_emotion, risk_level)
        patterns = self._identify_voice_patterns(voice_features)
        
        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            confidence=confidence,
            risk_level=risk_level,
            emotional_indicators=indicators,
            suggested_technique=technique,
            intensity=intensity,
            patterns=patterns
        )
    
    def _calculate_emotion_scores(self, pitch_mean: float, pitch_variance: float,
                                 speech_rate: float, energy: float, 
                                 pause_duration: float) -> Dict[EmotionState, float]:
        """Calculate scores for each emotion based on voice features"""
        
        scores = {}
        
        # Anxiety indicators
        scores[EmotionState.ANXIOUS] = self._calculate_anxiety_score(
            pitch_mean, pitch_variance, speech_rate, energy
        )
        
        # Depression indicators  
        scores[EmotionState.DEPRESSED] = self._calculate_depression_score(
            pitch_mean, energy, pause_duration, speech_rate
        )
        
        # Stress indicators
        scores[EmotionState.STRESSED] = self._calculate_stress_score(
            speech_rate, pitch_variance, energy
        )
        
        # Anger indicators
        scores[EmotionState.ANGRY] = self._calculate_anger_score(
            pitch_mean, energy, speech_rate
        )
        
        # Happiness indicators
        scores[EmotionState.HAPPY] = self._calculate_happiness_score(
            pitch_mean, energy, speech_rate, pitch_variance
        )
        
        # Calm indicators
        scores[EmotionState.CALM] = self._calculate_calm_score(
            pitch_variance, speech_rate, energy, pause_duration
        )
        
        return scores
    
    def _calculate_anxiety_score(self, pitch_mean: float, pitch_variance: float,
                               speech_rate: float, energy: float) -> float:
        """Calculate anxiety score from voice patterns"""
        score = 0.0
        
        # High pitch variance (nervous speech)
        if pitch_variance > 75:
            score += 0.3
        
        # Fast, rushed speech
        if speech_rate > 180:
            score += 0.3
        
        # Higher pitch when anxious
        if pitch_mean > 200:
            score += 0.2
        
        # Moderate to high energy with other indicators
        if energy > 0.6 and (pitch_variance > 60 or speech_rate > 170):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_depression_score(self, pitch_mean: float, energy: float,
                                  pause_duration: float, speech_rate: float) -> float:
        """Calculate depression score from voice patterns"""
        score = 0.0
        
        # Very low energy is a strong indicator
        if energy < 0.3:
            score += 0.4
        
        # Low pitch (monotone, flat affect)
        if pitch_mean < 120:
            score += 0.3
        
        # Long pauses (processing delays, fatigue)
        if pause_duration > 1.5:
            score += 0.3
        
        # Very slow speech
        if speech_rate < 120:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_stress_score(self, speech_rate: float, pitch_variance: float,
                              energy: float) -> float:
        """Calculate stress score from voice patterns"""
        score = 0.0
        
        # Extreme speech rates (too fast or too slow under stress)
        if speech_rate > 200 or speech_rate < 100:
            score += 0.3
        
        # High pitch variance (unstable under stress)
        if pitch_variance > 80:
            score += 0.3
        
        # High energy with other stress indicators
        if energy > 0.7 and pitch_variance > 60:
            score += 0.2
        
        # Moderate energy with extreme speech rate
        if 0.4 < energy < 0.7 and (speech_rate > 190 or speech_rate < 110):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_anger_score(self, pitch_mean: float, energy: float,
                             speech_rate: float) -> float:
        """Calculate anger score from voice patterns"""
        score = 0.0
        
        # High energy (raised voice)
        if energy > 0.8:
            score += 0.4
        
        # Higher pitch when angry
        if pitch_mean > 180:
            score += 0.3
        
        # Fast, clipped speech
        if speech_rate > 190:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_happiness_score(self, pitch_mean: float, energy: float,
                                 speech_rate: float, pitch_variance: float) -> float:
        """Calculate happiness score from voice patterns"""
        score = 0.0
        
        # Moderate to high energy
        if 0.6 < energy < 0.9:
            score += 0.3
        
        # Slightly elevated pitch
        if 160 < pitch_mean < 200:
            score += 0.2
        
        # Normal to slightly fast speech
        if 150 < speech_rate < 180:
            score += 0.2
        
        # Moderate pitch variance (expressive)
        if 40 < pitch_variance < 70:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_calm_score(self, pitch_variance: float, speech_rate: float,
                            energy: float, pause_duration: float) -> float:
        """Calculate calmness score from voice patterns"""
        score = 0.0
        
        # Steady pitch (controlled)
        if 25 < pitch_variance < 55:
            score += 0.3
        
        # Normal speech rate
        if 140 < speech_rate < 170:
            score += 0.3
        
        # Moderate energy
        if 0.4 < energy < 0.7:
            score += 0.2
        
        # Appropriate pause duration
        if 0.3 < pause_duration < 0.8:
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_voice_risk(self, emotion_scores: Dict, voice_features: Dict) -> RiskLevel:
        """Assess mental health risk from voice patterns"""
        
        # Crisis indicators in voice
        energy = voice_features.get('energy', 0.5)
        speech_rate = voice_features.get('speech_rate', 150)
        pause_duration = voice_features.get('avg_pause_duration', 0.5)
        
        # Severe depression indicators
        if (emotion_scores[EmotionState.DEPRESSED] > 0.8 and 
            energy < 0.2 and speech_rate < 100):
            return RiskLevel.CRISIS
        
        # High anxiety with other concerning factors
        if (emotion_scores[EmotionState.ANXIOUS] > 0.8 and
            pause_duration > 2.0):  # Long pauses could indicate overwhelm
            return RiskLevel.HIGH
        
        # Multiple concerning indicators
        concerning_emotions = sum(1 for score in emotion_scores.values() if score > 0.7)
        if concerning_emotions >= 2:
            return RiskLevel.HIGH
        
        # Single strong negative emotion
        if max(emotion_scores[EmotionState.DEPRESSED], 
               emotion_scores[EmotionState.ANXIOUS],
               emotion_scores[EmotionState.STRESSED]) > 0.6:
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _generate_voice_indicators(self, voice_features: Dict) -> List[str]:
        """Generate human-readable voice indicators"""
        indicators = []
        
        speech_rate = voice_features.get('speech_rate', 150)
        energy = voice_features.get('energy', 0.5)
        pitch_variance = voice_features.get('pitch_variance', 50)
        pause_duration = voice_features.get('avg_pause_duration', 0.5)
        
        # Speech rate indicators
        if speech_rate > 190:
            indicators.append("Rapid speech pattern")
        elif speech_rate < 120:
            indicators.append("Slow speech pattern")
        
        # Energy indicators
        if energy < 0.3:
            indicators.append("Low vocal energy")
        elif energy > 0.8:
            indicators.append("High vocal energy")
        
        # Pitch indicators
        if pitch_variance > 75:
            indicators.append("Variable pitch patterns")
        elif pitch_variance < 25:
            indicators.append("Monotone speech")
        
        # Pause indicators
        if pause_duration > 1.5:
            indicators.append("Extended pauses")
        elif pause_duration < 0.2:
            indicators.append("Minimal pauses")
        
        return indicators
    
    def _calculate_intensity(self, confidence: float) -> str:
        """Calculate emotional intensity from confidence score"""
        if confidence > 0.7:
            return "high"
        elif confidence > 0.4:
            return "medium"
        else:
            return "low"
    
    def _suggest_voice_technique(self, emotion: EmotionState, risk: RiskLevel) -> str:
        """Suggest therapeutic technique based on voice analysis"""
        
        if risk == RiskLevel.CRISIS:
            return "crisis_intervention"
        elif risk == RiskLevel.HIGH:
            return "safety_planning"
        
        techniques = {
            EmotionState.ANXIOUS: "breathing_exercise",
            EmotionState.DEPRESSED: "behavioral_activation",
            EmotionState.STRESSED: "grounding_technique",
            EmotionState.ANGRY: "emotion_regulation",
            EmotionState.HAPPY: "positive_reinforcement",
            EmotionState.CALM: "maintenance_check"
        }
        
        return techniques.get(emotion, "general_support")
    
    def _identify_voice_patterns(self, voice_features: Dict) -> List[str]:
        """Identify concerning voice patterns"""
        patterns = []
        
        energy = voice_features.get('energy', 0.5)
        speech_rate = voice_features.get('speech_rate', 150)
        pitch_variance = voice_features.get('pitch_variance', 50)
        
        # Depression patterns
        if energy < 0.3 and speech_rate < 120:
            patterns.append("potential_depression_indicators")
        
        # Anxiety patterns
        if speech_rate > 180 and pitch_variance > 70:
            patterns.append("potential_anxiety_indicators")
        
        # Stress patterns
        if (speech_rate > 200 or speech_rate < 100) and energy > 0.6:
            patterns.append("potential_stress_indicators")
        
        return patterns

class TextEmotionAnalyzer:
    """Analyze emotions from text using Gemma 3n and rule-based methods"""
    
    def __init__(self, gemma_client):
        self.gemma_client = gemma_client
        
        # Crisis keywords for immediate detection
        self.crisis_keywords = [
            "suicide", "kill myself", "end it all", "better off dead",
            "self harm", "hurt myself", "cutting", "overdose",
            "hopeless", "worthless", "no point", "can't go on",
            "want to die", "end my life", "not worth living"
        ]
        
        # Emotional keywords for backup analysis
        self.emotion_keywords = {
            EmotionState.ANXIOUS: ["worried", "nervous", "scared", "panic", "anxious", "afraid"],
            EmotionState.DEPRESSED: ["sad", "empty", "hopeless", "worthless", "depressed", "down"],
            EmotionState.STRESSED: ["overwhelmed", "pressure", "stressed", "burden", "exhausted"],
            EmotionState.ANGRY: ["angry", "furious", "mad", "frustrated", "rage", "irritated"],
            EmotionState.HAPPY: ["happy", "joy", "excited", "good", "great", "wonderful"]
        }
    
    async def analyze_text_emotion(self, text: str, context: Dict = None) -> EmotionAnalysis:
        """Comprehensive text emotion analysis"""
        
        # Quick crisis detection
        crisis_detected = self._detect_crisis_keywords(text.lower())
        
        try:
            # Use Gemma 3n for detailed analysis
            gemma_analysis = await self.gemma_client.analyze_emotion_from_text(text, context)
            
            # Parse results
            emotion_str = gemma_analysis.get('primary_emotion', 'calm')
            primary_emotion = self._string_to_emotion(emotion_str)
            confidence = gemma_analysis.get('confidence', 0.5)
            
            # Override risk if crisis keywords detected
            risk_level = RiskLevel.CRISIS if crisis_detected else self._string_to_risk(
                gemma_analysis.get('risk_level', 'low')
            )
            
            # Extract indicators
            crisis_indicators = gemma_analysis.get('crisis_indicators', [])
            positive_indicators = gemma_analysis.get('positive_indicators', [])
            patterns = gemma_analysis.get('emotional_patterns', [])
            
            indicators = crisis_indicators + positive_indicators
            if crisis_detected and not crisis_indicators:
                indicators.append("Crisis keywords detected")
            
            # Suggest technique
            technique = self._suggest_text_technique(primary_emotion, risk_level, gemma_analysis)
            
            return EmotionAnalysis(
                primary_emotion=primary_emotion,
                confidence=confidence,
                risk_level=risk_level,
                emotional_indicators=indicators,
                suggested_technique=technique,
                intensity=gemma_analysis.get('intensity', 'medium'),
                patterns=patterns
            )
            
        except Exception as e:
            logger.error(f"Gemma text analysis failed: {e}")
            return self._fallback_text_analysis(text, crisis_detected)
    
    def _detect_crisis_keywords(self, text: str) -> bool:
        """Quick detection of crisis-related language"""
        return any(keyword in text for keyword in self.crisis_keywords)
    
    def _string_to_emotion(self, emotion_str: str) -> EmotionState:
        """Convert string to EmotionState enum"""
        mapping = {
            'anxious': EmotionState.ANXIOUS,
            'depressed': EmotionState.DEPRESSED,
            'stressed': EmotionState.STRESSED,
            'angry': EmotionState.ANGRY,
            'happy': EmotionState.HAPPY,
            'calm': EmotionState.CALM,
            'confused': EmotionState.CONFUSED,
            'excited': EmotionState.EXCITED
        }
        return mapping.get(emotion_str.lower(), EmotionState.CALM)
    
    def _string_to_risk(self, risk_str: str) -> RiskLevel:
        """Convert string to RiskLevel enum"""
        mapping = {
            'low': RiskLevel.LOW,
            'medium': RiskLevel.MEDIUM,
            'high': RiskLevel.HIGH,
            'crisis': RiskLevel.CRISIS
        }
        return mapping.get(risk_str.lower(), RiskLevel.LOW)
    
    def _suggest_text_technique(self, emotion: EmotionState, risk: RiskLevel, 
                               analysis: Dict) -> str:
        """Suggest technique based on text analysis"""
        
        if risk == RiskLevel.CRISIS:
            return "crisis_intervention"
        elif risk == RiskLevel.HIGH:
            return "safety_planning"
        
        # Use Gemma's suggestion if available
        suggested_approach = analysis.get('suggested_approach', '')
        if suggested_approach in ['cbt', 'behavioral_activation', 'validation', 'crisis_intervention']:
            return suggested_approach
        
        # Default mappings
        return {
            EmotionState.ANXIOUS: "breathing_exercise",
            EmotionState.DEPRESSED: "behavioral_activation",
            EmotionState.STRESSED: "grounding_technique",
            EmotionState.ANGRY: "emotion_regulation",
            EmotionState.CONFUSED: "clarification_questions"
        }.get(emotion, "validation")
    
    def _fallback_text_analysis(self, text: str, crisis_detected: bool) -> EmotionAnalysis:
        """Fallback analysis using keyword matching"""
        
        # Simple keyword-based emotion detection
        emotion_scores = {}
        text_lower = text.lower()
        
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_scores[emotion] = score / len(keywords)
        
        # Determine primary emotion
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[primary_emotion]
        else:
            primary_emotion = EmotionState.CALM
            confidence = 0.3
        
        # Risk assessment
        risk_level = RiskLevel.CRISIS if crisis_detected else RiskLevel.LOW
        
        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            confidence=confidence,
            risk_level=risk_level,
            emotional_indicators=["Keyword-based analysis"],
            suggested_technique="validation",
            intensity="medium",
            patterns=["fallback_analysis"]
        )

class MultimodalEmotionFusion:
    """Combine voice and text analysis for comprehensive emotion detection"""
    
    def __init__(self):
        # Weights for different modalities
        self.voice_weight = 0.4
        self.text_weight = 0.6
        
        # Minimum confidence thresholds
        self.min_confidence = 0.3
        self.agreement_bonus = 0.2
    
    def fuse_emotions(self, voice_analysis: Optional[EmotionAnalysis], 
                     text_analysis: EmotionAnalysis) -> EmotionAnalysis:
        """Combine voice and text analysis for final emotion assessment"""
        
        # If no voice analysis, return text analysis
        if not voice_analysis:
            return text_analysis
        
        # Calculate weighted confidence
        combined_confidence = (
            voice_analysis.confidence * self.voice_weight +
            text_analysis.confidence * self.text_weight
        )
        
        # Check for agreement between modalities
        emotions_agree = voice_analysis.primary_emotion == text_analysis.primary_emotion
        
        if emotions_agree:
            # High confidence when modalities agree
            primary_emotion = voice_analysis.primary_emotion
            combined_confidence = min(combined_confidence + self.agreement_bonus, 1.0)
        else:
            # Prioritize text for semantic content, but consider voice for emotional tone
            primary_emotion = text_analysis.primary_emotion
            combined_confidence *= 0.8  # Reduce confidence for disagreement
        
        # Risk assessment - take the highest risk level
        risk_levels = [voice_analysis.risk_level, text_analysis.risk_level]
        risk_priorities = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, 
                          RiskLevel.HIGH: 2, RiskLevel.CRISIS: 3}
        
        risk_level = max(risk_levels, key=lambda x: risk_priorities[x])
        
        # Combine indicators and patterns
        combined_indicators = (
            voice_analysis.emotional_indicators + 
            text_analysis.emotional_indicators
        )
        
        combined_patterns = list(set(
            voice_analysis.patterns + text_analysis.patterns
        ))
        
        # Choose therapeutic technique
        technique = self._choose_combined_technique(
            primary_emotion, risk_level, voice_analysis, text_analysis
        )
        
        # Determine intensity
        intensity = self._determine_combined_intensity(
            voice_analysis.intensity, text_analysis.intensity, combined_confidence
        )
        
        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            confidence=max(combined_confidence, self.min_confidence),
            risk_level=risk_level,
            emotional_indicators=combined_indicators,
            suggested_technique=technique,
            intensity=intensity,
            patterns=combined_patterns
        )
    
    def _choose_combined_technique(self, emotion: EmotionState, risk: RiskLevel,
                                  voice_analysis: EmotionAnalysis, 
                                  text_analysis: EmotionAnalysis) -> str:
        """Choose therapeutic technique based on combined analysis"""
        
        # Crisis always takes priority
        if risk == RiskLevel.CRISIS:
            return "crisis_intervention"
        elif risk == RiskLevel.HIGH:
            return "safety_planning"
        
        # If both analyses suggest the same technique, use it
        if voice_analysis.suggested_technique == text_analysis.suggested_technique:
            return voice_analysis.suggested_technique
        
        # Prioritize text-based technique for semantic understanding
        return text_analysis.suggested_technique
    
    def _determine_combined_intensity(self, voice_intensity: str, 
                                    text_intensity: str, confidence: float) -> str:
        """Determine combined emotional intensity"""
        
        intensity_values = {'low': 1, 'medium': 2, 'high': 3}
        
        voice_val = intensity_values.get(voice_intensity, 2)
        text_val = intensity_values.get(text_intensity, 2)
        
        # Weighted average
        combined_val = (voice_val * self.voice_weight + text_val * self.text_weight)
        
        # Adjust based on confidence
        if confidence > 0.8:
            combined_val *= 1.1  # Boost intensity for high confidence
        elif confidence < 0.4:
            combined_val *= 0.9  # Reduce intensity for low confidence
        
        # Convert back to string
        if combined_val > 2.5:
            return "high"
        elif combined_val > 1.5:
            return "medium"
        else:
            return "low"
