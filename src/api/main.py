# ============================================================================
# FILE: src/api/main.py
# FastAPI application for MindfulMate - ENHANCED VERSION
# ============================================================================

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import asyncio
from datetime import datetime
import uuid

# Import our core components
from src.core.gemma_client import GemmaClient
from src.core.emotion_analyzer import (
    VoiceEmotionAnalyzer, TextEmotionAnalyzer, 
    MultimodalEmotionFusion, EmotionAnalysis
)
from src.core.conversation_manager import ConversationManager
from src.utils.logger import setup_logging
from src.utils.config import load_config

# Import enhanced voice processing
from src.audio.enhanced_voice_processor import EnhancedVoiceProcessor

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration
config = load_config()

# Initialize FastAPI app
app = FastAPI(
    title="MindfulMate API - Enhanced",
    description="AI Mental Health Companion - Private, Empathetic, Available 24/7",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="frontend/web"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Serve web interfaces
@app.get("/", response_class=HTMLResponse)
async def serve_web_interface():
    """Serve the main web interface"""
    try:
        with open("frontend/web/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>MindfulMate API</h1><p>Web interface not found. Visit <a href='/docs'>/docs</a> for API documentation.</p>"
        )

@app.get("/mobile", response_class=HTMLResponse)
async def serve_mobile_interface():
    """Serve the mobile-optimized interface"""
    try:
        with open("frontend/web/mobile.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>MindfulMate Mobile</h1><p>Mobile interface not found. Use <a href='/'>main interface</a>.</p>"
        )

@app.get("/manifest.json")
async def serve_manifest():
    """Serve PWA manifest"""
    try:
        with open("frontend/web/manifest.json", "r", encoding="utf-8") as f:
            import json
            return JSONResponse(content=json.loads(f.read()))
    except FileNotFoundError:
        return JSONResponse(content={"error": "Manifest not found"})

# Global components (initialized on startup)
gemma_client = None
conversation_manager = None
voice_analyzer = None
text_analyzer = None
emotion_fusion = None
voice_processor = None

# ============================================================================
# PYDANTIC MODELS FOR API
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    user_id: str
    session_id: Optional[str] = None
    voice_features: Optional[Dict] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str
    emotion_detected: str
    confidence: float
    risk_level: str
    suggested_technique: str
    follow_up_question: Optional[str] = None
    professional_help_suggested: bool = False
    timestamp: str

class VoiceAnalysisRequest(BaseModel):
    """Voice analysis request"""
    user_id: str
    session_id: Optional[str] = None
    voice_features: Dict

class EmotionResponse(BaseModel):
    """Emotion analysis response"""
    primary_emotion: str
    confidence: float
    risk_level: str
    intensity: str
    indicators: List[str]
    suggested_technique: str
    patterns: List[str]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    gemma_status: str
    timestamp: str
    version: str

# ============================================================================
# STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global gemma_client, conversation_manager, voice_analyzer, text_analyzer, emotion_fusion, voice_processor
    
    logger.info("[STARTUP] Starting MindfulMate API Enhanced...")
    
    try:
        # Initialize Gemma client
        gemma_client = GemmaClient(
            model_name=config.get('ollama', {}).get('model', 'gemma3n:e4b'),
            host=config.get('ollama', {}).get('host', 'http://localhost:11434')
        )
        logger.info("✅ Gemma client initialized")
        
        # Initialize conversation manager
        conversation_manager = ConversationManager(
            max_history=config.get('conversation', {}).get('max_history', 20),
            session_timeout=config.get('conversation', {}).get('timeout', 3600)
        )
        logger.info("✅ Conversation manager initialized")
        
        # Initialize emotion analyzers
        voice_analyzer = VoiceEmotionAnalyzer()
        text_analyzer = TextEmotionAnalyzer(gemma_client)
        emotion_fusion = MultimodalEmotionFusion()
        logger.info("✅ Emotion analyzers initialized")
        
        # Initialize enhanced voice processor
        voice_processor = EnhancedVoiceProcessor()
        logger.info("✅ Enhanced voice processor initialized")
        
        logger.info("🎉 MindfulMate API Enhanced startup complete!")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down MindfulMate API...")
    
    if conversation_manager:
        conversation_manager.cleanup_expired_sessions()
    
    logger.info("✅ Shutdown complete")

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    
    # Test Gemma connection
    try:
        test_response = await gemma_client.generate_therapeutic_response(
            "test", {"primary_emotion": "calm", "risk_level": "low"}
        )
        gemma_status = "healthy"
    except Exception as e:
        logger.error(f"Gemma health check failed: {e}")
        gemma_status = "unhealthy"
    
    return HealthResponse(
        status="healthy" if gemma_status == "healthy" else "degraded",
        gemma_status=gemma_status,
        timestamp=datetime.now().isoformat(),
        version="1.1.0"
    )

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check for monitoring"""
    
    health_data = {
        "api_status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.1.0",
        "components": {}
    }
    
    # Test each component
    try:
        # Gemma client
        await gemma_client.analyze_emotion_from_text("test")
        health_data["components"]["gemma_client"] = "healthy"
    except Exception as e:
        health_data["components"]["gemma_client"] = f"unhealthy: {str(e)}"
    
    # Conversation manager
    try:
        test_context = conversation_manager.get_or_create_context("health_check")
        health_data["components"]["conversation_manager"] = "healthy"
        health_data["active_sessions"] = len(conversation_manager.active_sessions)
    except Exception as e:
        health_data["components"]["conversation_manager"] = f"unhealthy: {str(e)}"
    
    # Emotion analyzers
    try:
        voice_analyzer.analyze_voice_features({"pitch_mean": 150, "energy": 0.5})
        health_data["components"]["voice_analyzer"] = "healthy"
    except Exception as e:
        health_data["components"]["voice_analyzer"] = f"unhealthy: {str(e)}"
    
    # Enhanced voice processor
    try:
        await voice_processor.process_audio_blob(b"test_audio_data")
        health_data["components"]["voice_processor"] = "healthy"
    except Exception as e:
        health_data["components"]["voice_processor"] = f"unhealthy: {str(e)}"
    
    return health_data

# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for text conversations"""
    
    try:
        # Get or create conversation context
        context = conversation_manager.get_or_create_context(
            request.user_id, request.session_id
        )
        
        # Analyze text emotion
        text_emotion = await text_analyzer.analyze_text_emotion(
            request.message, 
            conversation_manager.get_conversation_summary(context)
        )
        
        # Analyze voice emotion if features provided
        voice_emotion = None
        if request.voice_features:
            voice_emotion = voice_analyzer.analyze_voice_features(request.voice_features)
        
        # Fuse emotions for comprehensive analysis
        final_emotion = emotion_fusion.fuse_emotions(voice_emotion, text_emotion)
        
        # Generate therapeutic response
        ai_response = await gemma_client.generate_therapeutic_response(
            request.message,
            {
                "primary_emotion": final_emotion.primary_emotion.value,
                "risk_level": final_emotion.risk_level.value,
                "confidence": final_emotion.confidence,
                "emotional_indicators": final_emotion.emotional_indicators
            },
            context.conversation_history
        )
        
        # Update conversation context
        conversation_manager.add_interaction(
            context, 
            request.message, 
            ai_response.get("response", ""), 
            final_emotion
        )
        
        # Check if professional help should be suggested
        professional_help = conversation_manager.should_suggest_professional_help(context)
        
        return ChatResponse(
            response=ai_response.get("response", "I'm here to support you."),
            session_id=context.session_id,
            emotion_detected=final_emotion.primary_emotion.value,
            confidence=final_emotion.confidence,
            risk_level=final_emotion.risk_level.value,
            suggested_technique=final_emotion.suggested_technique,
            follow_up_question=ai_response.get("follow_up_question"),
            professional_help_suggested=professional_help,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ============================================================================
# ENHANCED VOICE ENDPOINTS
# ============================================================================

@app.post("/voice/analyze")
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

@app.post("/voice/features")
async def analyze_voice_features_endpoint(request: dict):
    """Analyze emotion from pre-extracted voice features"""
    
    voice_features = request.get("voice_features", {})
    
    # Basic validation
    if not voice_features.get("pitch_mean") or not voice_features.get("energy"):
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

# ============================================================================
# EMOTION ANALYSIS ENDPOINTS
# ============================================================================

@app.post("/analyze/text", response_model=EmotionResponse)
async def analyze_text_emotion(request: Dict):
    """Analyze emotion from text only"""
    
    try:
        text = request.get("text", "")
        context = request.get("context", {})
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        emotion_analysis = await text_analyzer.analyze_text_emotion(text, context)
        
        return EmotionResponse(
            primary_emotion=emotion_analysis.primary_emotion.value,
            confidence=emotion_analysis.confidence,
            risk_level=emotion_analysis.risk_level.value,
            intensity=emotion_analysis.intensity,
            indicators=emotion_analysis.emotional_indicators,
            suggested_technique=emotion_analysis.suggested_technique,
            patterns=emotion_analysis.patterns
        )
        
    except Exception as e:
        logger.error(f"Text emotion analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/voice", response_model=EmotionResponse)
async def analyze_voice_emotion(request: VoiceAnalysisRequest):
    """Analyze emotion from voice features"""
    
    try:
        emotion_analysis = voice_analyzer.analyze_voice_features(request.voice_features)
        
        return EmotionResponse(
            primary_emotion=emotion_analysis.primary_emotion.value,
            confidence=emotion_analysis.confidence,
            risk_level=emotion_analysis.risk_level.value,
            intensity=emotion_analysis.intensity,
            indicators=emotion_analysis.emotional_indicators,
            suggested_technique=emotion_analysis.suggested_technique,
            patterns=emotion_analysis.patterns
        )
        
    except Exception as e:
        logger.error(f"Voice emotion analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/multimodal", response_model=EmotionResponse)
async def analyze_multimodal_emotion(request: Dict):
    """Analyze emotion from both text and voice"""
    
    try:
        text = request.get("text", "")
        voice_features = request.get("voice_features", {})
        context = request.get("context", {})
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Analyze text
        text_emotion = await text_analyzer.analyze_text_emotion(text, context)
        
        # Analyze voice if features provided
        voice_emotion = None
        if voice_features:
            voice_emotion = voice_analyzer.analyze_voice_features(voice_features)
        
        # Fuse results
        final_emotion = emotion_fusion.fuse_emotions(voice_emotion, text_emotion)
        
        return EmotionResponse(
            primary_emotion=final_emotion.primary_emotion.value,
            confidence=final_emotion.confidence,
            risk_level=final_emotion.risk_level.value,
            intensity=final_emotion.intensity,
            indicators=final_emotion.emotional_indicators,
            suggested_technique=final_emotion.suggested_technique,
            patterns=final_emotion.patterns
        )
        
    except Exception as e:
        logger.error(f"Multimodal emotion analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/session/{session_id}")
async def get_session_info(session_id: str, user_id: str):
    """Get session information"""
    
    try:
        context = conversation_manager.get_or_create_context(user_id, session_id)
        summary = conversation_manager.get_conversation_summary(context)
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "session_start": context.session_start.isoformat(),
            "last_interaction": context.last_interaction.isoformat(),
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Session info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}")
async def end_session(session_id: str, user_id: str):
    """End and cleanup session"""
    
    try:
        context_key = f"{user_id}:{session_id}"
        if context_key in conversation_manager.active_sessions:
            del conversation_manager.active_sessions[context_key]
            return {"message": "Session ended successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except Exception as e:
        logger.error(f"End session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# THERAPEUTIC ENDPOINTS
# ============================================================================

@app.get("/techniques/{technique_name}")
async def get_technique_guide(technique_name: str):
    """Get guided therapeutic technique"""
    
    techniques = {
        "breathing_exercise": {
            "name": "4-7-8 Breathing Exercise",
            "description": "A calming breathing technique to reduce anxiety",
            "steps": [
                "Sit comfortably and place one hand on your chest, one on your belly",
                "Breathe in through your nose for 4 counts",
                "Hold your breath for 7 counts", 
                "Exhale slowly through your mouth for 8 counts",
                "Repeat 3-4 times"
            ],
            "duration_minutes": 3,
            "benefits": ["Reduces anxiety", "Calms nervous system", "Improves focus"]
        },
        "grounding_technique": {
            "name": "5-4-3-2-1 Grounding",
            "description": "A mindfulness technique to reduce overwhelm",
            "steps": [
                "Name 5 things you can see",
                "Name 4 things you can touch",
                "Name 3 things you can hear",
                "Name 2 things you can smell",
                "Name 1 thing you can taste"
            ],
            "duration_minutes": 5,
            "benefits": ["Reduces overwhelm", "Increases present-moment awareness", "Calms racing thoughts"]
        },
        "behavioral_activation": {
            "name": "Small Step Planning",
            "description": "Break overwhelming tasks into manageable steps", 
            "steps": [
                "Choose one small task you've been avoiding",
                "Break it into 3 smaller steps",
                "Commit to doing just the first step today",
                "Celebrate completing that step",
                "Plan the next step for tomorrow"
            ],
            "duration_minutes": 10,
            "benefits": ["Builds momentum", "Reduces overwhelm", "Increases sense of accomplishment"]
        }
    }
    
    if technique_name not in techniques:
        raise HTTPException(status_code=404, detail="Technique not found")
    
    return techniques[technique_name]

@app.get("/crisis-resources")
async def get_crisis_resources():
    """Get crisis intervention resources"""
    
    return {
        "immediate_help": {
            "suicide_crisis_lifeline": {
                "number": "988",
                "description": "24/7 suicide and crisis prevention",
                "available": "24/7"
            },
            "crisis_text_line": {
                "number": "Text HOME to 741741", 
                "description": "24/7 crisis support via text",
                "available": "24/7"
            },
            "emergency_services": {
                "number": "911",
                "description": "Emergency medical services",
                "available": "24/7"
            }
        },
        "online_resources": [
            {
                "name": "National Suicide Prevention Lifeline",
                "url": "https://suicidepreventionlifeline.org",
                "description": "Resources and chat support"
            },
            {
                "name": "Crisis Text Line", 
                "url": "https://crisistextline.org",
                "description": "Text-based crisis support"
            }
        ],
        "safety_planning": [
            "Remove or secure means of self-harm",
            "Reach out to trusted friends or family",
            "Contact mental health professionals",
            "Go to emergency room if in immediate danger"
        ]
    }
