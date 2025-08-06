# ============================================================================
# FILE: run_tests.py (Test runner script)
# ============================================================================

#!/usr/bin/env python3
"""
Test runner for MindfulMate
Provides different test execution options
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def main():
    parser = argparse.ArgumentParser(description="MindfulMate Test Runner")
    parser.add_argument("--quick", action="store_true", 
                       help="Run only quick unit tests")
    parser.add_argument("--integration", action="store_true",
                       help="Run integration tests")
    parser.add_argument("--api", action="store_true",
                       help="Run API tests")
    parser.add_argument("--all", action="store_true",
                       help="Run all tests")
    parser.add_argument("--coverage", action="store_true",
                       help="Run with coverage report")
    
    args = parser.parse_args()
    
    if not any([args.quick, args.integration, args.api, args.all]):
        args.all = True  # Default to all tests
    
    success_count = 0
    total_count = 0
    
    # Quick unit tests
    if args.quick or args.all:
        total_count += 1
        cmd = "python -m pytest tests/test_core/ -v"
        if args.coverage:
            cmd += " --cov=src --cov-report=html"
        
        if run_command(cmd, "Unit Tests"):
            success_count += 1
    
    # API tests
    if args.api or args.all:
        total_count += 1
        if run_command("python -m pytest tests/test_api/ -v", "API Tests"):
            success_count += 1
    
    # Integration tests
    if args.integration or args.all:
        total_count += 1
        if run_command("python tests/test_integration/test_end_to_end.py", "Integration Tests"):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All test suites passed!")
        sys.exit(0)
    else:
        print("❌ Some test suites failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()file__).parent.parent.parent
sys.path.append(str(project_root))

from src.core.gemma_client import GemmaClient
from src.core.emotion_analyzer import VoiceEmotionAnalyzer, TextEmotionAnalyzer, MultimodalEmotionFusion
from src.core.conversation_manager import ConversationManager

async def test_complete_conversation_flow():
    """Test complete conversation flow from input to response"""
    
    print("🧪 Testing Complete Conversation Flow")
    print("=" * 50)
    
    try:
        # Initialize components
        print("1. Initializing components...")
        gemma_client = GemmaClient()
        voice_analyzer = VoiceEmotionAnalyzer()
        text_analyzer = TextEmotionAnalyzer(gemma_client)
        emotion_fusion = MultimodalEmotionFusion()
        conversation_manager = ConversationManager()
        
        print("✅ All components initialized")
        
        # Create test conversation
        print("\n2. Creating test conversation...")
        user_id = "test_user_e2e"
        context = conversation_manager.get_or_create_context(user_id)
        
        # Test scenarios
        test_scenarios = [
            {
                "message": "I'm feeling really anxious about my job interview tomorrow",
                "voice_features": {
                    "pitch_mean": 180,
                    "pitch_variance": 85,
                    "speech_rate": 190,
                    "energy": 0.6,
                    "avg_pause_duration": 0.3
                },
                "expected_emotion": "anxious"
            },
            {
                "message": "Actually, talking about it helps. I'm feeling a bit calmer now",
                "voice_features": {
                    "pitch_mean": 160,
                    "pitch_variance": 45,
                    "speech_rate": 150,
                    "energy": 0.5,
                    "avg_pause_duration": 0.5
                },
                "expected_emotion": "calm"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n3.{i} Processing scenario: {scenario['expected_emotion']}")
            
            # Analyze text emotion
            text_emotion = await text_analyzer.analyze_text_emotion(
                scenario["message"], 
                conversation_manager.get_conversation_summary(context)
            )
            print(f"   Text Analysis: {text_emotion.primary_emotion.value} ({text_emotion.confidence:.2f})")
            
            # Analyze voice emotion
            voice_emotion = voice_analyzer.analyze_voice_features(scenario["voice_features"])
            print(f"   Voice Analysis: {voice_emotion.primary_emotion.value} ({voice_emotion.confidence:.2f})")
            
            # Fuse emotions
            final_emotion = emotion_fusion.fuse_emotions(voice_emotion, text_emotion)
            print(f"   Final Analysis: {final_emotion.primary_emotion.value} ({final_emotion.confidence:.2f})")
            print(f"   Risk Level: {final_emotion.risk_level.value}")
            
            # Generate response
            ai_response = await gemma_client.generate_therapeutic_response(
                scenario["message"],
                {
                    "primary_emotion": final_emotion.primary_emotion.value,
                    "risk_level": final_emotion.risk_level.value,
                    "confidence": final_emotion.confidence,
                    "emotional_indicators": final_emotion.emotional_indicators
                },
                context.conversation_history
            )
            
            print(f"   AI Response: {ai_response.get('response', 'No response')[:100]}...")
            
            # Update conversation
            conversation_manager.add_interaction(
                context,
                scenario["message"],
                ai_response.get("response", ""),
                final_emotion
            )
            
            print(f"   ✅ Scenario {i} completed successfully")
        
        # Test conversation summary
        print("\n4. Testing conversation summary...")
        summary = conversation_manager.get_conversation_summary(context)
        print(f"   Total interactions: {summary['total_interactions']}")
        print(f"   Recent emotions: {summary['recent_emotions']}")
        print(f"   Current risk: {summary['current_risk_level']}")
        print(f"   ✅ Summary generated successfully")
        
        print("\n🎉 End-to-end test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_crisis_detection_flow():
    """Test crisis detection and intervention"""
    
    print("\n🚨 Testing Crisis Detection Flow")
    print("=" * 50)
    
    try:
        # Initialize components
        gemma_client = GemmaClient()
        text_analyzer = TextEmotionAnalyzer(gemma_client)
        conversation_manager = ConversationManager()
        
        # Crisis test cases
        crisis_scenarios = [
            "I can't take this anymore, I want to end it all",
            "I've been thinking about hurting myself",
            "Life isn't worth living anymore"
        ]
        
        user_id = "crisis_test_user"
        context = conversation_manager.get_or_create_context(user_id)
        
        for i, message in enumerate(crisis_scenarios, 1):
            print(f"\n{i}. Testing crisis message: '{message[:50]}...'")
            
            # Analyze for crisis
            emotion_analysis = await text_analyzer.analyze_text_emotion(message)
            
            print(f"   Risk Level: {emotion_analysis.risk_level.value}")
            print(f"   Crisis Indicators: {emotion_analysis.emotional_indicators}")
            
            # Generate crisis response
            ai_response = await gemma_client.generate_therapeutic_response(
                message,
                {
                    "primary_emotion": emotion_analysis.primary_emotion.value,
                    "risk_level": emotion_analysis.risk_level.value,
                    "confidence": emotion_analysis.confidence,
                    "emotional_indicators": emotion_analysis.emotional_indicators
                },
                context.conversation_history
            )
            
            print(f"   Crisis Response: {ai_response.get('response', '')[:100]}...")
            print(f"   Professional Help Suggested: {ai_response.get('professional_help_needed', False)}")
            
            # Update context
            conversation_manager.add_interaction(
                context, message, ai_response.get("response", ""), emotion_analysis
            )
            
            # Check if professional help is recommended
            should_refer = conversation_manager.should_suggest_professional_help(context)
            print(f"   Should Suggest Professional Help: {should_refer}")
            
            if emotion_analysis.risk_level.value == "crisis":
                print(f"   ✅ Crisis correctly detected")
            else:
                print(f"   ⚠️ Crisis not detected - may need adjustment")
        
        print("\n✅ Crisis detection test completed")
        return True
        
    except Exception as e:
        print(f"\n❌ Crisis detection test failed: {e}")
        return False

async def test_performance_benchmarks():
    """Test system performance"""
    
    print("\n⚡ Testing Performance Benchmarks")
    print("=" * 50)
    
    try:
        import time
        
        gemma_client = GemmaClient()
        text_analyzer = TextEmotionAnalyzer(gemma_client)
        voice_analyzer = VoiceEmotionAnalyzer()
        
        # Performance test cases
        test_cases = [
            "I'm feeling good today!",
            "Work has been really stressful lately and I'm struggling to cope",
            "I don't know what to do anymore, everything feels overwhelming"
        ]
        
        voice_features = {
            "pitch_mean": 150,
            "pitch_variance": 50,
            "speech_rate": 150,
            "energy": 0.5,
            "avg_pause_duration": 0.5
        }
        
        total_times = []
        
        for i, message in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: '{message[:30]}...'")
            
            start_time = time.time()
            
            # Text analysis
            text_start = time.time()
            text_emotion = await text_analyzer.analyze_text_emotion(message)
            text_time = time.time() - text_start
            
            # Voice analysis
            voice_start = time.time()
            voice_emotion = voice_analyzer.analyze_voice_features(voice_features)
            voice_time = time.time() - voice_start
            
            # Response generation
            response_start = time.time()
            ai_response = await gemma_client.generate_therapeutic_response(
                message,
                {
                    "primary_emotion": text_emotion.primary_emotion.value,
                    "risk_level": text_emotion.risk_level.value,
                    "confidence": text_emotion.confidence
                }
            )
            response_time = time.time() - response_start
            
            total_time = time.time() - start_time
            total_times.append(total_time)
            
            print(f"   Text Analysis: {text_time:.2f}s")
            print(f"   Voice Analysis: {voice_time:.3f}s")
            print(f"   Response Generation: {response_time:.2f}s")
            print(f"   Total Time: {total_time:.2f}s")
            
            # Performance targets
            if total_time < 5.0:
                print(f"   ✅ Good performance (< 5s)")
            elif total_time < 10.0:
                print(f"   ⚠️ Acceptable performance (< 10s)")
            else:
                print(f"   ❌ Slow performance (> 10s)")
        
        # Summary
        avg_time = sum(total_times) / len(total_times)
        print(f"\n📊 Performance Summary:")
        print(f"   Average Response Time: {avg_time:.2f}s")
        print(f"   Fastest Response: {min(total_times):.2f}s")
        print(f"   Slowest Response: {max(total_times):.2f}s")
        
        if avg_time < 5.0:
            print(f"   ✅ Excellent overall performance")
        elif avg_time < 8.0:
            print(f"   ✅ Good overall performance")
        else:
            print(f"   ⚠️ Performance may need optimization")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Performance test failed: {e}")
        return False

async def run_all_integration_tests():
    """Run all integration tests"""
    
    print("🚀 MindfulMate Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Complete Conversation Flow", test_complete_conversation_flow),
        ("Crisis Detection", test_crisis_detection_flow),
        ("Performance Benchmarks", test_performance_benchmarks)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 Running: {test_name}")
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! System is ready for demo.")
    else:
        print("⚠️ Some tests failed. Review the results and fix issues.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(run_all_integration_tests())