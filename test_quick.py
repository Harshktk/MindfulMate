#!/usr/bin/env python3
"""
Quick test to verify MindfulMate setup is working
Run this first before running the full test suite
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def test_imports():
    """Test that all modules can be imported"""
    print("📦 Testing imports...")
    
    try:
        from src.core.gemma_client import GemmaClient
        print("✅ GemmaClient import successful")
        
        from src.core.emotion_analyzer import VoiceEmotionAnalyzer, TextEmotionAnalyzer, MultimodalEmotionFusion
        print("✅ Emotion analyzers import successful")
        
        from src.core.conversation_manager import ConversationManager
        print("✅ ConversationManager import successful")
        
        from src.utils.config import load_config
        from src.utils.logger import setup_logging
        print("✅ Utilities import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🔌 Testing Ollama connection...")
    
    try:
        from src.core.gemma_client import GemmaClient
        
        # This will test the connection
        client = GemmaClient()
        print("✅ Ollama connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("Make sure Ollama is running: ollama serve")
        return False

def test_basic_functionality():
    """Test basic emotion analysis"""
    print("\n🧠 Testing basic emotion analysis...")
    
    try:
        from src.core.emotion_analyzer import VoiceEmotionAnalyzer
        
        voice_analyzer = VoiceEmotionAnalyzer()
        
        # Test voice analysis
        test_features = {
            "pitch_mean": 180,
            "pitch_variance": 80,
            "speech_rate": 190,
            "energy": 0.7,
            "avg_pause_duration": 0.3
        }
        
        analysis = voice_analyzer.analyze_voice_features(test_features)
        print(f"✅ Voice analysis: {analysis.primary_emotion.value} ({analysis.confidence:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

async def test_gemma_response():
    """Test Gemma response generation"""
    print("\n🤖 Testing Gemma response generation...")
    
    try:
        from src.core.gemma_client import GemmaClient
        
        client = GemmaClient()
        
        # Test simple response
        response = await client.generate_therapeutic_response(
            "I'm feeling anxious",
            {"primary_emotion": "anxious", "risk_level": "medium", "confidence": 0.8}
        )
        
        print(f"✅ Gemma response: {response.get('response', 'No response')[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Gemma response test failed: {e}")
        return False

async def main():
    """Run all quick tests"""
    
    print("🚀 MindfulMate Quick Test Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports, False),
        ("Ollama Connection", test_ollama_connection, False), 
        ("Basic Functionality", test_basic_functionality, False),
        ("Gemma Response", test_gemma_response, True)
    ]
    
    results = []
    
    for test_name, test_func, is_async in tests:
        try:
            if is_async:
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All quick tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run the API: python run.py")
        print("2. Test the API: http://localhost:8000/docs")
        print("3. Run full tests: python tests/test_integration/test_end_to_end.py")
    else:
        print("❌ Some tests failed. Fix the issues above before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
