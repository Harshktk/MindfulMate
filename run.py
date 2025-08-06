#!/usr/bin/env python3
import uvicorn
import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """Run the MindfulMate API server with mobile access"""
    
    # IMPORTANT: Use 0.0.0.0 to allow external connections
    host = "0.0.0.0"  # Changed from localhost to allow mobile access
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print("🧠 Starting MindfulMate - AI Mental Health Companion")
    print(f"📡 Server: http://0.0.0.0:{port}")
    print(f"📱 Mobile: http://YOUR_COMPUTER_IP:{port}/mobile")
    print(f"📚 API Docs: http://YOUR_COMPUTER_IP:{port}/docs")
    print("=" * 50)
    print("🔧 MOBILE SETUP INSTRUCTIONS:")
    print("1. Find your computer's IP address:")
    print("   Windows: ipconfig | findstr IPv4")
    print("   Mac/Linux: ifconfig | grep inet")
    print("2. On your phone, visit: http://YOUR_IP:8000/mobile")
    print("3. Make sure both devices are on the same WiFi network")
    print("=" * 50)
    
    uvicorn.run(
        "src.api.main:app",
        host=host,        # 0.0.0.0 allows external connections
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()
