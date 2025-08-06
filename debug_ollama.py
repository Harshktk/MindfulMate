#!/usr/bin/env python3
"""
Debug Ollama response - Fixed version
"""

import ollama

def debug_ollama_response():
    """Debug what Ollama actually returns"""
    
    print("🔍 Debugging Ollama Response Structure")
    print("=" * 50)
    
    try:
        client = ollama.Client()
        
        # Test the list models response
        print("1. Testing models list...")
        models_response = client.list()
        
        print("Raw response type:", type(models_response))
        print("Response attributes:", dir(models_response))
        
        # Check if it has models attribute
        if hasattr(models_response, 'models'):
            models = models_response.models
            print(f"\nFound {len(models)} models:")
            
            for i, model in enumerate(models):
                print(f"  Model {i+1}: {model}")
                print(f"    Type: {type(model)}")
                
                # Check model attributes
                if hasattr(model, '__dict__'):
                    print(f"    Attributes: {model.__dict__}")
                elif hasattr(model, 'name'):
                    print(f"    Name: {model.name}")
                
                # Try to get name different ways
                model_name = None
                if hasattr(model, 'name'):
                    model_name = model.name
                elif hasattr(model, 'model'):
                    model_name = model.model
                elif isinstance(model, str):
                    model_name = model
                
                print(f"    Extracted name: {model_name}")
                
                # Test if it's a Gemma model
                if model_name and 'gemma' in str(model_name).lower():
                    print(f"    🎯 Found Gemma model: {model_name}")
                    
                    # Test this model
                    try:
                        test_response = client.generate(
                            model=str(model_name),
                            prompt="Say 'Hello'",
                            options={"temperature": 0.1}
                        )
                        print(f"    ✅ Model {model_name} works: {test_response['response']}")
                        return str(model_name)  # Return working model name
                    except Exception as e:
                        print(f"    ❌ Model {model_name} failed: {e}")
                
                print()
        else:
            print("❌ No 'models' attribute found")
            print("Available attributes:", [attr for attr in dir(models_response) if not attr.startswith('_')])
        
        print("❌ No working Gemma models found")
        return None
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    working_model = debug_ollama_response()
    if working_model:
        print(f"\n✅ Use this model name: {working_model}")
    else:
        print("\n❌ No working model found. Check Ollama installation.")
