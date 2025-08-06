# ============================================================================
# FILE: src/audio/voice_analysis.py
# Advanced voice pattern analysis for emotion detection
# ============================================================================

import numpy as np
import librosa
import logging
from typing import Dict, List, Tuple, Optional
import tempfile
import os

logger = logging.getLogger(__name__)

class VoicePatternAnalyzer:
    """Extract emotional features from voice audio"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.hop_length = 512
        self.frame_length = 2048
    
    def extract_voice_features(self, audio_file_path: str) -> Dict:
        """Extract comprehensive voice features for emotion analysis"""
        
        try:
            # Load audio file
            audio_data, sr = librosa.load(audio_file_path, sr=self.sample_rate)
            
            if len(audio_data) == 0:
                raise ValueError("Empty audio file")
            
            # Extract features
            features = {
                "pitch_mean": self._extract_pitch_mean(audio_data, sr),
                "pitch_variance": self._extract_pitch_variance(audio_data, sr),
                "energy": self._extract_energy(audio_data),
                "speech_rate": self._estimate_speech_rate(audio_data, sr),
                "avg_pause_duration": self._calculate_pause_duration(audio_data, sr),
                "spectral_centroid": self._extract_spectral_centroid(audio_data, sr),
                "zero_crossing_rate": self._extract_zero_crossing_rate(audio_data),
                "mfcc_features": self._extract_mfcc(audio_data, sr)
            }
            
            logger.info(f"Extracted voice features: {features['pitch_mean']:.1f}Hz pitch, {features['energy']:.2f} energy")
            
            return {
                "success": True,
                "features": features,
                "audio_duration": len(audio_data) / sr
            }
            
        except Exception as e:
            logger.error(f"Voice feature extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "features": self._get_default_features()
            }
    
    def _extract_pitch_mean(self, audio_data: np.ndarray, sr: int) -> float:
        """Extract average pitch (fundamental frequency)"""
        
        try:
            # Use librosa's pitch detection
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr, 
                                                   hop_length=self.hop_length,
                                                   fmin=50, fmax=400)
            
            # Extract fundamental frequency
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:  # Only valid pitches
                    pitch_values.append(pitch)
            
            if pitch_values:
                return float(np.mean(pitch_values))
            else:
                return 150.0  # Default pitch
                
        except Exception as e:
            logger.warning(f"Pitch extraction failed: {e}")
            return 150.0
    
    def _extract_pitch_variance(self, audio_data: np.ndarray, sr: int) -> float:
        """Extract pitch variance (emotional expressiveness)"""
        
        try:
            pitches, magnitudes = librosa.piptrack(y=audio_data, sr=sr,
                                                   hop_length=self.hop_length,
                                                   fmin=50, fmax=400)
            
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 1:
                return float(np.std(pitch_values))
            else:
                return 50.0  # Default variance
                
        except Exception as e:
            logger.warning(f"Pitch variance extraction failed: {e}")
            return 50.0
    
    def _extract_energy(self, audio_data: np.ndarray) -> float:
        """Extract voice energy (loudness/intensity)"""
        
        try:
            # RMS energy
            rms_energy = librosa.feature.rms(y=audio_data, 
                                           frame_length=self.frame_length,
                                           hop_length=self.hop_length)
            
            mean_energy = float(np.mean(rms_energy))
            
            # Normalize to 0-1 range
            normalized_energy = min(mean_energy * 10, 1.0)
            
            return normalized_energy
            
        except Exception as e:
            logger.warning(f"Energy extraction failed: {e}")
            return 0.5
    
    def _estimate_speech_rate(self, audio_data: np.ndarray, sr: int) -> float:
        """Estimate speech rate (words per minute)"""
        
        try:
            # Detect onset frames (approximate syllables/words)
            onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sr,
                                                     hop_length=self.hop_length)
            
            # Calculate duration
            duration_seconds = len(audio_data) / sr
            
            if duration_seconds > 0 and len(onset_frames) > 0:
                # Estimate words per minute
                # Rough approximation: onsets per second * 60 / 2 (assuming 2 onsets per word)
                onsets_per_second = len(onset_frames) / duration_seconds
                estimated_wpm = (onsets_per_second * 60) / 2
                
                # Clamp to reasonable range
                return max(50, min(estimated_wpm, 300))
            else:
                return 150.0  # Default WPM
                
        except Exception as e:
            logger.warning(f"Speech rate estimation failed: {e}")
            return 150.0
    
    def _calculate_pause_duration(self, audio_data: np.ndarray, sr: int) -> float:
        """Calculate average pause duration"""
        
        try:
            # Detect silence using energy threshold
            frame_length = 2048
            hop_length = 512
            
            # Calculate RMS energy per frame
            rms = librosa.feature.rms(y=audio_data, 
                                    frame_length=frame_length,
                                    hop_length=hop_length)[0]
            
            # Threshold for silence (adjust based on overall energy)
            silence_threshold = np.mean(rms) * 0.1
            
            # Find silent frames
            silent_frames = rms < silence_threshold
            
            # Calculate pause durations
            pause_durations = []
            in_pause = False
            pause_start = 0
            
            for i, is_silent in enumerate(silent_frames):
                if is_silent and not in_pause:
                    # Start of pause
                    in_pause = True
                    pause_start = i
                elif not is_silent and in_pause:
                    # End of pause
                    in_pause = False
                    pause_length = (i - pause_start) * hop_length / sr
                    if pause_length > 0.1:  # Only count pauses > 100ms
                        pause_durations.append(pause_length)
            
            if pause_durations:
                return float(np.mean(pause_durations))
            else:
                return 0.5  # Default pause duration
                
        except Exception as e:
            logger.warning(f"Pause duration calculation failed: {e}")
            return 0.5
    
    def _extract_spectral_centroid(self, audio_data: np.ndarray, sr: int) -> float:
        """Extract spectral centroid (brightness of sound)"""
        
        try:
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr,
                                                                  hop_length=self.hop_length)[0]
            return float(np.mean(spectral_centroids))
        except Exception as e:
            logger.warning(f"Spectral centroid extraction failed: {e}")
            return 2000.0
    
    def _extract_zero_crossing_rate(self, audio_data: np.ndarray) -> float:
        """Extract zero crossing rate (measure of noisiness)"""
        
        try:
            zcr = librosa.feature.zero_crossing_rate(audio_data, 
                                                   frame_length=self.frame_length,
                                                   hop_length=self.hop_length)[0]
            return float(np.mean(zcr))
        except Exception as e:
            logger.warning(f"Zero crossing rate extraction failed: {e}")
            return 0.1
    
    def _extract_mfcc(self, audio_data: np.ndarray, sr: int) -> List[float]:
        """Extract MFCC features for voice quality analysis"""
        
        try:
            # Extract 13 MFCC coefficients
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13,
                                       hop_length=self.hop_length)
            
            # Return mean values
            return [float(np.mean(mfcc)) for mfcc in mfccs]
            
        except Exception as e:
            logger.warning(f"MFCC extraction failed: {e}")
            return [0.0] * 13
    
    def _get_default_features(self) -> Dict:
        """Get default voice features when extraction fails"""
        
        return {
            \"pitch_mean\": 150.0,
            \"pitch_variance\": 50.0,
            \"energy\": 0.5,
            \"speech_rate\": 150.0,
            \"avg_pause_duration\": 0.5,
            \"spectral_centroid\": 2000.0,
            \"zero_crossing_rate\": 0.1,
            \"mfcc_features\": [0.0] * 13
        }
    
    def analyze_emotion_from_audio(self, audio_file_path: str) -> Dict:
        \"\"\"Complete pipeline: extract features and analyze emotion\"\"\"
        
        # Extract features
        feature_result = self.extract_voice_features(audio_file_path)
        
        if not feature_result[\"success\"]:
            return {
                \"success\": False,
                \"error\": feature_result.get(\"error\", \"Feature extraction failed\")
            }
        
        features = feature_result[\"features\"]
        
        # Use the emotion analyzer
        from src.core.emotion_analyzer import VoiceEmotionAnalyzer
        
        emotion_analyzer = VoiceEmotionAnalyzer()
        emotion_analysis = emotion_analyzer.analyze_voice_features(features)
        
        return {
            \"success\": True,
            \"emotion_analysis\": {
                \"primary_emotion\": emotion_analysis.primary_emotion.value,
                \"confidence\": emotion_analysis.confidence,
                \"risk_level\": emotion_analysis.risk_level.value,
                \"intensity\": emotion_analysis.intensity,
                \"indicators\": emotion_analysis.emotional_indicators,
                \"suggested_technique\": emotion_analysis.suggested_technique
            },
            \"voice_features\": features,
            \"audio_duration\": feature_result.get(\"audio_duration\", 0)
        }", "oldText": "            # Normalize to 0-1 range"}]