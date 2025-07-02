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
