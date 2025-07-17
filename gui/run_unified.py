#!/usr/bin/env python3
"""
Unified ToF Simulator GUI Launcher
Everything on one page: real data streaming, 3D visualization, and image viewing
"""

import sys
import os

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
    print("ToF Simulator - Unified GUI Launcher")
    print("=" * 50)
    print("Features:")
    print("  ✅ Real PLY file loading and 3D visualization")
    print("  ✅ Real data streaming with byte-level inspection")
    print("  ✅ ToF image viewing")
    print("  ✅ Everything on one unified page")
    print("  ✅ No mock data - everything real from your files")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Import and run the unified GUI
    try:
        from unified_gui import main
        print("Starting unified GUI...")
        main()
    except Exception as e:
        print(f"Error starting unified GUI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 