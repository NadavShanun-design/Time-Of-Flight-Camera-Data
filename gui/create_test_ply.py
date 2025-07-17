#!/usr/bin/env python3
"""
Create Test PLY File
Generate a real PLY file with 3D point cloud data for testing the GUI
"""

import numpy as np
import struct

def create_test_ply(filename="test_point_cloud.ply", num_points=1000):
    """Create a test PLY file with 3D point cloud data"""
    
    # Generate realistic 3D points (sphere with some noise)
    phi = np.random.uniform(0, 2*np.pi, num_points)
    theta = np.random.uniform(0, np.pi, num_points)
    radius = np.random.uniform(0.8, 1.2, num_points)  # Add some variation
    
    x = radius * np.sin(theta) * np.cos(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(theta)
    
    # Add some color variation based on position
    r = np.clip((x + 1) * 127, 0, 255).astype(np.uint8)
    g = np.clip((y + 1) * 127, 0, 255).astype(np.uint8)
    b = np.clip((z + 1) * 127, 0, 255).astype(np.uint8)
    
    # Write PLY file
    with open(filename, 'wb') as f:
        # Write header
        f.write(b"ply\n")
        f.write(b"format binary_little_endian 1.0\n")
        f.write(f"element vertex {num_points}\n".encode())
        f.write(b"property float x\n")
        f.write(b"property float y\n")
        f.write(b"property float z\n")
        f.write(b"property uchar red\n")
        f.write(b"property uchar green\n")
        f.write(b"property uchar blue\n")
        f.write(b"end_header\n")
        
        # Write point data
        for i in range(num_points):
            # Write position (3 floats)
            f.write(struct.pack('<fff', x[i], y[i], z[i]))
            # Write color (3 bytes)
            f.write(struct.pack('<BBB', r[i], g[i], b[i]))
    
    print(f"Created test PLY file: {filename}")
    print(f"Points: {num_points}")
    print(f"File size: {os.path.getsize(filename)} bytes")
    
    return filename

def create_complex_ply(filename="complex_point_cloud.ply", num_points=5000):
    """Create a more complex PLY file with multiple objects"""
    
    points = []
    colors = []
    
    # Create a sphere
    sphere_points = int(num_points * 0.4)
    phi = np.random.uniform(0, 2*np.pi, sphere_points)
    theta = np.random.uniform(0, np.pi, sphere_points)
    radius = np.random.uniform(0.8, 1.2, sphere_points)
    
    x = radius * np.sin(theta) * np.cos(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(theta)
    
    for i in range(sphere_points):
        points.append([x[i], y[i], z[i]])
        colors.append([255, 100, 100])  # Red sphere
    
    # Create a cube
    cube_points = int(num_points * 0.3)
    for i in range(cube_points):
        x = np.random.uniform(-1.5, -0.5)
        y = np.random.uniform(-1.5, -0.5)
        z = np.random.uniform(-1.5, -0.5)
        points.append([x, y, z])
        colors.append([100, 255, 100])  # Green cube
    
    # Create a plane
    plane_points = int(num_points * 0.3)
    for i in range(plane_points):
        x = np.random.uniform(-2, 2)
        y = np.random.uniform(-2, 2)
        z = np.random.uniform(-2, -1.8)
        points.append([x, y, z])
        colors.append([100, 100, 255])  # Blue plane
    
    # Shuffle points
    indices = np.random.permutation(len(points))
    points = [points[i] for i in indices]
    colors = [colors[i] for i in indices]
    
    # Write PLY file
    with open(filename, 'wb') as f:
        # Write header
        f.write(b"ply\n")
        f.write(b"format binary_little_endian 1.0\n")
        f.write(f"element vertex {len(points)}\n".encode())
        f.write(b"property float x\n")
        f.write(b"property float y\n")
        f.write(b"property float z\n")
        f.write(b"property uchar red\n")
        f.write(b"property uchar green\n")
        f.write(b"property uchar blue\n")
        f.write(b"end_header\n")
        
        # Write point data
        for i in range(len(points)):
            # Write position (3 floats)
            f.write(struct.pack('<fff', points[i][0], points[i][1], points[i][2]))
            # Write color (3 bytes)
            f.write(struct.pack('<BBB', colors[i][0], colors[i][1], colors[i][2]))
    
    print(f"Created complex PLY file: {filename}")
    print(f"Points: {len(points)}")
    print(f"File size: {os.path.getsize(filename)} bytes")
    
    return filename

if __name__ == "__main__":
    import os
    
    print("Creating test PLY files for the GUI...")
    print("=" * 40)
    
    # Create simple test file
    simple_file = create_test_ply("test_simple.ply", 1000)
    
    # Create complex test file
    complex_file = create_complex_ply("test_complex.ply", 3000)
    
    print("\n" + "=" * 40)
    print("Test files created successfully!")
    print(f"Simple file: {simple_file}")
    print(f"Complex file: {complex_file}")
    print("\nYou can now:")
    print("1. Load these files in the 3D viewer")
    print("2. Stream them in the data inspector")
    print("3. See real data transfer in action!") 