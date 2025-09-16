#!/usr/bin/env python3
"""
Simple script to start both frontend and backend servers
"""

import subprocess
import time
import os
import signal
import sys
from threading import Thread

def start_backend():
    """Start the Flask backend server"""
    print("🚀 Starting Backend Server on port 5000...")
    os.chdir('/workspaces/AI_Medical_chatbot/backend')
    subprocess.run(['python', 'app.py'])

def start_frontend():
    """Start the frontend HTTP server"""
    print("🌐 Starting Frontend Server on port 8080...")
    os.chdir('/workspaces/AI_Medical_chatbot/frontend')
    subprocess.run(['python', '-m', 'http.server', '8080'])

def signal_handler(sig, frame):
    print('\n👋 Shutting down servers...')
    sys.exit(0)

if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🏥 AI Medical Chatbot - Starting Servers")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(3)
    
    print("\n📱 Frontend will be available at:")
    print("   Local: http://localhost:8080")
    print("   Codespace: Check the 'Ports' tab for the public URL")
    print("\n🔧 Backend API available at:")
    print("   Local: http://localhost:5000") 
    print("   Codespace: Check the 'Ports' tab for port 5000")
    print("\n💡 Make sure both ports 5000 and 8080 are set to 'Public' in the Ports tab")
    print("\nPress Ctrl+C to stop both servers\n")
    
    # Start frontend (this will block)
    start_frontend()