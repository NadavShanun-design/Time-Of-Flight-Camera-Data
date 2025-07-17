#!/usr/bin/env python3
"""
Hardware Simulator for ToF Camera System
Simulates real hardware data streaming from PLY files
"""

import os
import sys
import time
import struct
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional

class ToFCameraSimulator:
    """Simulates a real ToF camera hardware system"""
    
    def __init__(self, data_folder="hardware_data"):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        self.current_ply_file = None
        self.points = None
        self.colors = None
        self.info = None
        self.is_connected = False
        self.streaming = False
        
    def get_available_data_files(self) -> List[str]:
        """Get list of available PLY files in the hardware data folder"""
        ply_files = list(self.data_folder.glob("*.ply"))
        return [f.name for f in ply_files]
    
    def load_ply_file(self, filename: str) -> bool:
        """Load a PLY file from the hardware data folder"""
        file_path = self.data_folder / filename
        if not file_path.exists():
            print(f"Error: File {file_path} not found")
            return False
            
        try:
            with open(file_path, 'rb') as f:
                # Read header
                line = f.readline().decode().strip()
                if line != 'ply':
                    raise ValueError("Not a valid PLY file")
                
                info = {
                    'num_points': 0,
                    'num_faces': 0,
                    'has_color': False,
                    'format_type': 'unknown',
                    'properties': []
                }
                
                # Parse header
                while True:
                    line = f.readline().decode().strip()
                    if line == 'end_header':
                        break
                    
                    parts = line.split()
                    if len(parts) < 2:
                        continue
                    
                    if parts[0] == 'format':
                        info['format_type'] = parts[1]
                    elif parts[0] == 'element':
                        if parts[1] == 'vertex':
                            info['num_points'] = int(parts[2])
                        elif parts[1] == 'face':
                            info['num_faces'] = int(parts[2])
                    elif parts[0] == 'property':
                        prop_type = parts[1]
                        prop_name = parts[2] if len(parts) > 2 else ""
                        info['properties'].append((prop_type, prop_name))
                        if prop_name in ['red', 'green', 'blue']:
                            info['has_color'] = True
                
                # Read all points
                points = []
                colors = []
                
                if info['format_type'] == 'ascii':
                    for i in range(info['num_points']):
                        line = f.readline().decode().strip()
                        values = line.split()
                        x, y, z = float(values[0]), float(values[1]), float(values[2])
                        points.append([x, y, z])
                        
                        if info['has_color'] and len(values) >= 6:
                            r, g, b = int(values[3]), int(values[4]), int(values[5])
                            colors.append([r/255, g/255, b/255])
                        else:
                            colors.append([0.5, 0.5, 0.5])  # Default gray
                else:
                    # Binary format
                    for i in range(info['num_points']):
                        # Read position
                        data = f.read(12)  # 3 floats * 4 bytes
                        if len(data) == 12:
                            x, y, z = struct.unpack('fff', data)
                            points.append([x, y, z])
                            
                            # Read color if available
                            if info['has_color']:
                                color_data = f.read(3)  # 3 bytes for RGB
                                if len(color_data) == 3:
                                    r, g, b = struct.unpack('BBB', color_data)
                                    colors.append([r/255, g/255, b/255])
                                else:
                                    colors.append([0.5, 0.5, 0.5])
                            else:
                                colors.append([0.5, 0.5, 0.5])
                
                self.points = np.array(points)
                self.colors = np.array(colors)
                self.info = info
                self.current_ply_file = filename
                
                print(f"Loaded PLY file: {filename}")
                print(f"Points: {len(self.points)}")
                print(f"Has colors: {info['has_color']}")
                print(f"Format: {info['format_type']}")
                
                return True
                
        except Exception as e:
            print(f"Error loading PLY file: {e}")
            return False
    
    def connect_hardware(self) -> bool:
        """Simulate connecting to ToF camera hardware"""
        if self.current_ply_file is None:
            print("Error: No PLY file loaded")
            return False
            
        print(f"Connecting to ToF camera hardware...")
        print(f"Data source: {self.current_ply_file}")
        print(f"Total points: {len(self.points)}")
        
        # Simulate hardware connection delay
        time.sleep(1)
        
        self.is_connected = True
        print("✅ Hardware connected successfully!")
        return True
    
    def disconnect_hardware(self):
        """Simulate disconnecting from ToF camera hardware"""
        self.is_connected = False
        self.streaming = False
        print("Hardware disconnected")
    
    def start_data_stream(self, points_per_packet=100, delay_ms=50):
        """Start streaming real data from the loaded PLY file"""
        if not self.is_connected:
            print("Error: Hardware not connected")
            return False
            
        if self.points is None:
            print("Error: No data loaded")
            return False
            
        self.streaming = True
        total_points = len(self.points)
        packets_sent = 0
        
        print(f"Starting real data stream...")
        print(f"Points per packet: {points_per_packet}")
        print(f"Total packets: {total_points // points_per_packet + 1}")
        
        for i in range(0, total_points, points_per_packet):
            if not self.streaming:
                break
                
            end_idx = min(i + points_per_packet, total_points)
            packet_points = self.points[i:end_idx]
            packet_colors = self.colors[i:end_idx] if self.colors is not None else None
            
            packets_sent += 1
            
            # Convert to bytes (real data)
            packet_data = self.points_to_bytes(packet_points, packet_colors)
            
            # Yield real packet data
            yield {
                'packet_id': packets_sent,
                'points': packet_points,
                'colors': packet_colors,
                'raw_bytes': packet_data,
                'progress': (end_idx / total_points) * 100,
                'description': f"Hardware Packet #{packets_sent}: {len(packet_points)} points"
            }
            
            # Simulate real hardware timing
            time.sleep(delay_ms / 1000.0)
        
        print(f"Data stream complete: {packets_sent} packets sent")
    
    def points_to_bytes(self, points, colors=None):
        """Convert points to real byte data as if from hardware"""
        # Format: 3 floats (x,y,z) + 3 bytes (r,g,b) per point
        data = bytearray()
        
        for i, point in enumerate(points):
            # Position data (3 floats, 12 bytes)
            data.extend(struct.pack('<fff', point[0], point[1], point[2]))
            
            # Color data (3 bytes)
            if colors is not None and i < len(colors):
                r = int(colors[i][0] * 255)
                g = int(colors[i][1] * 255)
                b = int(colors[i][2] * 255)
                data.extend(struct.pack('<BBB', r, g, b))
            else:
                data.extend(struct.pack('<BBB', 128, 128, 128))  # Default gray
        
        return bytes(data)
    
    def stop_data_stream(self):
        """Stop the data stream"""
        self.streaming = False
        print("Data stream stopped")

class HardwareDataManager:
    """Manages hardware data files and operations"""
    
    def __init__(self, data_folder="hardware_data"):
        self.data_folder = Path(data_folder)
        self.data_folder.mkdir(exist_ok=True)
        self.simulator = ToFCameraSimulator(data_folder)
        
    def get_data_folder_path(self) -> str:
        """Get the absolute path to the data folder"""
        return str(self.data_folder.absolute())
    
    def list_available_files(self) -> List[str]:
        """List all available PLY files"""
        return self.simulator.get_available_data_files()
    
    def load_file(self, filename: str) -> bool:
        """Load a PLY file into the simulator"""
        return self.simulator.load_ply_file(filename)
    
    def connect_hardware(self) -> bool:
        """Connect to simulated hardware"""
        return self.simulator.connect_hardware()
    
    def disconnect_hardware(self):
        """Disconnect from simulated hardware"""
        self.simulator.disconnect_hardware()
    
    def start_streaming(self, points_per_packet=100, delay_ms=50):
        """Start streaming data from hardware"""
        return self.simulator.start_data_stream(points_per_packet, delay_ms)
    
    def stop_streaming(self):
        """Stop streaming data"""
        self.simulator.stop_data_stream()
    
    def get_current_file_info(self):
        """Get information about the currently loaded file"""
        if self.simulator.current_ply_file:
            return {
                'filename': self.simulator.current_ply_file,
                'points': len(self.simulator.points) if self.simulator.points is not None else 0,
                'has_colors': self.simulator.info['has_color'] if self.simulator.info else False,
                'format': self.simulator.info['format_type'] if self.simulator.info else 'unknown'
            }
        return None

# Example usage
if __name__ == "__main__":
    # Create hardware data manager
    manager = HardwareDataManager()
    
    print("ToF Camera Hardware Simulator")
    print("=" * 40)
    print(f"Data folder: {manager.get_data_folder_path()}")
    
    # List available files
    files = manager.list_available_files()
    if files:
        print(f"Available files: {files}")
        
        # Load first file
        if manager.load_file(files[0]):
            print("File loaded successfully!")
            
            # Connect hardware
            if manager.connect_hardware():
                print("Hardware connected!")
                
                # Start streaming
                for packet in manager.start_streaming(points_per_packet=50, delay_ms=100):
                    print(f"Packet {packet['packet_id']}: {len(packet['points'])} points, {len(packet['raw_bytes'])} bytes")
                    if packet['progress'] >= 100:
                        break
    else:
        print("No PLY files found in data folder")
        print("Please place PLY files in:", manager.get_data_folder_path()) 