# ============================================================================
# FILE: src/therapeutic/cbt_techniques.py
# Cognitive Behavioral Therapy techniques and exercises
# ============================================================================

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class CBTTechniques:
    """Cognitive Behavioral Therapy techniques for mental health support"""
    
    def __init__(self):
        self.techniques = {
            "thought_challenging": {
                "name": "Thought Challenging",
                "description": "Question and examine negative thought patterns",
                "steps": [
                    "What is the specific thought you're having?",
                    "What evidence supports this thought?", 
                    "What evidence contradicts this thought?",
                    "What would you tell a friend having this thought?",
                    "What's a more balanced way to think about this?"
                ],
                "use_cases": ["anxiety", "depression", "catastrophizing"]
            },
            "behavioral_activation": {
                "name": "Behavioral Activation",
                "description": "Increase engagement in meaningful activities",
                "steps": [
                    "List 3 activities you used to enjoy",
                    "Choose the easiest one to start with",
                    "Break it into small, manageable steps",
                    "Schedule the first step for today",
                    "Notice how you feel after completing it"
                ],
                "use_cases": ["depression", "apathy", "isolation"]
            },
            "grounding_5_4_3_2_1": {
                "name": "5-4-3-2-1 Grounding",
                "description": "Ground yourself in the present moment",
                "steps": [
                    "Name 5 things you can see around you",
                    "Name 4 things you can physically touch",
                    "Name 3 things you can hear right now",
                    "Name 2 things you can smell",
                    "Name 1 thing you can taste"
                ],
                "use_cases": ["anxiety", "panic", "overwhelm", "dissociation"]
            },
            "breathing_4_7_8": {
                "name": "4-7-8 Breathing",
                "description": "Calming breathing technique to reduce anxiety",
                "steps": [
                    "Sit comfortably with your back straight",
                    "Place one hand on chest, one on belly",
                    "Breathe in through nose for 4 counts",
                    "Hold your breath for 7 counts",
                    "Exhale through mouth for 8 counts",
                    "Repeat 3-4 times"
                ],
                "use_cases": ["anxiety", "stress", "panic", "insomnia"]
            }
        }
    
    def get_technique_for_emotion(self, emotion: str, intensity: str = "medium") -> Dict:
        """Get appropriate CBT technique based on detected emotion"""
        
        technique_mapping = {
            "anxious": "breathing_4_7_8",
            "stressed": "grounding_5_4_3_2_1", 
            "depressed": "behavioral_activation",
            "angry": "thought_challenging",
            "overwhelmed": "grounding_5_4_3_2_1"
        }
        
        technique_name = technique_mapping.get(emotion, "grounding_5_4_3_2_1")
        technique = self.techniques.get(technique_name)
        
        if technique:
            return {
                "technique": technique_name,
                "name": technique["name"],
                "description": technique["description"],
                "steps": technique["steps"],
                "estimated_time": len(technique["steps"]) * 2,  # 2 minutes per step
                "difficulty": "easy" if intensity == "low" else "moderate"
            }
        
        return self._get_default_technique()
    
    def get_guided_exercise(self, technique_name: str) -> Dict:
        """Get guided version of CBT exercise"""
        
        if technique_name not in self.techniques:
            return {"error": "Technique not found"}
        
        technique = self.techniques[technique_name]
        
        # Create guided version with prompts
        guided_steps = []
        for i, step in enumerate(technique["steps"], 1):
            guided_steps.append({
                "step_number": i,
                "instruction": step,
                "prompt": f"Let me know when you've completed step {i}, and I'll guide you to the next one.",
                "validation": f"How did step {i} feel for you?"
            })
        
        return {
            "technique_name": technique_name,
            "guided_steps": guided_steps,
            "total_steps": len(guided_steps),
            "estimated_duration": len(guided_steps) * 2
        }
    
    def _get_default_technique(self) -> Dict:
        """Default technique when specific one not found"""
        
        return {
            "technique": "grounding_5_4_3_2_1",
            "name": "Grounding Exercise",
            "description": "A simple technique to help you feel more present",
            "steps": self.techniques["grounding_5_4_3_2_1"]["steps"],
            "estimated_time": 5,
            "difficulty": "easy"
        }
