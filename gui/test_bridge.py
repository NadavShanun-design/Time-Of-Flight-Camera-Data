#!/usr/bin/env python3
"""
Test script for C++ Bridge integration
Demonstrates how the Python GUI connects with the C++ data pipeline
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from cpp_bridge import CppBridge, DataProcessor
from PyQt6.QtWidgets import QApplication

def test_cpp_bridge():
    """Test the C++ bridge functionality"""
    print("Testing C++ Bridge Integration")
    print("=" * 40)
    
    # Initialize bridge
    bridge = CppBridge()
    
    if not bridge.cpp_executable:
        print("❌ C++ executable not found")
        print("   Make sure to build the C++ project first:")
        print("   cd .. && mkdir build && cd build && cmake .. && cmake --build .")
        return False
    
    print(f"✅ Found C++ executable: {bridge.cpp_executable}")
    
    # Get data summary
    summary = bridge.get_data_summary()
    print(f"📊 Available ToF images: {len(summary['tof_images'])}")
    print(f"📊 Available point clouds: {len(summary['point_clouds'])}")
    
    # Generate data if needed
    if not summary['tof_images']:
        print("🔄 Generating synthetic ToF data...")
        if bridge.generate_synthetic_tof():
            print("✅ Successfully generated ToF data")
            # Refresh summary
            summary = bridge.get_data_summary()
        else:
            print("❌ Failed to generate ToF data")
            return False
    
    # Test PPM parsing
    for tof_image in summary['tof_images']:
        print(f"\n📷 ToF Image: {os.path.basename(tof_image['filepath'])}")
        print(f"   Format: {tof_image['format']}")
        print(f"   Dimensions: {tof_image['width']}x{tof_image['height']}")
        print(f"   Max value: {tof_image['max_value']}")
        
        # Test numpy conversion
        img_array = DataProcessor.ppm_to_numpy(tof_image['filepath'])
        if img_array is not None:
            print(f"   ✅ Converted to numpy array: {img_array.shape}")
        else:
            print(f"   ❌ Failed to convert to numpy")
    
    # Test PLY parsing
    for point_cloud in summary['point_clouds']:
        print(f"\n☁️  Point Cloud: {os.path.basename(point_cloud['filepath'])}")
        print(f"   Format: {point_cloud['format']}")
        print(f"   Points: {point_cloud['num_points']}")
        print(f"   Has color: {point_cloud['has_color']}")
        print(f"   Format type: {point_cloud['format_type']}")
        
        # Test numpy conversion
        points_array = DataProcessor.ply_to_numpy(point_cloud['filepath'], max_points=1000)
        if points_array is not None:
            print(f"   ✅ Converted to numpy array: {points_array.shape}")
        else:
            print(f"   ❌ Failed to convert to numpy")
    
    print("\n🎉 C++ Bridge test completed successfully!")
    return True

def test_data_streaming():
    """Test the data streaming simulation"""
    print("\nTesting Data Streaming")
    print("=" * 30)
    
    # Create QApplication for Qt functionality
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    from main import DataStreamThread
    import time
    
    # Create a simple test
    thread = DataStreamThread()
    thread.packet_size = 64  # Smaller packets for testing
    thread.delay_ms = 500    # Slower for testing
    
    packet_count = 0
    def on_data_received(data, description):
        nonlocal packet_count
        packet_count += 1
        print(f"📦 {description}")
        print(f"   First 16 bytes: {' '.join(f'{b:02x}' for b in data[:16])}")
        if packet_count >= 3:  # Stop after 3 packets
            thread.stop()
    
    thread.data_received.connect(on_data_received)
    thread.start()
    
    # Wait for completion
    while thread.running:
        time.sleep(0.1)
    
    print("✅ Data streaming test completed!")

if __name__ == "__main__":
    print("ToF Simulator - C++ Bridge Test")
    print("=" * 50)
    
    # Test C++ bridge
    if test_cpp_bridge():
        # Test data streaming
        test_data_streaming()
        
        print("\n🚀 All tests passed! The GUI is ready to use.")
        print("\nTo run the GUI:")
        print("   python run_gui.py")
    else:
        print("\n❌ Bridge test failed. Please check the C++ build.")
        sys.exit(1) 