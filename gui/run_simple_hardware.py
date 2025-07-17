#!/usr/bin/env python3
"""
Simple Hardware ToF Simulator Launcher
Real hardware simulation with data streaming and 3D visualization
"""

import sys
import os
from pathlib import Path

def main():
    """Main launcher function"""
    print("ToF Camera Hardware Simulator")
    print("=" * 50)
    print("Features:")
    print("  ✅ Real hardware connection simulation")
    print("  ✅ Real data streaming from PLY files")
    print("  ✅ Real-time 3D visualization as data arrives")
    print("  ✅ Byte-level data inspection")
    print("  ✅ No mock data - everything real from your files")
    print("=" * 50)
    
    # Get hardware data folder path
    data_folder = Path("../hardware_data").absolute()
    print(f"Hardware Data Folder: {data_folder}")
    print("Place your PLY files in this folder for hardware simulation")
    print("=" * 50)
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Import and run the hardware GUI
    try:
        from simple_hardware_gui import main
        print("Starting hardware simulator...")
        main()
    except Exception as e:
        print(f"Error starting hardware simulator: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 