# ============================================================================
# FILE: src/utils/config.py  
# Configuration management
# ============================================================================

import yaml
import os
from typing import Dict, Any

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load application configuration"""
    
    # Default configuration
    default_config = {
        "ollama": {
            "host": "http://localhost:11434",
            "model": "gemma3n:e4b",
            "timeout": 120
        },
        "api": {
            "host": "localhost",
            "port": 8000,
            "debug": True
        },
        "conversation": {
            "max_history": 20,
            "timeout": 3600
        },
        "emotion_detection": {
            "voice_weight": 0.4,
            "text_weight": 0.6,
            "confidence_threshold": 0.6
        }
    }
    
    # Load from file if exists
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(file_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
    
    # Override with environment variables
    if os.getenv("OLLAMA_HOST"):
        default_config["ollama"]["host"] = os.getenv("OLLAMA_HOST")
    if os.getenv("GEMMA_MODEL"):
        default_config["ollama"]["model"] = os.getenv("GEMMA_MODEL")
    if os.getenv("API_PORT"):
        default_config["api"]["port"] = int(os.getenv("API_PORT"))
    
    return default_config