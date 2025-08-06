from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import logging
import asyncio

from ..audio.enhanced_voice_processor import EnhancedVoiceProcessor
from ..core.emotion_analyzer import VoiceEmotionAnalyzer
from ..utils.helpers import validate_voice_features

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Initialize processors
voice_processor = EnhancedVoiceProcessor()
voice_analyzer = VoiceEmotionAnalyzer()

@router.post("/analyze")
async def analyze_voice_upload(
    audio_file: UploadFile = File(...),
    user_id: str = "anonymous",
    session_id: Optional[str] = None
):
    """Analyze uploaded audio file for emotional content"""
    
    if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be audio format")
    
    if audio_file.size and audio_file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Audio file too large (max 10MB)")
    
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Process audio to extract features
        logger.info(f"Processing audio file: {audio_file.filename}")
        voice_features = await voice_processor.process_audio_blob(audio_data)
        
        # Analyze emotions from voice features
        emotion_analysis = voice_analyzer.analyze_voice_features(voice_features)
        
        return {
            "voice_features": voice_features,
            "emotion_analysis": {
                "primary_emotion": emotion_analysis.primary_emotion.value,
                "confidence": emotion_analysis.confidence,
                "risk_level": emotion_analysis.risk_level.value,
                "intensity": emotion_analysis.intensity,
                "indicators": emotion_analysis.emotional_indicators,
                "suggested_technique": emotion_analysis.suggested_technique,
                "patterns": emotion_analysis.patterns
            },
            "processing_info": {
                "file_name": audio_file.filename,
                "file_size": len(audio_data),
                "content_type": audio_file.content_type
            }
        }
        
    except Exception as e:
        logger.error(f"Voice analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice analysis failed: {str(e)}")

@router.post("/features")
async def analyze_voice_features(request: dict):
    """Analyze emotion from pre-extracted voice features"""
    
    voice_features = request.get("voice_features", {})
    
    if not validate_voice_features(voice_features):
        raise HTTPException(
            status_code=400, 
            detail="Invalid voice features. Required: pitch_mean, energy"
        )
    
    try:
        emotion_analysis = voice_analyzer.analyze_voice_features(voice_features)
        
        return {
            "primary_emotion": emotion_analysis.primary_emotion.value,
            "confidence": emotion_analysis.confidence,
            "risk_level": emotion_analysis.risk_level.value,
            "intensity": emotion_analysis.intensity,
            "indicators": emotion_analysis.emotional_indicators,
            "suggested_technique": emotion_analysis.suggested_technique,
            "patterns": emotion_analysis.patterns,
            "input_features": voice_features
        }
        
    except Exception as e:
        logger.error(f"Voice feature analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
