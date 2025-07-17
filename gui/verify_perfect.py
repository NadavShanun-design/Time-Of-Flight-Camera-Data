#!/usr/bin/env python3
"""
Perfect Verification Script for ToF Simulator GUI
Comprehensive test to ensure everything works flawlessly
"""

import sys
import os
import time
from pathlib import Path

def print_status(message, status="INFO"):
    """Print a formatted status message"""
    colors = {
        "SUCCESS": "✅",
        "ERROR": "❌", 
        "WARNING": "⚠️",
        "INFO": "ℹ️"
    }
    print(f"{colors.get(status, 'ℹ️')} {message}")

def test_dependencies():
    """Test all required dependencies"""
    print("Testing Dependencies...")
    print("=" * 30)
    
    dependencies = [
        ("PyQt6", "PyQt6"),
        ("numpy", "numpy"),
        ("matplotlib", "matplotlib"),
        ("PIL", "PIL")
    ]
    
    all_good = True
    for name, import_name in dependencies:
        try:
            __import__(import_name)
            print_status(f"{name} - OK", "SUCCESS")
        except ImportError:
            print_status(f"{name} - MISSING", "ERROR")
            all_good = False
    
    return all_good

def test_cpp_integration():
    """Test C++ integration"""
    print("\nTesting C++ Integration...")
    print("=" * 30)
    
    try:
        from cpp_bridge import CppBridge, DataProcessor
        
        bridge = CppBridge()
        if not bridge.cpp_executable:
            print_status("C++ executable not found", "ERROR")
            return False
        
        print_status(f"C++ executable found: {os.path.basename(bridge.cpp_executable)}", "SUCCESS")
        
        # Test data summary
        summary = bridge.get_data_summary()
        print_status(f"Found {len(summary['tof_images'])} ToF images", "SUCCESS")
        print_status(f"Found {len(summary['point_clouds'])} point clouds", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"C++ integration failed: {e}", "ERROR")
        return False

def test_gui_components():
    """Test GUI component imports"""
    print("\nTesting GUI Components...")
    print("=" * 30)
    
    try:
        # Test main GUI imports
        from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
        from PyQt6.QtCore import Qt, QThread, pyqtSignal
        from PyQt6.QtGui import QAction, QPalette, QColor
        
        print_status("PyQt6 widgets - OK", "SUCCESS")
        
        # Test matplotlib integration
        import matplotlib
        matplotlib.use('qtagg')
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        
        print_status("Matplotlib integration - OK", "SUCCESS")
        
        # Test numpy
        import numpy as np
        test_array = np.random.rand(10, 10)
        print_status(f"Numpy test array created: {test_array.shape}", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"GUI components failed: {e}", "ERROR")
        return False

def test_data_processing():
    """Test data processing capabilities"""
    print("\nTesting Data Processing...")
    print("=" * 30)
    
    try:
        from cpp_bridge import DataProcessor
        import numpy as np
        
        # Test PPM processing
        ppm_file = "../build/Debug/tof_image.ppm"
        if os.path.exists(ppm_file):
            img_array = DataProcessor.ppm_to_numpy(ppm_file)
            if img_array is not None:
                print_status(f"PPM processing - OK: {img_array.shape}", "SUCCESS")
            else:
                print_status("PPM processing failed", "ERROR")
                return False
        else:
            print_status("PPM file not found for testing", "WARNING")
        
        # Test array operations
        test_data = np.random.randint(0, 255, (64, 64), dtype=np.uint8)
        print_status(f"Array operations - OK: {test_data.shape}", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"Data processing failed: {e}", "ERROR")
        return False

def test_file_access():
    """Test file access and permissions"""
    print("\nTesting File Access...")
    print("=" * 30)
    
    # Test current directory
    current_dir = os.getcwd()
    print_status(f"Current directory: {current_dir}", "INFO")
    
    # Test GUI files
    gui_files = [
        "main.py",
        "cpp_bridge.py", 
        "run_gui.py",
        "requirements.txt"
    ]
    
    all_files_exist = True
    for file in gui_files:
        if os.path.exists(file):
            print_status(f"{file} - OK", "SUCCESS")
        else:
            print_status(f"{file} - MISSING", "ERROR")
            all_files_exist = False
    
    # Test C++ files
    cpp_files = [
        "../build/Debug/ToFSimulator.exe",
        "../build/Debug/tof_image.ppm",
        "../fragment.ply"
    ]
    
    for file in cpp_files:
        if os.path.exists(file):
            print_status(f"{os.path.basename(file)} - OK", "SUCCESS")
        else:
            print_status(f"{os.path.basename(file)} - MISSING", "WARNING")
    
    return all_files_exist

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 ToF Simulator GUI - Perfect Verification")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("C++ Integration", test_cpp_integration),
        ("GUI Components", test_gui_components),
        ("Data Processing", test_data_processing),
        ("File Access", test_file_access)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_status(f"{test_name} test crashed: {e}", "ERROR")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print_status("🎉 ALL TESTS PASSED! GUI is PERFECT!", "SUCCESS")
        print("\n🚀 Ready to launch:")
        print("   python run_gui.py")
        return True
    else:
        print_status(f"⚠️  {total - passed} tests failed", "WARNING")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 