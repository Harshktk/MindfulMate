# ============================================================================
# FILE: src/therapeutic/crisis_detection.py
# Crisis detection and intervention protocols
# ============================================================================

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class CrisisType(Enum):
    """Types of crisis situations"""
    SUICIDAL_IDEATION = "suicidal_ideation"
    SELF_HARM = "self_harm"
    SEVERE_DEPRESSION = "severe_depression"
    PANIC_ATTACK = "panic_attack"
    PSYCHOTIC_EPISODE = "psychotic_episode"
    SUBSTANCE_ABUSE = "substance_abuse"

class CrisisUrgency(Enum):
    """Crisis urgency levels"""
    IMMEDIATE = "immediate"  # Call 911
    URGENT = "urgent"        # Crisis hotline
    MONITOR = "monitor"      # Increased check-ins

class CrisisDetector:
    """Detect and classify crisis situations"""
    
    def __init__(self):
        self.crisis_patterns = {
            CrisisType.SUICIDAL_IDEATION: {
                "keywords": [
                    "suicide", "kill myself", "end it all", "want to die",
                    "better off dead", "end my life", "not worth living",
                    "suicide plan", "ways to die"
                ],
                "phrases": [
                    "i want to die", "i should die", "kill me",
                    "end it all", "can't go on", "no reason to live"
                ],
                "urgency": CrisisUrgency.IMMEDIATE
            },
            CrisisType.SELF_HARM: {
                "keywords": [
                    "hurt myself", "cut myself", "self harm", "cutting",
                    "burn myself", "punch wall", "harm myself"
                ],
                "phrases": [
                    "want to hurt myself", "cutting helps", "pain makes it better"
                ],
                "urgency": CrisisUrgency.URGENT
            },
            CrisisType.SEVERE_DEPRESSION: {
                "keywords": [
                    "hopeless", "worthless", "useless", "burden",
                    "empty", "numb", "void", "pointless"
                ],
                "phrases": [
                    "nothing matters", "no point", "completely hopeless",
                    "total failure", "everyone hates me"
                ],
                "urgency": CrisisUrgency.MONITOR
            },
            CrisisType.PANIC_ATTACK: {
                "keywords": [
                    "panic attack", "can't breathe", "heart racing",
                    "chest pain", "dizzy", "dying"
                ],
                "phrases": [
                    "having a panic attack", "can't catch my breath",
                    "feel like dying", "heart pounding"
                ],
                "urgency": CrisisUrgency.URGENT
            }
        }
    
    def detect_crisis(self, text: str, emotion_context: Dict = None) -> Dict:
        """Detect crisis situations in text"""
        
        text_lower = text.lower()
        detected_crises = []
        highest_urgency = None
        
        # Check each crisis type
        for crisis_type, patterns in self.crisis_patterns.items():
            score = self._calculate_crisis_score(text_lower, patterns)
            
            if score > 0.3:  # Threshold for crisis detection
                detected_crises.append({
                    "type": crisis_type.value,
                    "score": score,
                    "urgency": patterns["urgency"].value
                })
                
                # Track highest urgency
                if (highest_urgency is None or 
                    self._urgency_priority(patterns["urgency"]) > 
                    self._urgency_priority(highest_urgency)):
                    highest_urgency = patterns["urgency"]
        
        # Add context-based crisis detection
        if emotion_context:
            context_crisis = self._detect_contextual_crisis(emotion_context)
            if context_crisis:
                detected_crises.extend(context_crisis)
        
        return {
            "crisis_detected": len(detected_crises) > 0,
            "crisis_types": detected_crises,
            "highest_urgency": highest_urgency.value if highest_urgency else None,
            "immediate_action_needed": highest_urgency == CrisisUrgency.IMMEDIATE,
            "resources_needed": self._get_crisis_resources(detected_crises),
            "safety_planning_required": len(detected_crises) > 0
        }
    
    def _calculate_crisis_score(self, text: str, patterns: Dict) -> float:
        """Calculate crisis score for a specific type"""
        score = 0.0
        
        # Check keywords
        keyword_matches = sum(1 for keyword in patterns["keywords"] if keyword in text)
        keyword_score = min(keyword_matches * 0.3, 0.8)
        
        # Check phrases
        phrase_matches = sum(1 for phrase in patterns["phrases"] if phrase in text)
        phrase_score = min(phrase_matches * 0.5, 1.0)
        
        # Combine scores
        score = max(keyword_score, phrase_score)
        
        return score
    
    def _detect_contextual_crisis(self, emotion_context: Dict) -> List[Dict]:
        """Detect crisis from emotional context"""
        crises = []
        
        risk_level = emotion_context.get("risk_level", "low")
        confidence = emotion_context.get("confidence", 0.0)
        
        # High-confidence high-risk situations
        if risk_level == "crisis" and confidence > 0.7:
            crises.append({
                "type": "contextual_crisis",
                "score": confidence,
                "urgency": "immediate"
            })
        elif risk_level == "high" and confidence > 0.8:
            crises.append({
                "type": "contextual_high_risk",
                "score": confidence,
                "urgency": "urgent"
            })
        
        return crises
    
    def _urgency_priority(self, urgency: CrisisUrgency) -> int:
        """Get numeric priority for urgency levels"""
        priorities = {
            CrisisUrgency.MONITOR: 1,
            CrisisUrgency.URGENT: 2,
            CrisisUrgency.IMMEDIATE: 3
        }
        return priorities.get(urgency, 0)
    
    def _get_crisis_resources(self, detected_crises: List[Dict]) -> Dict:
        """Get appropriate crisis resources"""
        
        if not detected_crises:
            return {}
        
        # Determine needed resources based on crisis types
        resources = {
            "immediate_help": {},
            "professional_resources": [],
            "self_help_techniques": []
        }
        
        crisis_types = [crisis["type"] for crisis in detected_crises]
        urgencies = [crisis["urgency"] for crisis in detected_crises]
        
        # Immediate help resources
        if "immediate" in urgencies:
            resources["immediate_help"] = {
                "suicide_crisis_lifeline": "988",
                "emergency_services": "911",
                "crisis_text_line": "Text HOME to 741741"
            }
        elif "urgent" in urgencies:
            resources["immediate_help"] = {
                "suicide_crisis_lifeline": "988",
                "crisis_text_line": "Text HOME to 741741"
            }
        
        # Professional resources
        if any(crisis in crisis_types for crisis in ["suicidal_ideation", "self_harm"]):
            resources["professional_resources"].extend([
                "Emergency room evaluation",
                "Mental health crisis center",
                "Psychiatrist or therapist"
            ])
        
        # Self-help techniques (only for lower urgency)
        if all(urgency != "immediate" for urgency in urgencies):
            resources["self_help_techniques"].extend([
                "Safety planning",
                "Grounding techniques",
                "Crisis coping skills"
            ])
        
        return resources

class CrisisInterventionProtocol:
    """Handle crisis intervention responses"""
    
    def __init__(self):
        self.intervention_responses = {
            CrisisType.SUICIDAL_IDEATION: {
                "immediate_response": "I'm very concerned about what you've shared. Your life has value and there are people who want to help. Let's talk about keeping you safe right now.",
                "safety_questions": [
                    "Do you have a plan to hurt yourself?",
                    "Do you have access to means of self-harm?",
                    "Are you alone right now?",
                    "Is there someone you trust who could come be with you?"
                ],
                "resources": ["988 Suicide & Crisis Lifeline", "Emergency Services 911"]
            },
            CrisisType.SELF_HARM: {
                "immediate_response": "I'm worried about you wanting to hurt yourself. Self-harm might provide temporary relief, but there are safer ways to cope with these feelings.",
                "safety_questions": [
                    "What usually triggers your urge to self-harm?",
                    "Do you have a support person you can call?",
                    "Are you in a safe environment right now?"
                ],
                "resources": ["Crisis Text Line", "Self-Injury Outreach & Support"]
            },
            CrisisType.SEVERE_DEPRESSION: {
                "immediate_response": "I can hear how much pain you're in right now. These feelings of hopelessness are symptoms of depression, and they can improve with proper support.",
                "safety_questions": [
                    "Have you had thoughts of hurting yourself?",
                    "Who in your life knows you're struggling?",
                    "What has helped you get through difficult times before?"
                ],
                "resources": ["Mental health professionals", "Depression support groups"]
            }
        }
    
    def generate_crisis_response(self, crisis_info: Dict, user_context: Dict = None) -> Dict:
        """Generate appropriate crisis intervention response"""
        
        if not crisis_info.get("crisis_detected", False):
            return {"crisis_response": False}
        
        crisis_types = [crisis["type"] for crisis in crisis_info["crisis_types"]]
        highest_urgency = crisis_info.get("highest_urgency", "monitor")
        
        # Determine primary crisis type
        primary_crisis = self._determine_primary_crisis(crisis_types)
        
        # Get intervention protocol
        protocol = self.intervention_responses.get(primary_crisis)
        if not protocol:
            protocol = self._get_default_crisis_protocol()
        
        # Build response
        response = {
            "crisis_response": True,
            "urgency_level": highest_urgency,
            "immediate_response": protocol["immediate_response"],
            "safety_assessment_needed": True,
            "recommended_actions": self._get_recommended_actions(highest_urgency),
            "crisis_resources": crisis_info.get("resources_needed", {}),
            "follow_up_required": True
        }
        
        # Add safety questions for assessment
        if highest_urgency in ["immediate", "urgent"]:
            response["safety_questions"] = protocol.get("safety_questions", [])
        
        return response
    
    def _determine_primary_crisis(self, crisis_types: List[str]) -> CrisisType:
        """Determine the primary crisis type to address"""
        
        # Priority order (most severe first)
        priority_order = [
            CrisisType.SUICIDAL_IDEATION,
            CrisisType.SELF_HARM,
            CrisisType.SEVERE_DEPRESSION,
            CrisisType.PANIC_ATTACK
        ]
        
        for crisis_type in priority_order:
            if crisis_type.value in crisis_types:
                return crisis_type
        
        # Default to first detected crisis
        if crisis_types:
            return CrisisType(crisis_types[0])
        
        return CrisisType.SEVERE_DEPRESSION
    
    def _get_recommended_actions(self, urgency: str) -> List[str]:
        """Get recommended actions based on urgency"""
        
        actions = {
            "immediate": [
                "Call 911 if in immediate danger",
                "Call 988 Suicide & Crisis Lifeline",
                "Remove access to means of self-harm",
                "Stay with a trusted person",
                "Go to emergency room"
            ],
            "urgent": [
                "Call 988 Suicide & Crisis Lifeline",
                "Text HOME to 741741 for crisis support",
                "Contact a mental health professional",
                "Reach out to trusted friend or family",
                "Create a safety plan"
            ],
            "monitor": [
                "Schedule appointment with mental health professional",
                "Increase social support",
                "Monitor mood and thoughts closely",
                "Use coping strategies",
                "Consider therapy or counseling"
            ]
        }
        
        return actions.get(urgency, actions["monitor"])
    
    def _get_default_crisis_protocol(self) -> Dict:
        """Default crisis protocol when specific type not found"""
        
        return {
            "immediate_response": "I'm concerned about what you've shared. Let's focus on keeping you safe right now and getting you the support you need.",
            "safety_questions": [
                "Are you safe right now?",
                "Do you have someone you can call for support?",
                "Have you been having thoughts of hurting yourself?"
            ]
        }

class SafetyPlanning:
    """Create and manage safety plans for users in crisis"""
    
    def __init__(self):
        self.safety_plan_template = {
            "warning_signs": [],
            "coping_strategies": [],
            "support_contacts": [],
            "professional_contacts": [],
            "environment_safety": [],
            "crisis_resources": []
        }
    
    def create_safety_plan_prompt(self, crisis_info: Dict) -> str:
        """Create prompts to help user develop safety plan"""
        
        crisis_types = [crisis["type"] for crisis in crisis_info.get("crisis_types", [])]
        
        if "suicidal_ideation" in crisis_types:
            return self._suicide_safety_plan_prompt()
        elif "self_harm" in crisis_types:
            return self._self_harm_safety_plan_prompt()
        else:
            return self._general_safety_plan_prompt()
    
    def _suicide_safety_plan_prompt(self) -> str:
        """Safety planning for suicidal ideation"""
        
        return """
Let's work together to create a safety plan to help keep you safe:

1. **Warning Signs**: What thoughts, feelings, or situations usually come before you feel suicidal?

2. **Coping Strategies**: What are some things you can do on your own when you start having these thoughts?

3. **People for Support**: Who are 2-3 people you could reach out to when you're in crisis?

4. **Professional Help**: What mental health professionals or crisis services can you contact?

5. **Making Your Environment Safe**: What means of self-harm should be removed or secured?

6. **Emergency Contacts**: 
   - 988 Suicide & Crisis Lifeline (24/7)
   - Emergency Services: 911
   - Crisis Text Line: Text HOME to 741741

Would you like to start with identifying your warning signs?
"""
    
    def _self_harm_safety_plan_prompt(self) -> str:
        """Safety planning for self-harm"""
        
        return """
Let's create a plan to help you cope with urges to self-harm in healthier ways:

1. **Triggers**: What situations or feelings usually lead to urges to self-harm?

2. **Alternative Coping**: What are some safer ways to cope with these feelings?
   - Ice cubes on skin
   - Drawing red lines instead of cutting
   - Intense exercise
   - Calling someone

3. **Support Network**: Who can you reach out to when you have these urges?

4. **Professional Help**: Mental health professionals who understand self-harm

5. **Emergency Resources**:
   - Crisis Text Line: Text HOME to 741741
   - Self-Injury Outreach & Support

Which area would you like to start working on?
"""
    
    def _general_safety_plan_prompt(self) -> str:
        """General safety planning"""
        
        return """
Let's create a plan to help you through difficult times:

1. **Early Warning Signs**: What signals tell you that you're starting to struggle?

2. **Coping Strategies**: What helps you feel better when you're having a hard time?

3. **Support People**: Who can you talk to when you need support?

4. **Professional Resources**: Mental health professionals you can contact

5. **Crisis Resources**: Emergency contacts for serious situations

What area feels most important to you right now?
"""
