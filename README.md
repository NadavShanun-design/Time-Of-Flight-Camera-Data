# Camera-data-transfer

A C++ project to simulate and visualize Time-of-Flight (ToF) image data, including mock SpaceWire packet handling and GUI visualization.

## Build Instructions

1. Install CMake (>=3.10) and a C++17 compiler (GCC, Clang, or MSVC).
2. Clone the repository and run:

```sh
mkdir build
cd build
cmake ..
cmake --build .
```
3. Run the executable:

```sh
./ToFSimulator
```

## Next Steps
- Add mock STAR-API interface
- Implement ToF data generator
- Build GUI for visualization

## Real Hardware Simulation: Streaming ToF Data

### Where to Put Your PLY Files

Place your `.ply` file(s) in the following folder:

```
hardware_data
```

This folder is at the root of your project. Example full path:

```
C:/Users/parad/Downloads/TOF-data/hardware_data
```

### How the Simulated Hardware Data Transfer Works

- The GUI simulates a real Time-of-Flight (ToF) camera by streaming the bytes of your `.ply` file, packet by packet, as if they were coming from hardware.
- You select your file, click **Connect to Hardware**, then click **Start Transfer from Hardware**.
- The 3D viewer and data inspector update in real time, showing exactly what’s in your file—no mock data, only real data.

### Byte Streaming Protocol (How Data is Sent)

- The system reads your `.ply` file and splits the point cloud data into packets (default: 100 points per packet).
- Each packet is sent as a sequence of bytes, just like a real ToF camera would send over USB, serial, or SpaceWire.
- Each point is encoded as 3 floats (x, y, z) and, if present, 3 bytes (r, g, b) for color.
- The GUI shows the actual bytes being transferred in the Data Inspector panel.

### How to Run the GUI and See Your Data

1. Place your `.ply` file(s) in the `hardware_data` folder.
2. From your project root, run:
   ```sh
   python gui/run_hardware.py
   # or for the simple version:
   python gui/run_simple_hardware.py
   ```
3. In the GUI:
   - Select your `.ply` file from the dropdown
   - Click **Connect to Hardware**
   - Click **Start Transfer from Hardware**
   - Watch the 3D point cloud and byte-level data stream in real time

### How This Mimics a Real ToF Camera

- The system streams your `.ply` file as if it’s coming from a real ToF camera, using the same byte structure and packetization.
- No mock data is used—everything is real, from your file.
- The GUI is designed to make it easy to swap in a real hardware interface in the future (USB, serial, etc.).

---
