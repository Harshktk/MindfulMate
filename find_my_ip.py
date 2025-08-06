import socket
import subprocess
import platform

def get_local_ip():
    """Get the local IP address of this computer"""
    try:
        # Create a socket connection to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None

def get_ip_from_system():
    """Get IP using system commands"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if 'IPv4 Address' in line and '192.168.' in line:
                    return line.split(':')[-1].strip()
        else:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            return result.stdout.strip().split()[0]
    except Exception:
        return None

def main():
    """Find and display IP address for mobile connection"""
    print("🔍 Finding your computer's IP address for mobile connection...")
    print("=" * 60)
    
    # Method 1: Socket connection
    ip1 = get_local_ip()
    if ip1:
        print(f"✅ Method 1 - Socket: {ip1}")
    
    # Method 2: System command
    ip2 = get_ip_from_system()
    if ip2:
        print(f"✅ Method 2 - System: {ip2}")
    
    # Choose the best IP
    best_ip = ip1 or ip2
    
    if best_ip:
        print(f"\n🎯 USE THIS IP ADDRESS: {best_ip}")
        print(f"📱 Mobile URL: http://{best_ip}:8000/mobile")
        print(f"🖥️  Desktop URL: http://{best_ip}:8000")
        print(f"📚 API Docs: http://{best_ip}:8000/docs")
        print("\n⚠️  IMPORTANT:")
        print("1. Make sure both your computer and phone are on the same WiFi network")
        print("2. Start your server with: python run.py")
        print("3. Then visit the mobile URL on your phone")
    else:
        print("❌ Could not determine IP address automatically")
        print("\n🔧 Manual steps:")
        print("Windows: Open Command Prompt, type 'ipconfig'")
        print("Mac: Open Terminal, type 'ifconfig | grep inet'")
        print("Linux: Open Terminal, type 'hostname -I'")
        print("Look for an IP starting with 192.168.x.x")

if __name__ == "__main__":
    main()
