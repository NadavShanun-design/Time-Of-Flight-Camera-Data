#!/usr/bin/env python3
"""
ToF Simulator GUI Launcher
Simple launcher script to run the high-tech GUI
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['PyQt6', 'numpy', 'matplotlib']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("ToF Simulator - High-Tech GUI Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Import and run the main GUI
    try:
        from main import main
        print("Starting GUI...")
        main()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 