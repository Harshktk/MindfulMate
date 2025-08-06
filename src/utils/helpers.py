# ============================================================================
# FILE: src/utils/helpers.py
# Helper functions
# ============================================================================

import uuid
import hashlib
from typing import Dict, Any
from datetime import datetime

def generate_session_id() -> str:
    """Generate unique session ID"""
    return str(uuid.uuid4())

def generate_user_id(identifier: str = None) -> str:
    """Generate anonymous user ID"""
    if identifier:
        # Create consistent hash for same identifier
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    else:
        # Random anonymous ID
        return f"anon_{uuid.uuid4().hex[:8]}"

def sanitize_text(text: str) -> str:
    """Sanitize user input text"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Limit length
    max_length = 1000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def format_timestamp(dt: datetime = None) -> str:
    """Format timestamp for API responses"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

def validate_voice_features(features: Dict[str, Any]) -> bool:
    """Validate voice feature dictionary"""
    required_features = ["pitch_mean", "energy"]
    optional_features = ["pitch_variance", "speech_rate", "avg_pause_duration"]
    
    # Check required features
    for feature in required_features:
        if feature not in features:
            return False
        if not isinstance(features[feature], (int, float)):
            return False
    
    return True