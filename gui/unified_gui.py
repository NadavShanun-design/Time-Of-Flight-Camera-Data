#!/usr/bin/env python3
"""
Unified ToF Simulator GUI - Everything on One Page
Real data streaming, 3D visualization, and image viewing all together
"""

import sys
import os
import numpy as np
import struct
import time
from pathlib import Path

# Set matplotlib backend before importing matplotlib
import matplotlib
matplotlib.use('qtagg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QLabel, QPushButton, 
                             QTextEdit, QFileDialog, QMessageBox, QProgressBar,
                             QSlider, QGroupBox, QGridLayout, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QImage, QPalette, QColor, QFont, QIcon, QAction

class RealDataStreamThread(QThread):
    """Thread for real data streaming from files"""
    data_received = pyqtSignal(bytes, str)  # data, description
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    
    def __init__(self, file_path=None, chunk_size=1024):
        super().__init__()
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.running = False
        self.delay_ms = 100
        
    def set_file(self, file_path):
        """Set the file to stream from"""
        self.file_path = file_path
        
    def run(self):
        """Stream real data from file"""
        if not self.file_path or not os.path.exists(self.file_path):
            self.status_update.emit("Error: File not found")
            return
            
        self.running = True
        file_size = os.path.getsize(self.file_path)
        bytes_read = 0
        packet_count = 0
        
        try:
            with open(self.file_path, 'rb') as f:
                while self.running and bytes_read < file_size:
                    # Read chunk of real data
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                        
                    bytes_read += len(chunk)
                    packet_count += 1
                    
                    # Calculate progress
                    progress = int((bytes_read / file_size) * 100)
                    
                    # Emit real data
                    description = f"Packet #{packet_count}: {len(chunk)} bytes from {os.path.basename(self.file_path)}"
                    self.data_received.emit(chunk, description)
                    self.progress_update.emit(progress)
                    self.status_update.emit(f"Streaming: {bytes_read}/{file_size} bytes ({progress}%)")
                    
                    # Delay for visualization
                    time.sleep(self.delay_ms / 1000.0)
                    
            self.status_update.emit("Streaming complete")
            
        except Exception as e:
            self.status_update.emit(f"Error: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the streaming"""
        self.running = False

class RealPLYLoader:
    """Real PLY file loader for 3D visualization"""
    
    @staticmethod
    def load_ply_real(file_path, max_points=50000):
        """Load real PLY file and return points, colors, and info"""
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
                
                # Read points
                points = []
                colors = []
                points_to_read = min(info['num_points'], max_points)
                
                if info['format_type'] == 'ascii':
                    for i in range(points_to_read):
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
                    for i in range(points_to_read):
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
                
                return np.array(points), np.array(colors), info
                
        except Exception as e:
            print(f"Error loading PLY file: {e}")
            return None, None, None

class UnifiedToFViewer(QWidget):
    """Unified widget for ToF image viewing"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.current_image = None
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("ToF Image Viewer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00aaff;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(title)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(300, 200)
        self.image_label.setStyleSheet("""
            QLabel {
                background: #0a0a0a;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.image_label.setText("Load a ToF image to view it here")
        layout.addWidget(self.image_label)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load ToF Image")
        self.load_btn.setStyleSheet(self.get_button_style())
        self.load_btn.clicked.connect(self.load_image)
        controls_layout.addWidget(self.load_btn)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
    
    def get_button_style(self):
        return """
            QPushButton {
                background: #2a2a2a;
                color: #00aaff;
                border: 2px solid #00aaff;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00aaff;
                color: #000;
            }
        """
    
    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open ToF Image", "", 
            "PPM Images (*.ppm);;PNG Images (*.png);;All Files (*)"
        )
        if file_name:
            self.display_image(file_name)
    
    def display_image(self, file_path):
        """Display an image file"""
        if file_path.lower().endswith('.ppm'):
            self.display_ppm_image(file_path)
        else:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
    
    def display_ppm_image(self, file_path):
        """Display PPM image with proper parsing"""
        try:
            with open(file_path, 'rb') as f:
                # Read PPM header
                magic = f.readline().decode().strip()
                if magic != 'P6':
                    raise ValueError("Not a P6 PPM file")
                
                # Read dimensions
                dimensions = f.readline().decode().strip()
                width, height = map(int, dimensions.split())
                
                # Read max value
                max_val = int(f.readline().decode().strip())
                
                # Read image data
                data = f.read()
                
                # Convert to numpy array
                img_array = np.frombuffer(data, dtype=np.uint8)
                img_array = img_array.reshape(height, width, 3)
                
                # Convert to QImage
                height, width, channel = img_array.shape
                bytes_per_line = 3 * width
                q_img = QImage(img_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                
                # Display
                pixmap = QPixmap.fromImage(q_img)
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load PPM image: {str(e)}")

class Real3DViewer(QWidget):
    """Real 3D point cloud viewer"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.points = None
        self.colors = None
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("3D Point Cloud Viewer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #ffaa00;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(title)
        
        # 3D Plot
        self.figure = Figure(figsize=(6, 4), facecolor='#0a0a0a')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: #0a0a0a; border: 2px solid #333; border-radius: 8px;")
        layout.addWidget(self.canvas)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load PLY File")
        self.load_btn.setStyleSheet(self.get_button_style())
        self.load_btn.clicked.connect(self.load_ply)
        controls_layout.addWidget(self.load_btn)
        
        self.reset_btn = QPushButton("Reset View")
        self.reset_btn.setStyleSheet(self.get_button_style())
        self.reset_btn.clicked.connect(self.reset_view)
        controls_layout.addWidget(self.reset_btn)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
        
        # Initialize empty 3D plot
        self.setup_3d_plot()
    
    def get_button_style(self):
        return """
            QPushButton {
                background: #2a2a2a;
                color: #ffaa00;
                border: 2px solid #ffaa00;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ffaa00;
                color: #000;
            }
        """
    
    def setup_3d_plot(self):
        """Setup the 3D matplotlib plot"""
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#0a0a0a')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlabel('X', color='white')
        self.ax.set_ylabel('Y', color='white')
        self.ax.set_zlabel('Z', color='white')
        
        # Set dark theme for the plot
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.zaxis.label.set_color('white')
        self.ax.tick_params(colors='white')
        
        # Add placeholder text
        self.ax.text(0, 0, 0, 'Load a PLY file to view 3D point cloud', 
                    color='white', ha='center', va='center', fontsize=12)
        self.ax.set_title('3D Point Cloud Viewer', color='white', pad=20)
        self.canvas.draw()
    
    def load_ply(self):
        """Load real PLY point cloud file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open PLY File", "", 
            "PLY Files (*.ply);;All Files (*)"
        )
        if file_name:
            self.load_ply_file(file_name)
    
    def load_ply_file(self, file_path):
        """Load and display real PLY point cloud"""
        try:
            points, colors, info = RealPLYLoader.load_ply_real(file_path)
            if points is not None and len(points) > 0:
                self.display_points(points, colors, info, file_path)
            else:
                QMessageBox.warning(self, "Error", "Failed to load PLY file or no points found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load PLY file: {str(e)}")
    
    def display_points(self, points, colors, info, file_path):
        """Display real point cloud in 3D plot"""
        # Clear previous plot
        self.ax.clear()
        self.setup_3d_plot()
        
        # Plot real points
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        
        # Use provided colors or create gradient based on height
        if colors is not None and len(colors) == len(points):
            point_colors = colors
        else:
            # Create color gradient based on height
            z_normalized = (z - z.min()) / (z.max() - z.min() + 1e-8)
            point_colors = plt.cm.viridis(z_normalized)
        
        self.ax.scatter(x, y, z, c=point_colors, s=1, alpha=0.8)
        
        # Update title with file info
        filename = os.path.basename(file_path)
        title = f'3D Point Cloud: {filename}\n{len(points)} points'
        if info and info['has_color']:
            title += ' (with colors)'
        self.ax.set_title(title, color='white', pad=20)
        
        self.canvas.draw()
    
    def reset_view(self):
        """Reset the 3D view"""
        self.ax.view_init(elev=20, azim=45)
        self.canvas.draw()

class RealDataInspector(QWidget):
    """Real data stream inspector"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.data_thread = RealDataStreamThread()
        self.data_thread.data_received.connect(self.on_data_received)
        self.data_thread.status_update.connect(self.on_status_update)
        self.data_thread.progress_update.connect(self.on_progress_update)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Real Data Stream Inspector")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(title)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #ccc; padding: 4px;")
        file_layout.addWidget(self.file_label)
        
        self.select_file_btn = QPushButton("Select File")
        self.select_file_btn.setStyleSheet(self.get_button_style())
        self.select_file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.select_file_btn)
        
        layout.addLayout(file_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333;
                border-radius: 5px;
                text-align: center;
                background: #1a1a1a;
            }
            QProgressBar::chunk {
                background: #00ff88;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Stream")
        self.start_btn.setStyleSheet(self.get_button_style())
        self.start_btn.clicked.connect(self.toggle_stream)
        controls_layout.addWidget(self.start_btn)
        
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.setStyleSheet(self.get_button_style())
        self.clear_btn.clicked.connect(self.clear_log)
        controls_layout.addWidget(self.clear_btn)
        
        layout.addLayout(controls_layout)
        
        # Data log
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a;
                color: #00ff88;
                border: 2px solid #333;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def get_button_style(self):
        return """
            QPushButton {
                background: #2a2a2a;
                color: #00ff88;
                border: 2px solid #00ff88;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00ff88;
                color: #000;
            }
        """
    
    def select_file(self):
        """Select a file to stream"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select File to Stream", "", 
            "All Files (*);;PLY Files (*.ply);;PPM Files (*.ppm);;Text Files (*.txt)"
        )
        if file_name:
            self.data_thread.set_file(file_name)
            self.file_label.setText(os.path.basename(file_name))
            self.status_label.setText(f"File selected: {os.path.basename(file_name)}")
    
    def toggle_stream(self):
        """Toggle data stream on/off"""
        if self.data_thread.running:
            self.data_thread.stop()
            self.start_btn.setText("Start Stream")
            self.status_label.setText("Stream stopped")
        else:
            if not self.data_thread.file_path:
                QMessageBox.warning(self, "Warning", "Please select a file first")
                return
            self.data_thread.start()
            self.start_btn.setText("Stop Stream")
            self.status_label.setText("Streaming...")
    
    def on_data_received(self, data, description):
        """Handle received real data packet"""
        # Convert bytes to hex representation
        hex_data = ' '.join(f'{b:02x}' for b in data[:32])  # Show first 32 bytes
        if len(data) > 32:
            hex_data += ' ...'
        
        # Try to parse as different data types
        data_info = []
        
        # As 16-bit values
        if len(data) >= 2:
            try:
                values = struct.unpack(f'<{len(data)//2}H', data[:len(data)//2*2])
                value_str = ' '.join(f'{v:5d}' for v in values[:8])  # Show first 8 values
                if len(values) > 8:
                    value_str += ' ...'
                data_info.append(f"16-bit values: {value_str}")
            except:
                pass
        
        # As 32-bit floats
        if len(data) >= 4:
            try:
                floats = struct.unpack(f'<{len(data)//4}f', data[:len(data)//4*4])
                float_str = ' '.join(f'{f:.2f}' for f in floats[:4])  # Show first 4 floats
                if len(floats) > 4:
                    float_str += ' ...'
                data_info.append(f"32-bit floats: {float_str}")
            except:
                pass
        
        # As ASCII text
        try:
            text = data.decode('ascii', errors='ignore').strip()
            if text and len(text) <= 50:
                data_info.append(f"ASCII: {text}")
        except:
            pass
        
        # Add to log
        log_entry = f"[{time.strftime('%H:%M:%S.%f')[:-3]}] {description}\n"
        log_entry += f"  Hex: {hex_data}\n"
        for info in data_info:
            log_entry += f"  {info}\n"
        log_entry += f"  Size: {len(data)} bytes\n"
        log_entry += "-" * 50 + "\n"
        
        self.log_text.append(log_entry)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_status_update(self, status):
        """Handle status updates"""
        self.status_label.setText(status)
    
    def on_progress_update(self, progress):
        """Handle progress updates"""
        self.progress_bar.setValue(progress)
    
    def clear_log(self):
        """Clear the data log"""
        self.log_text.clear()
        self.progress_bar.setValue(0)

class UnifiedMainWindow(QMainWindow):
    """Unified main window with everything on one page"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_dark_theme()
        
    def setup_ui(self):
        self.setWindowTitle("ToF Simulator - Unified High-Tech GUI")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("ToF Simulator - Real Data Visualization")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00aaff;
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
                background: linear-gradient(90deg, #1a1a1a, #2a2a2a);
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - ToF Image and Data Inspector
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # ToF Image viewer
        self.tof_viewer = UnifiedToFViewer()
        left_layout.addWidget(self.tof_viewer)
        
        # Data Inspector
        self.data_inspector = RealDataInspector()
        left_layout.addWidget(self.data_inspector)
        
        # Right panel - 3D Viewer
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.point_cloud_viewer = Real3DViewer()
        right_layout.addWidget(self.point_cloud_viewer)
        
        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(main_splitter)
        
        # Setup menu bar
        self.setup_menu()
        
        # Setup status bar
        self.statusBar().showMessage("Ready - Load your PLY files and start streaming real data!")
        self.statusBar().setStyleSheet("color: #00aaff; font-weight: bold; background: #1a1a1a;")
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        load_ply_action = QAction("Load PLY File", self)
        load_ply_action.triggered.connect(self.point_cloud_viewer.load_ply)
        file_menu.addAction(load_ply_action)
        
        load_image_action = QAction("Load ToF Image", self)
        load_image_action.triggered.connect(self.tof_viewer.load_image)
        file_menu.addAction(load_image_action)
        
        select_stream_file_action = QAction("Select Stream File", self)
        select_stream_file_action.triggered.connect(self.data_inspector.select_file)
        file_menu.addAction(select_stream_file_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background: #1e1e1e;
                color: #ffffff;
            }
            QMenuBar {
                background: #2a2a2a;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background: #00aaff;
                color: #000000;
            }
            QMenu {
                background: #2a2a2a;
                color: #ffffff;
                border: 1px solid #333;
            }
            QMenu::item:selected {
                background: #00aaff;
                color: #000000;
            }
            QSplitter::handle {
                background: #333;
            }
            QSplitter::handle:hover {
                background: #00aaff;
            }
        """)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About ToF Simulator",
            "<h2>ToF Simulator - Unified High-Tech GUI</h2>"
            "<p>A unified interface for real Time-of-Flight data visualization.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Real PLY file loading and 3D visualization</li>"
            "<li>Real data streaming with byte-level inspection</li>"
            "<li>ToF image viewing and processing</li>"
            "<li>All features on one unified page</li>"
            "<li>No mock data - everything real from your files</li>"
            "</ul>"
            "<p><i>Built with PyQt6 and Python</i></p>")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("ToF Simulator - Unified")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("ToF Research")
    
    # Create and show main window
    window = UnifiedMainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 