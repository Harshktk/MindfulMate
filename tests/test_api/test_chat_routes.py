# ============================================================================
# FILE: tests/test_api/test_chat_routes.py
# API endpoint tests
# ============================================================================

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# This requires the API to be importable
try:
    from src.api.main import app
    client = TestClient(app)
    API_AVAILABLE = True
except Exception as e:
    API_AVAILABLE = False
    API_ERROR = str(e)

@pytest.mark.skipif(not API_AVAILABLE, reason=f"API not available: {API_ERROR if not API_AVAILABLE else ''}")
class TestChatRoutes:
    """Test suite for chat API endpoints"""
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_chat_endpoint_basic(self):
        """Test basic chat functionality"""
        
        chat_request = {
            "message": "Hello, I'm feeling good today",
            "user_id": "test_user"
        }
        
        response = client.post("/chat", json=chat_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required response fields
        required_fields = [
            "response", "session_id", "emotion_detected", 
            "confidence", "risk_level", "suggested_technique"
        ]
        
        for field in required_fields:
            assert field in data
        
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0
        assert isinstance(data["confidence"], (int, float))
        assert 0 <= data["confidence"] <= 1
    
    def test_chat_with_voice_features(self):
        """Test chat with voice analysis"""
        
        chat_request = {
            "message": "I'm feeling anxious",
            "user_id": "test_user",
            "voice_features": {
                "pitch_mean": 180,
                "pitch_variance": 80,
                "speech_rate": 190,
                "energy": 0.7,
                "avg_pause_duration": 0.3
            }
        }
        
        response = client.post("/chat", json=chat_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should detect anxiety
        assert data["emotion_detected"] in ["anxious", "stressed"]
        assert data["risk_level"] in ["low", "medium", "high"]
    
    def test_text_analysis_endpoint(self):
        """Test text-only emotion analysis"""
        
        request_data = {
            "text": "I'm feeling overwhelmed by everything"
        }
        
        response = client.post("/analyze/text", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "primary_emotion", "confidence", "risk_level", 
            "intensity", "indicators", "suggested_technique"
        ]
        
        for field in required_fields:
            assert field in data
    
    def test_voice_analysis_endpoint(self):
        """Test voice-only emotion analysis"""
        
        request_data = {
            "user_id": "test_user",
            "voice_features": {
                "pitch_mean": 120,
                "pitch_variance": 25,
                "speech_rate": 100,
                "energy": 0.3,
                "avg_pause_duration": 1.5
            }
        }
        
        response = client.post("/analyze/voice", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should suggest depression indicators
        assert data["primary_emotion"] in ["depressed", "calm"]
        if "Low vocal energy" in str(data.get("indicators", [])):
            assert data["primary_emotion"] == "depressed"
    
    def test_crisis_resources_endpoint(self):
        """Test crisis resources endpoint"""
        
        response = client.get("/crisis-resources")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "immediate_help" in data
        assert "suicide_crisis_lifeline" in data["immediate_help"]
        assert "988" in data["immediate_help"]["suicide_crisis_lifeline"]["number"]
    
    def test_technique_guides(self):
        """Test therapeutic technique guides"""
        
        techniques = ["breathing_exercise", "grounding_technique", "behavioral_activation"]
        
        for technique in techniques:
            response = client.get(f"/techniques/{technique}")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "name" in data
            assert "steps" in data
            assert "benefits" in data
            assert isinstance(data["steps"], list)
            assert len(data["steps"]) > 0
    
    def test_invalid_requests(self):
        """Test handling of invalid requests"""
        
        # Empty message
        response = client.post("/chat", json={"user_id": "test"})
        assert response.status_code == 422  # Validation error
        
        # Missing text in analysis
        response = client.post("/analyze/text", json={})
        assert response.status_code == 400
        
        # Invalid technique
        response = client.get("/techniques/invalid_technique")
        assert response.status_code == 404
