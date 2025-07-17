# ToF Simulator - High-Tech GUI

A beautiful, interactive GUI for Time-of-Flight data visualization built with PyQt6 and Python.

## Features

- **Real-time ToF Image Visualization**: Load and display ToF images with color mapping
- **3D Point Cloud Viewer**: Interactive 3D visualization of point cloud data
- **Data Stream Inspector**: Real-time packet analysis and byte-level inspection
- **Modern Dark Theme**: Clean, high-tech design with smooth animations
- **Extensible Architecture**: Easy to add new data sources and visualization types

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

### Required Packages

- **PyQt6**: Modern Qt bindings for Python
- **numpy**: Numerical computing
- **matplotlib**: 2D/3D plotting and visualization
- **open3d**: Advanced 3D point cloud processing
- **pillow**: Image processing

## Usage

### Quick Start

```bash
# Run the GUI launcher
python run_gui.py
```

### Manual Launch

```bash
# Or run directly
python main.py
```

## GUI Components

### 1. ToF Image Viewer
- Load PPM, PNG, or other image formats
- Real-time color mapping with Jet colormap
- Generate synthetic ToF data
- Interactive zoom and pan

### 2. 3D Point Cloud Viewer
- Load PLY point cloud files
- Interactive 3D visualization
- Point size and color controls
- Reset view functionality

### 3. Data Stream Inspector
- Real-time packet analysis
- Byte-level data inspection
- Hex and decimal value display
- Stream control (start/stop/clear)

## File Formats Supported

### Images
- **PPM**: Portable Pixmap (raw ToF data)
- **PNG**: Standard image format
- **JPEG**: Compressed images

### Point Clouds
- **PLY**: Stanford Triangle Format
- **PCD**: Point Cloud Data format (planned)
- **XYZ**: Simple point format (planned)

## Integration with C++ Pipeline

The GUI is designed to work alongside your existing C++ data processing pipeline:

1. **Data Generation**: C++ generates synthetic ToF data
2. **File Output**: C++ saves data to PPM/PLY files
3. **GUI Loading**: Python GUI loads and visualizes the data
4. **Real-time Updates**: GUI can monitor file changes for live updates

## Customization

### Themes
The GUI uses a modern dark theme by default. You can customize colors by modifying the stylesheet in `main.py`.

### Adding New Visualizations
1. Create a new widget class inheriting from `QWidget`
2. Add it to the main tab widget
3. Connect it to your data sources

### Extending Data Sources
1. Modify the `DataStreamThread` class
2. Add new file format parsers
3. Connect to real hardware APIs

## Troubleshooting

### Common Issues

1. **PyQt6 not found**: Install with `pip install PyQt6`
2. **Matplotlib backend issues**: Ensure Qt5Agg backend is available
3. **3D rendering problems**: Check OpenGL support on your system

### Performance Tips

- For large point clouds, use subsampling
- Enable hardware acceleration if available
- Close unused tabs to free memory

## Development

### Project Structure
```
gui/
├── main.py              # Main GUI application
├── run_gui.py           # Launcher script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Contributing
1. Follow PEP 8 style guidelines
2. Add docstrings to new functions
3. Test with different data formats
4. Update requirements.txt for new dependencies

## License

This GUI is part of the ToF Simulator project and follows the same license terms. 