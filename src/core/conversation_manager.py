# ============================================================================
# FILE: src/core/conversation_manager.py
# Manages conversation context and flow
# ============================================================================

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid
import logging
from dataclasses import dataclass
from .emotion_analyzer import EmotionAnalysis, EmotionState, RiskLevel

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Conversation context and state management"""
    user_id: str
    session_id: str
    conversation_history: List[Dict]
    emotion_history: List[EmotionAnalysis]
    risk_flags: List[str]
    last_interaction: datetime
    session_start: datetime
    therapeutic_goals: List[str]
    check_in_schedule: Dict
    
class ConversationManager:
    """Manages conversation state and therapeutic continuity"""
    
    def __init__(self, max_history: int = 20, session_timeout: int = 3600):
        self.max_history = max_history
        self.session_timeout = session_timeout
        self.active_sessions = {}
        
        # Therapeutic patterns to track
        self.concern_patterns = [
            "repeated_crisis_language",
            "persistent_negative_mood", 
            "social_isolation_mentions",
            "substance_use_indicators",
            "sleep_disturbance_reports"
        ]
    
    def get_or_create_context(self, user_id: str, session_id: Optional[str] = None) -> ConversationContext:
        """Get existing context or create new session"""
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Check if session exists and is valid
        context_key = f"{user_id}:{session_id}"
        
        if context_key in self.active_sessions:
            context = self.active_sessions[context_key]
            
            # Check if session has expired
            if datetime.now() - context.last_interaction > timedelta(seconds=self.session_timeout):
                logger.info(f"Session {session_id} expired, creating new session")
                return self._create_new_context(user_id, session_id)
            
            return context
        
        return self._create_new_context(user_id, session_id)
    
    def _create_new_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Create new conversation context"""
        
        context = ConversationContext(
            user_id=user_id,
            session_id=session_id,
            conversation_history=[],
            emotion_history=[],
            risk_flags=[],
            last_interaction=datetime.now(),
            session_start=datetime.now(),
            therapeutic_goals=[],
            check_in_schedule={}
        )
        
        context_key = f"{user_id}:{session_id}"
        self.active_sessions[context_key] = context
        
        logger.info(f"Created new session {session_id} for user {user_id}")
        return context
    
    def add_interaction(self, context: ConversationContext, 
                       user_input: str, ai_response: str,
                       emotion_analysis: EmotionAnalysis) -> ConversationContext:
        """Add new interaction to conversation history"""
        
        # Add to conversation history
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": ai_response,
            "emotion": emotion_analysis.primary_emotion.value,
            "risk_level": emotion_analysis.risk_level.value,
            "confidence": emotion_analysis.confidence
        }
        
        context.conversation_history.append(interaction)
        context.emotion_history.append(emotion_analysis)
        context.last_interaction = datetime.now()
        
        # Maintain history size limit
        if len(context.conversation_history) > self.max_history:
            context.conversation_history = context.conversation_history[-self.max_history:]
            context.emotion_history = context.emotion_history[-self.max_history:]
        
        # Update risk flags and patterns
        self._update_risk_assessment(context, emotion_analysis)
        
        # Update therapeutic goals if needed
        self._update_therapeutic_goals(context, emotion_analysis)
        
        return context
    
    def _update_risk_assessment(self, context: ConversationContext, 
                               emotion_analysis: EmotionAnalysis):
        """Update risk flags based on conversation patterns"""
        
        # Clear old flags
        context.risk_flags = [flag for flag in context.risk_flags 
                             if not flag.startswith("session_")]
        
        # Check for crisis patterns
        if emotion_analysis.risk_level == RiskLevel.CRISIS:
            context.risk_flags.append("session_crisis_detected")
        
        # Check for persistent negative emotions
        recent_emotions = context.emotion_history[-5:] if len(context.emotion_history) >= 5 else context.emotion_history
        
        negative_emotions = [EmotionState.DEPRESSED, EmotionState.ANXIOUS, EmotionState.STRESSED]
        negative_count = sum(1 for analysis in recent_emotions 
                           if analysis.primary_emotion in negative_emotions)
        
        if negative_count >= 4:  # 4 out of 5 recent interactions
            context.risk_flags.append("session_persistent_negative_mood")
        
        # Check for escalating risk
        if len(context.emotion_history) >= 3:
            recent_risks = [analysis.risk_level for analysis in context.emotion_history[-3:]]
            risk_values = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRISIS: 4}
            
            if all(risk_values[recent_risks[i]] <= risk_values[recent_risks[i+1]] 
                   for i in range(len(recent_risks)-1)):
                context.risk_flags.append("session_escalating_risk")
    
    def _update_therapeutic_goals(self, context: ConversationContext,
                                 emotion_analysis: EmotionAnalysis):
        """Update therapeutic goals based on detected patterns"""
        
        # Add goals based on primary emotion
        emotion = emotion_analysis.primary_emotion
        
        goal_mapping = {
            EmotionState.ANXIOUS: "anxiety_management",
            EmotionState.DEPRESSED: "mood_improvement",
            EmotionState.STRESSED: "stress_reduction",
            EmotionState.ANGRY: "anger_management"
        }
        
        if emotion in goal_mapping:
            goal = goal_mapping[emotion]
            if goal not in context.therapeutic_goals:
                context.therapeutic_goals.append(goal)
        
        # Limit goals to prevent overwhelming
        if len(context.therapeutic_goals) > 3:
            context.therapeutic_goals = context.therapeutic_goals[-3:]
    
    def get_conversation_summary(self, context: ConversationContext) -> Dict:
        """Generate conversation summary for AI context"""
        
        if not context.conversation_history:
            return {"summary": "New conversation", "key_points": []}
        
        # Recent emotion trend
        recent_emotions = [analysis.primary_emotion.value 
                          for analysis in context.emotion_history[-5:]]
        
        # Risk assessment
        current_risk = context.emotion_history[-1].risk_level.value if context.emotion_history else "low"
        
        # Session duration
        session_duration = datetime.now() - context.session_start
        
        summary = {
            "session_length_minutes": int(session_duration.total_seconds() / 60),
            "total_interactions": len(context.conversation_history),
            "recent_emotions": recent_emotions,
            "current_risk_level": current_risk,
            "active_risk_flags": context.risk_flags,
            "therapeutic_goals": context.therapeutic_goals,
            "key_themes": self._extract_key_themes(context)
        }
        
        return summary
    
    def _extract_key_themes(self, context: ConversationContext) -> List[str]:
        """Extract key themes from conversation"""
        themes = []
        
        # Analyze recent interactions for themes
        recent_text = " ".join([
            interaction.get("user", "") 
            for interaction in context.conversation_history[-5:]
        ]).lower()
        
        # Common mental health themes
        theme_keywords = {
            "work_stress": ["work", "job", "boss", "deadline", "pressure"],
            "relationships": ["partner", "friend", "family", "relationship", "lonely"],
            "health_concerns": ["sick", "health", "pain", "tired", "sleep"],
            "financial_stress": ["money", "bills", "debt", "financial", "afford"],
            "academic_stress": ["school", "exam", "grade", "study", "homework"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in recent_text for keyword in keywords):
                themes.append(theme)
        
        return themes[:3]  # Limit to top 3 themes
    
    def should_suggest_professional_help(self, context: ConversationContext) -> bool:
        """Determine if professional help should be suggested"""
        
        # Immediate crisis
        if "session_crisis_detected" in context.risk_flags:
            return True
        
        # Persistent high risk
        if ("session_persistent_negative_mood" in context.risk_flags and 
            "session_escalating_risk" in context.risk_flags):
            return True
        
        # Extended session with high emotions
        session_duration = datetime.now() - context.session_start
        if (session_duration > timedelta(hours=2) and 
            len(context.conversation_history) > 15):
            return True
        
        return False
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions to free memory"""
        
        cutoff_time = datetime.now() - timedelta(seconds=self.session_timeout)
        expired_sessions = [
            key for key, context in self.active_sessions.items()
            if context.last_interaction < cutoff_time
        ]
        
        for session_key in expired_sessions:
            del self.active_sessions[session_key]
            logger.info(f"Cleaned up expired session: {session_key}")
        
        return len(expired_sessions)