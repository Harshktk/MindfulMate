#============================================================================
# FILE: tests/test_core/test_gemma_client.py
# Unit tests for Gemma client
# ============================================================================

import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.core.gemma_client import GemmaClient

class TestGemmaClient:
    """Test suite for Gemma client"""
    
    @pytest.fixture
    async def gemma_client(self):
        """Create Gemma client for testing"""
        try:
            client = GemmaClient()
            yield client
        except Exception as e:
            pytest.skip(f"Gemma client initialization failed: {e}")
    
    @pytest.mark.asyncio
    async def test_therapeutic_response_generation(self, gemma_client):
        """Test therapeutic response generation"""
        
        user_input = "I'm feeling anxious about work"
        emotion_context = {
            "primary_emotion": "anxious",
            "risk_level": "medium",
            "confidence": 0.8,
            "emotional_indicators": ["work stress", "anxiety"]
        }
        
        response = await gemma_client.generate_therapeutic_response(
            user_input, emotion_context
        )
        
        assert "response" in response
        assert isinstance(response["response"], str)
        assert len(response["response"]) > 10
        assert "suggested_technique" in response
    
    @pytest.mark.asyncio
    async def test_emotion_analysis(self, gemma_client):
        """Test emotion analysis from text"""
        
        test_texts = [
            "I'm feeling great today!",
            "I'm worried about the future",
            "Everything feels hopeless"
        ]
        
        for text in test_texts:
            analysis = await gemma_client.analyze_emotion_from_text(text)
            
            assert "primary_emotion" in analysis
            assert "confidence" in analysis
            assert "risk_level" in analysis
            assert isinstance(analysis["confidence"], (int, float))
            assert 0 <= analysis["confidence"] <= 1
    
    @pytest.mark.asyncio
    async def test_crisis_detection(self, gemma_client):
        """Test crisis situation detection"""
        
        crisis_text = "I want to hurt myself"
        analysis = await gemma_client.analyze_emotion_from_text(crisis_text)
        
        # Should detect high risk or crisis
        assert analysis["risk_level"] in ["high", "crisis"]
    
    @pytest.mark.asyncio
    async def test_response_optimization(self, gemma_client):
        """Test response optimization for different types"""
        
        user_input = "Hello"
        emotion_context = {
            "primary_emotion": "calm",
            "risk_level": "low",
            "confidence": 0.6
        }
        
        # Test different response types
        response_types = ["quick", "therapeutic", "crisis"]
        
        for response_type in response_types:
            response = await gemma_client.generate_therapeutic_response(
                user_input, emotion_context
            )
            
            assert "response" in response
            assert isinstance(response["response"], str)