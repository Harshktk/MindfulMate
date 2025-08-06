@echo off
echo 🛡️  MindfulMate Firewall Fix
echo ========================

echo Checking if running as Administrator...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
    echo.
    echo Adding firewall rule for Python on port 8000...
    netsh advfirewall firewall add rule name="MindfulMate Python Server" dir=in action=allow protocol=TCP localport=8000
    echo.
    echo ✅ Firewall rule added successfully!
    echo.
    echo Now try accessing MindfulMate from your mobile device:
    echo 📱 http://YOUR_COMPUTER_IP:8000/mobile
    echo.
    pause
) else (
    echo ❌ This script must be run as Administrator
    echo.
    echo Right-click this file and select "Run as administrator"
    echo.
    pause
)
