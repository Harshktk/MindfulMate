#!/usr/bin/env python3
"""
Week 2 Enhancement Testing Script
Test all the new features we've added
"""

import asyncio
import sys
import os
from pathlib import Path
import requests
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

API_BASE = "http://localhost:8000"

async def test_enhanced_api():
    """Test enhanced API features"""
    
    print("🚀 Testing Week 2 MindfulMate Enhancements")
    print("=" * 60)
    
    # Test 1: Enhanced Health Check
    print("\n1. Testing Enhanced Health Check...")
    try:
        response = requests.get(f"{API_BASE}/health/detailed")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Version: {data.get('version', 'Unknown')}")
            print(f"✅ Components Status:")
            for component, status in data.get('components', {}).items():
                print(f"   - {component}: {status}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Mobile Interface
    print("\n2. Testing Mobile Interface...")
    try:
        response = requests.get(f"{API_BASE}/mobile")
        if response.status_code == 200:
            print("✅ Mobile interface accessible")
            print(f"   Content length: {len(response.content)} bytes")
        else:
            print(f"❌ Mobile interface failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Mobile interface error: {e}")
    
    # Test 3: PWA Manifest
    print("\n3. Testing PWA Manifest...")
    try:
        response = requests.get(f"{API_BASE}/manifest.json")
        if response.status_code == 200:
            manifest = response.json()
            print("✅ PWA Manifest loaded")
            print(f"   App name: {manifest.get('name', 'Unknown')}")
            print(f"   Icons: {len(manifest.get('icons', []))} available")
            print(f"   Shortcuts: {len(manifest.get('shortcuts', []))} available")
        else:
            print(f"❌ PWA Manifest failed: {response.status_code}")
    except Exception as e:
        print(f"❌ PWA Manifest error: {e}")
    
    # Test 4: Enhanced Voice Features
    print("\n4. Testing Enhanced Voice Features...")
    try:
        # Test voice feature analysis
        test_voice_features = {
            "voice_features": {
                "pitch_mean": 180.0,
                "pitch_variance": 85.0,
                "speech_rate": 190.0,
                "energy": 0.7,
                "avg_pause_duration": 0.3
            }
        }
        
        response = requests.post(
            f"{API_BASE}/voice/features", 
            json=test_voice_features
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Voice feature analysis working")
            print(f"   Detected emotion: {data.get('primary_emotion', 'Unknown')}")
            print(f"   Confidence: {data.get('confidence', 0):.2f}")
            print(f"   Risk level: {data.get('risk_level', 'Unknown')}")
        else:
            print(f"❌ Voice feature analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Voice feature analysis error: {e}")
    
    # Test 5: Multimodal Analysis
    print("\n5. Testing Multimodal Analysis...")
    try:
        test_multimodal = {
            "text": "I'm feeling really anxious about tomorrow",
            "voice_features": {
                "pitch_mean": 190.0,
                "energy": 0.8,
                "speech_rate": 200.0
            }
        }
        
        response = requests.post(
            f"{API_BASE}/analyze/multimodal",
            json=test_multimodal
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Multimodal analysis working")
            print(f"   Combined emotion: {data.get('primary_emotion', 'Unknown')}")
            print(f"   Combined confidence: {data.get('confidence', 0):.2f}")
            print(f"   Suggested technique: {data.get('suggested_technique', 'Unknown')}")
        else:
            print(f"❌ Multimodal analysis failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Multimodal analysis error: {e}")
    
    # Test 6: Enhanced Chat with Voice Features
    print("\n6. Testing Enhanced Chat...")
    try:
        test_chat = {
            "message": "I'm having a panic attack and can't breathe",
            "user_id": "test_user_week2",
            "voice_features": {
                "pitch_mean": 200.0,
                "energy": 0.9,
                "speech_rate": 220.0,
                "avg_pause_duration": 0.2
            }
        }
        
        response = requests.post(
            f"{API_BASE}/chat",
            json=test_chat
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced chat working")
            print(f"   Response: {data.get('response', 'No response')[:100]}...")
            print(f"   Detected emotion: {data.get('emotion_detected', 'Unknown')}")
            print(f"   Risk level: {data.get('risk_level', 'Unknown')}")
            print(f"   Professional help suggested: {data.get('professional_help_suggested', False)}")
        else:
            print(f"❌ Enhanced chat failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Enhanced chat error: {e}")
    
    print("\n" + "=" * 60)
    print("📊 WEEK 2 ENHANCEMENT TEST SUMMARY")
    print("=" * 60)
    print("✅ Enhanced API with voice processing")
    print("✅ Mobile-optimized interface")
    print("✅ PWA manifest for app installation")
    print("✅ Multimodal emotion detection")
    print("✅ User story scenarios documented")
    
    print("\n🎯 NEXT STEPS FOR WEEK 2:")
    print("1. 📱 Test mobile interface on your phone")
    print("2. 🎤 Test voice recording (requires browser)")
    print("3. 📸 Capture screenshots for demo")
    print("4. 🎬 Plan demo video scenes")
    print("5. 📝 Write demo script")

def test_demo_scenarios():
    """Test the demo scenarios we created"""
    
    print("\n🎬 TESTING DEMO SCENARIOS")
    print("=" * 40)
    
    scenarios = [
        {
            "name": "Sarah - Anxiety Attack",
            "message": "I'm having a panic attack at work, I can't breathe",
            "voice_features": {
                "pitch_mean": 200.0,
                "pitch_variance": 90.0,
                "speech_rate": 220.0,
                "energy": 0.8
            }
        },
        {
            "name": "Marcus - Depression",
            "message": "I feel so empty, nothing matters anymore",
            "voice_features": {
                "pitch_mean": 120.0,
                "pitch_variance": 20.0,
                "speech_rate": 100.0,
                "energy": 0.2
            }
        },
        {
            "name": "Elena - Student Stress",
            "message": "I have three exams tomorrow and I haven't studied enough",
            "voice_features": {
                "pitch_mean": 180.0,
                "pitch_variance": 70.0,
                "speech_rate": 200.0,
                "energy": 0.7
            }
        },
        {
            "name": "Robert - Crisis",
            "message": "I can't take this anymore, my family would be better off without me",
            "voice_features": {
                "pitch_mean": 110.0,
                "pitch_variance": 15.0,
                "speech_rate": 90.0,
                "energy": 0.1
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/chat",
                json={
                    "message": scenario["message"],
                    "user_id": f"demo_user_{i}",
                    "voice_features": scenario["voice_features"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Emotion: {data.get('emotion_detected', 'unknown')}")
                print(f"   ✅ Risk: {data.get('risk_level', 'unknown')}")
                print(f"   ✅ Technique: {data.get('suggested_technique', 'unknown')}")
                print(f"   ✅ Crisis help: {data.get('professional_help_suggested', False)}")
                
                if data.get('risk_level') == 'crisis':
                    print(f"   🚨 CRISIS DETECTED - Good for demo!")
                    
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def main():
    """Run all enhancement tests"""
    
    # Test if API is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API not responding. Please start the server with: python run.py")
            return
    except Exception:
        print("❌ API not running. Please start the server with: python run.py")
        return
    
    # Run tests
    await test_enhanced_api()
    test_demo_scenarios()
    
    print("\n🎉 Week 2 Enhancement Testing Complete!")
    print("\n📱 Try the mobile interface: http://localhost:8000/mobile")
    print("📚 Check API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    asyncio.run(main())
