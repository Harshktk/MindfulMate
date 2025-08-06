#!/usr/bin/env python3
"""
Test Ollama connection and diagnose common issues
Run this to verify your Ollama setup is working
"""

import requests
import json
import sys
import time

def test_ollama_http():
    """Test Ollama HTTP API directly"""
    print("🔌 Testing Ollama HTTP API...")
    
    try:
        # Test if Ollama is responding
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        
        if response.status_code == 200:
            print("✅ Ollama HTTP API is responding")
            
            data = response.json()
            models = data.get('models', [])
            
            if models:
                print(f"📋 Available models:")
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0)
                    print(f"  - {name} ({size // (1024*1024*1024):.1f}GB)")
                
                # Look for Gemma models
                gemma_models = [m for m in models if 'gemma' in m.get('name', '').lower()]
                if gemma_models:
                    print(f"✅ Found Gemma models: {[m['name'] for m in gemma_models]}")
                    return gemma_models[0]['name']
                else:
                    print("❌ No Gemma models found")
                    return None
            else:
                print("❌ No models installed")
                return None
                
        else:
            print(f"❌ Ollama HTTP API error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama on localhost:11434")
        print("Ollama might not be running or using a different port")
        return None
    except requests.exceptions.Timeout:
        print("❌ Ollama connection timeout")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_ollama_client():
    """Test using ollama Python client"""
    print("\n🐍 Testing Ollama Python client...")
    
    try:
        import ollama
        
        # Test connection
        client = ollama.Client()
        models = client.list()
        print("✅ Ollama Python client connected")
        
        return True
        
    except ImportError:
        print("❌ Ollama package not installed")
        print("Run: pip install ollama")
        return False
    except Exception as e:
        print(f"❌ Ollama client error: {e}")
        return False

def test_simple_generation(model_name):
    """Test simple text generation"""
    print(f"\n🧠 Testing text generation with {model_name}...")
    
    try:
        import ollama
        
        client = ollama.Client()
        
        print("Sending test prompt...")
        start_time = time.time()
        
        response = client.generate(
            model=model_name,
            prompt="Say exactly: 'Hello from Gemma!'",
            options={"temperature": 0.1}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"✅ Response ({response_time:.1f}s): {response['response']}")
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

def diagnose_common_issues():
    """Diagnose and suggest fixes for common issues"""
    print("\n🔍 Diagnosing common issues...")
    
    # Check if port is in use
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 11434))
        sock.close()
        
        if result == 0:
            print("✅ Port 11434 is open and responding")
        else:
            print("❌ Port 11434 is not responding")
            
    except Exception as e:
        print(f"❌ Port check failed: {e}")
    
    # Check Ollama installation
    import subprocess
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Ollama CLI installed: {result.stdout.strip()}")
        else:
            print("❌ Ollama CLI not found in PATH")
    except subprocess.TimeoutExpired:
        print("❌ Ollama CLI command timeout")
    except FileNotFoundError:
        print("❌ Ollama CLI not installed or not in PATH")
    except Exception as e:
        print(f"❌ Ollama CLI check failed: {e}")

def show_fix_suggestions():
    """Show common fixes"""
    print("\n🔧 COMMON FIXES:")
    print("""
1. OLLAMA ALREADY RUNNING ERROR:
   - This is actually GOOD! It means Ollama is running
   - Don't run 'ollama serve' again
   - Just test your connection with this script

2. NO MODELS FOUND:
   - Install Gemma: ollama pull gemma:3n
   - Or try: ollama pull gemma:7b
   - List models: ollama list

3. CONNECTION REFUSED:
   - Check if Ollama is running: ollama ps
   - Restart Ollama: kill ollama processes, then 'ollama serve'
   - Check firewall settings

4. PYTHON CLIENT ISSUES:
   - Install client: pip install ollama
   - Update client: pip install --upgrade ollama

5. SLOW RESPONSES:
   - Normal for first run (model loading)
   - Subsequent calls should be faster
   - Check system RAM (Gemma needs 4-8GB)
""")

def main():
    """Run comprehensive Ollama diagnostics"""
    print("🚀 OLLAMA CONNECTION DIAGNOSTICS")
    print("=" * 50)
    
    # Test 1: HTTP API
    model_name = test_ollama_http()
    
    # Test 2: Python client
    client_ok = test_ollama_client()
    
    # Test 3: Text generation (if we have a model)
    if model_name and client_ok:
        generation_ok = test_simple_generation(model_name)
    else:
        generation_ok = False
    
    # Test 4: Diagnose issues
    diagnose_common_issues()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if model_name and client_ok and generation_ok:
        print("🎉 ALL TESTS PASSED!")
        print(f"✅ Ollama is working with model: {model_name}")
        print("\n🚀 You're ready to run MindfulMate!")
        print("Next step: python quick_test.py")
    else:
        print("❌ SOME TESTS FAILED")
        if not model_name:
            print("❌ No Gemma models found - run: ollama pull gemma:3n")
        if not client_ok:
            print("❌ Python client issue - run: pip install ollama")
        if not generation_ok:
            print("❌ Text generation failed - check model installation")
        
        show_fix_suggestions()

if __name__ == "__main__":
    main()