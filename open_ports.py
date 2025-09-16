#!/usr/bin/env python3
"""
Script to help expose ports in GitHub Codespace
"""
import webbrowser
import time

print("🚀 AI Medical Chatbot - Opening Ports")
print("=====================================")
print()
print("🏥 Backend API: http://localhost:5000")
print("🌐 Frontend UI: http://localhost:8080") 
print()
print("📋 In GitHub Codespace:")
print("1. Check the 'Ports' tab in VS Code")
print("2. Look for ports 5000 and 8080")
print("3. Click the globe icon for public URLs")
print()
print("If ports don't appear automatically:")
print("• Press Ctrl+Shift+P")
print("• Type 'Ports: Focus on Ports View'")
print("• Click '+' to add ports 5000 and 8080")
print()

# Try to open the URLs (this might help trigger port detection)
try:
    print("🔍 Attempting to trigger port detection...")
    webbrowser.open('http://localhost:5000')
    time.sleep(1)
    webbrowser.open('http://localhost:8080')
    print("✅ Port detection triggered")
except:
    print("⚠️  Manual port setup required")

print()
print("🎯 Ready for testing!")