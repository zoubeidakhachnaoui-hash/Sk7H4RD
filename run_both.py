
#!/usr/bin/env python3
"""
Script to run both api.py and main.py simultaneously
"""
import subprocess
import sys
import time

def run_service(script_name):
    """Run a Python script"""
    return subprocess.Popen([sys.executable, script_name])

if __name__ == '__main__':
    print("🚀 Starting both services...")
    
    # Start api.py
    print("Starting Bot API on port 8080...")
    api_process = run_service('api.py')
    time.sleep(2)  # Wait for API to initialize
    
    # Start main.py
    print("Starting Website on port 5000...")
    main_process = run_service('main.py')
    
    print("✅ Both services are running!")
    print("- Bot API: http://0.0.0.0:8080")
    print("- Website: http://0.0.0.0:5000")
    print("\nPress Ctrl+C to stop both services\n")
    
    try:
        # Keep script running
        api_process.wait()
        main_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        api_process.terminate()
        main_process.terminate()
        api_process.wait()
        main_process.wait()
        print("✅ Services stopped successfully")
