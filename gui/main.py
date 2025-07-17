#!/usr/bin/env python3
"""
ToF Simulator - High-Tech GUI
A beautiful, interactive GUI for Time-of-Flight data visualization
Built with PyQt6, featuring real-time data streaming and 3D visualization
"""

import sys
import os
import numpy as np

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
                             QSlider, QGroupBox, QGridLayout, QTabWidget,
                             QMenuBar, QStatusBar, QToolBar, QFrame)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QImage, QPalette, QColor, QFont, QIcon, QAction
import subprocess
import struct
import time
from pathlib import Path

# Add the src directory to the path so we can import C++ modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class DataStreamThread(QThread):
    """Thread for simulating real-time data streaming"""
    data_received = pyqtSignal(bytes, str)  # data, description
    status_update = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.packet_size = 1024
        self.delay_ms = 100
        
    def run(self):
        self.running = True
        packet_count = 0
        
        while self.running:
            # Simulate packet data
            packet_data = self.generate_mock_packet(packet_count)
            description = f"Packet #{packet_count}: {len(packet_data)} bytes"
            
            self.data_received.emit(packet_data, description)
            packet_count += 1
            
            time.sleep(self.delay_ms / 1000.0)
    
    def generate_mock_packet(self, packet_num):
        """Generate mock ToF data packet"""
        # Simulate 16-bit depth values
        num_pixels = self.packet_size // 2
        base_depth = 1000 + (packet_num * 10) % 500
        noise = np.random.randint(-20, 21, num_pixels)
        depths = np.clip(base_depth + noise, 0, 65535).astype(np.uint16)
        
        # Convert to bytes (little-endian)
        return depths.tobytes()
    
    def stop(self):
        self.running = False

class ToFImageWidget(QWidget):
    """Widget for displaying ToF images with real-time updates"""
    
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
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("""
            QLabel {
                background: #0a0a0a;
                border: 2px solid #333;
                border-radius: 10px;
                padding: 20px;
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
        
        self.generate_btn = QPushButton("Generate Synthetic")
        self.generate_btn.setStyleSheet(self.get_button_style())
        self.generate_btn.clicked.connect(self.generate_synthetic)
        controls_layout.addWidget(self.generate_btn)
        
        layout.addLayout(controls_layout)
        self.setLayout(layout)
    
    def get_button_style(self):
        return """
            QPushButton {
                background: #2a2a2a;
                color: #00aaff;
                border: 2px solid #00aaff;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00aaff;
                color: #000;
            }
            QPushButton:pressed {
                background: #0088cc;
                color: #fff;
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
            # Handle PPM format
            self.display_ppm_image(file_path)
        else:
            # Handle other formats
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
    
    def generate_synthetic(self):
        """Generate synthetic ToF image"""
        # This will be connected to the C++ ToF generator
        QMessageBox.information(self, "Generate", "Synthetic ToF generation coming soon!")

class PointCloudWidget(QWidget):
    """Widget for 3D point cloud visualization"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.points = None
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("3D Point Cloud Viewer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #ffaa00;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
        # 3D Plot
        self.figure = Figure(figsize=(8, 6), facecolor='#0a0a0a')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: #0a0a0a; border: 2px solid #333; border-radius: 10px;")
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
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #ffaa00;
                color: #000;
            }
            QPushButton:pressed {
                background: #cc8800;
                color: #fff;
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
        
        # Add some sample points for demo
        self.plot_sample_points()
        self.canvas.draw()
    
    def plot_sample_points(self):
        """Plot sample points for demonstration"""
        # Generate some sample 3D points
        n_points = 1000
        x = np.random.randn(n_points) * 10
        y = np.random.randn(n_points) * 10
        z = np.random.randn(n_points) * 5
        
        # Create a color gradient based on height
        colors = plt.cm.viridis((z - z.min()) / (z.max() - z.min()))
        
        self.ax.scatter(x, y, z, c=colors, s=1, alpha=0.6)
        self.ax.set_title('Sample Point Cloud', color='white', pad=20)
    
    def load_ply(self):
        """Load PLY point cloud file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open PLY File", "", 
            "PLY Files (*.ply);;All Files (*)"
        )
        if file_name:
            self.load_ply_file(file_name)
    
    def load_ply_file(self, file_path):
        """Load and display PLY point cloud"""
        try:
            # For now, we'll use a simple PLY parser
            # In a full implementation, this would use the C++ PLYLoader
            points = self.parse_ply_simple(file_path)
            if points is not None:
                self.display_points(points)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load PLY file: {str(e)}")
    
    def parse_ply_simple(self, file_path):
        """Simple PLY parser for demonstration"""
        try:
            with open(file_path, 'rb') as f:
                # Read header
                line = f.readline().decode().strip()
                if line != 'ply':
                    raise ValueError("Not a PLY file")
                
                # Skip to vertex count
                while True:
                    line = f.readline().decode().strip()
                    if line.startswith('element vertex'):
                        num_vertices = int(line.split()[-1])
                        break
                
                # Skip to end_header
                while f.readline().decode().strip() != 'end_header':
                    pass
                
                # Read points (assuming x,y,z format)
                points = []
                for i in range(min(num_vertices, 10000)):  # Limit for performance
                    data = f.read(12)  # 3 floats * 4 bytes
                    if len(data) == 12:
                        x, y, z = struct.unpack('fff', data)
                        points.append([x, y, z])
                
                return np.array(points)
        except Exception as e:
            print(f"PLY parsing error: {e}")
            return None
    
    def display_points(self, points):
        """Display point cloud in 3D plot"""
        if points is None or len(points) == 0:
            return
        
        # Clear previous plot
        self.ax.clear()
        self.setup_3d_plot()
        
        # Plot points
        x, y, z = points[:, 0], points[:, 1], points[:, 2]
        colors = plt.cm.viridis((z - z.min()) / (z.max() - z.min() + 1e-8))
        
        self.ax.scatter(x, y, z, c=colors, s=1, alpha=0.6)
        self.ax.set_title(f'Point Cloud: {len(points)} points', color='white', pad=20)
        
        self.canvas.draw()
    
    def reset_view(self):
        """Reset the 3D view"""
        self.ax.view_init(elev=20, azim=45)
        self.canvas.draw()

class DataInspectorWidget(QWidget):
    """Widget for inspecting data streams and packets"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.data_thread = DataStreamThread()
        self.data_thread.data_received.connect(self.on_data_received)
        self.data_thread.status_update.connect(self.on_status_update)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Data Stream Inspector")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)
        
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
                font-size: 12px;
            }
        """)
        self.log_text.setMaximumHeight(200)
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
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00ff88;
                color: #000;
            }
            QPushButton:pressed {
                background: #00cc66;
                color: #fff;
            }
        """
    
    def toggle_stream(self):
        """Toggle data stream on/off"""
        if self.data_thread.running:
            self.data_thread.stop()
            self.start_btn.setText("Start Stream")
            self.status_label.setText("Stream stopped")
        else:
            self.data_thread.start()
            self.start_btn.setText("Stop Stream")
            self.status_label.setText("Streaming...")
    
    def on_data_received(self, data, description):
        """Handle received data packet"""
        # Convert bytes to hex representation
        hex_data = ' '.join(f'{b:02x}' for b in data[:32])  # Show first 32 bytes
        if len(data) > 32:
            hex_data += ' ...'
        
        # Parse as 16-bit values
        if len(data) >= 2:
            values = struct.unpack(f'<{len(data)//2}H', data[:len(data)//2*2])
            value_str = ' '.join(f'{v:5d}' for v in values[:8])  # Show first 8 values
            if len(values) > 8:
                value_str += ' ...'
        else:
            value_str = "Invalid data"
        
        # Add to log
        log_entry = f"[{time.strftime('%H:%M:%S')}] {description}\n"
        log_entry += f"  Hex: {hex_data}\n"
        log_entry += f"  Values: {value_str}\n"
        log_entry += f"  Size: {len(data)} bytes\n"
        log_entry += "-" * 50 + "\n"
        
        self.log_text.append(log_entry)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_status_update(self, status):
        """Handle status updates"""
        self.status_label.setText(status)
    
    def clear_log(self):
        """Clear the data log"""
        self.log_text.clear()

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_dark_theme()
        
    def setup_ui(self):
        self.setWindowTitle("ToF Simulator - High-Tech GUI")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Create main splitter for image and 3D view
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ToF Image widget
        self.tof_widget = ToFImageWidget()
        main_splitter.addWidget(self.tof_widget)
        
        # 3D Point Cloud widget
        self.point_cloud_widget = PointCloudWidget()
        main_splitter.addWidget(self.point_cloud_widget)
        
        # Data Inspector widget
        self.data_inspector = DataInspectorWidget()
        
        # Add widgets to tabs
        self.tab_widget.addTab(main_splitter, "Visualization")
        self.tab_widget.addTab(self.data_inspector, "Data Inspector")
        
        # Setup menu bar
        self.setup_menu()
        
        # Setup status bar
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("color: #00aaff; font-weight: bold;")
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_image_action = QAction("Open ToF Image", self)
        open_image_action.triggered.connect(self.tof_widget.load_image)
        file_menu.addAction(open_image_action)
        
        open_ply_action = QAction("Open PLY File", self)
        open_ply_action.triggered.connect(self.point_cloud_widget.load_ply)
        file_menu.addAction(open_ply_action)
        
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
            QTabWidget::pane {
                border: 1px solid #333;
                background: #1e1e1e;
            }
            QTabBar::tab {
                background: #2a2a2a;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #00aaff;
                color: #000000;
            }
            QTabBar::tab:hover {
                background: #3a3a3a;
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
        """)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About ToF Simulator",
            "<h2>ToF Simulator - High-Tech GUI</h2>"
            "<p>A beautiful, interactive GUI for Time-of-Flight data visualization.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Real-time ToF image loading and visualization</li>"
            "<li>3D point cloud viewer with interactive controls</li>"
            "<li>Data stream inspector with packet analysis</li>"
            "<li>Modern, clean, high-tech design</li>"
            "<li>Extensible for hardware and new formats</li>"
            "</ul>"
            "<p><i>Built with PyQt6 and Python</i></p>")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("ToF Simulator")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("ToF Research")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 