#!/usr/bin/env python3
"""
Hardware ToF Simulator GUI
Real hardware simulation with data streaming and 3D visualization
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
                             QSlider, QGroupBox, QGridLayout, QFrame, QComboBox,
                             QSpinBox, QCheckBox)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QImage, QPalette, QColor, QFont, QIcon, QAction

# Import hardware simulator
from hardware_simulator import HardwareDataManager

class HardwareStreamThread(QThread):
    """Thread for hardware data streaming"""
    data_received = pyqtSignal(dict)  # packet data
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    point_received = pyqtSignal(np.ndarray, np.ndarray)  # points, colors
    
    def __init__(self, hardware_manager, points_per_packet=100, delay_ms=50):
        super().__init__()
        self.hardware_manager = hardware_manager
        self.points_per_packet = points_per_packet
        self.delay_ms = delay_ms
        self.running = False
        
    def run(self):
        """Stream real data from hardware"""
        if not self.hardware_manager.simulator.is_connected:
            self.status_update.emit("Error: Hardware not connected")
            return
            
        self.running = True
        self.status_update.emit("Starting hardware data stream...")
        
        try:
            for packet in self.hardware_manager.start_streaming(
                points_per_packet=self.points_per_packet, 
                delay_ms=self.delay_ms
            ):
                if not self.running:
                    break
                    
                # Emit packet data
                self.data_received.emit(packet)
                self.progress_update.emit(int(packet['progress']))
                
                # Emit points for 3D visualization
                if packet['points'] is not None:
                    self.point_received.emit(packet['points'], packet['colors'])
                
                # Update status
                self.status_update.emit(
                    f"Streaming: Packet {packet['packet_id']}, "
                    f"{len(packet['points'])} points, "
                    f"{len(packet['raw_bytes'])} bytes"
                )
                
        except Exception as e:
            self.status_update.emit(f"Stream error: {str(e)}")
        finally:
            self.running = False
            self.status_update.emit("Hardware stream complete")
    
    def stop(self):
        """Stop the hardware stream"""
        self.running = False
        self.hardware_manager.stop_streaming()

class RealTime3DViewer(QWidget):
    """Real-time 3D point cloud viewer that updates as data streams in"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.all_points = []
        self.all_colors = []
        self.max_points_display = 10000  # Limit for performance
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Real-Time 3D Hardware Viewer")
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
        self.figure = Figure(figsize=(8, 6), facecolor='#0a0a0a')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: #0a0a0a; border: 2px solid #333; border-radius: 8px;")
        layout.addWidget(self.canvas)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Reset View")
        self.reset_btn.setStyleSheet(self.get_button_style())
        self.reset_btn.clicked.connect(self.reset_view)
        controls_layout.addWidget(self.reset_btn)
        
        self.clear_btn = QPushButton("Clear Points")
        self.clear_btn.setStyleSheet(self.get_button_style())
        self.clear_btn.clicked.connect(self.clear_points)
        controls_layout.addWidget(self.clear_btn)
        
        # Point limit control
        self.point_limit_label = QLabel("Max Points:")
        self.point_limit_label.setStyleSheet("color: #ffaa00;")
        controls_layout.addWidget(self.point_limit_label)
        
        self.point_limit_spin = QSpinBox()
        self.point_limit_spin.setRange(1000, 50000)
        self.point_limit_spin.setValue(10000)
        self.point_limit_spin.setStyleSheet("""
            QSpinBox {
                background: #2a2a2a;
                color: #ffaa00;
                border: 1px solid #ffaa00;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        self.point_limit_spin.valueChanged.connect(self.update_point_limit)
        controls_layout.addWidget(self.point_limit_spin)
        
        layout.addLayout(controls_layout)
        
        # Status
        self.status_label = QLabel("Ready for hardware data")
        self.status_label.setStyleSheet("color: #ffaa00; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Initialize 3D plot
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
        self.ax.text(0, 0, 0, 'Waiting for hardware data...', 
                    color='white', ha='center', va='center', fontsize=12)
        self.ax.set_title('Real-Time 3D Hardware Viewer', color='white', pad=20)
        self.canvas.draw()
    
    def add_points(self, points, colors=None):
        """Add new points to the 3D visualization"""
        if points is None or len(points) == 0:
            return
            
        # Add to our collection
        self.all_points.extend(points)
        if colors is not None:
            self.all_colors.extend(colors)
        else:
            # Default colors
            default_colors = np.array([[0.5, 0.5, 0.5]] * len(points))
            self.all_colors.extend(default_colors)
        
        # Limit points for performance
        if len(self.all_points) > self.max_points_display:
            self.all_points = self.all_points[-self.max_points_display:]
            self.all_colors = self.all_colors[-self.max_points_display:]
        
        # Update visualization
        self.update_visualization()
    
    def update_visualization(self):
        """Update the 3D visualization with all collected points"""
        if not self.all_points:
            return
            
        # Clear previous plot
        self.ax.clear()
        self.setup_3d_plot()
        
        # Convert to numpy arrays
        points_array = np.array(self.all_points)
        colors_array = np.array(self.all_colors)
        
        # Plot points
        x, y, z = points_array[:, 0], points_array[:, 1], points_array[:, 2]
        
        # Use provided colors or create gradient
        if colors_array is not None and len(colors_array) == len(points_array):
            point_colors = colors_array
        else:
            # Create color gradient based on height
            z_normalized = (z - z.min()) / (z.max() - z.min() + 1e-8)
            point_colors = plt.cm.viridis(z_normalized)
        
        self.ax.scatter(x, y, z, c=point_colors, s=1, alpha=0.8)
        
        # Update title with point count
        title = f'Real-Time 3D Hardware Viewer\n{len(self.all_points)} points received'
        self.ax.set_title(title, color='white', pad=20)
        
        # Update status
        self.status_label.setText(f"Points received: {len(self.all_points)}")
        
        self.canvas.draw()
    
    def reset_view(self):
        """Reset the 3D view"""
        self.ax.view_init(elev=20, azim=45)
        self.canvas.draw()
    
    def clear_points(self):
        """Clear all points"""
        self.all_points = []
        self.all_colors = []
        self.setup_3d_plot()
        self.status_label.setText("Points cleared")
    
    def update_point_limit(self, limit):
        """Update the maximum number of points to display"""
        self.max_points_display = limit
        if len(self.all_points) > limit:
            self.all_points = self.all_points[-limit:]
            self.all_colors = self.all_colors[-limit:]
            self.update_visualization()

class HardwareControlPanel(QWidget):
    """Control panel for hardware simulation"""
    
    def __init__(self, hardware_manager):
        super().__init__()
        self.hardware_manager = hardware_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Hardware Control Panel")
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
        
        # Data folder info
        folder_group = QGroupBox("Data Source")
        folder_group.setStyleSheet("""
            QGroupBox {
                color: #00ff88;
                font-weight: bold;
                border: 2px solid #00ff88;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        folder_layout = QVBoxLayout(folder_group)
        
        self.folder_label = QLabel(f"Data Folder: {self.hardware_manager.get_data_folder_path()}")
        self.folder_label.setStyleSheet("color: #ccc; font-size: 10px;")
        self.folder_label.setWordWrap(True)
        folder_layout.addWidget(self.folder_label)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_combo = QComboBox()
        self.file_combo.setStyleSheet("""
            QComboBox {
                background: #2a2a2a;
                color: #00ff88;
                border: 1px solid #00ff88;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        self.refresh_files()
        file_layout.addWidget(self.file_combo)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(self.get_button_style())
        self.refresh_btn.clicked.connect(self.refresh_files)
        file_layout.addWidget(self.refresh_btn)
        
        folder_layout.addLayout(file_layout)
        layout.addWidget(folder_group)
        
        # Hardware controls
        hardware_group = QGroupBox("Hardware Controls")
        hardware_group.setStyleSheet("""
            QGroupBox {
                color: #00ff88;
                font-weight: bold;
                border: 2px solid #00ff88;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        hardware_layout = QVBoxLayout(hardware_group)
        
        # Connect button
        self.connect_btn = QPushButton("Connect to Hardware")
        self.connect_btn.setStyleSheet(self.get_button_style())
        self.connect_btn.clicked.connect(self.connect_hardware)
        hardware_layout.addWidget(self.connect_btn)
        
        # Disconnect button
        self.disconnect_btn = QPushButton("Disconnect Hardware")
        self.disconnect_btn.setStyleSheet(self.get_button_style())
        self.disconnect_btn.clicked.connect(self.disconnect_hardware)
        self.disconnect_btn.setEnabled(False)
        hardware_layout.addWidget(self.disconnect_btn)
        
        # Stream controls
        stream_layout = QHBoxLayout()
        
        self.stream_btn = QPushButton("Start Data Stream")
        self.stream_btn.setStyleSheet(self.get_button_style())
        self.stream_btn.clicked.connect(self.start_stream)
        self.stream_btn.setEnabled(False)
        stream_layout.addWidget(self.stream_btn)
        
        self.stop_btn = QPushButton("Stop Stream")
        self.stop_btn.setStyleSheet(self.get_button_style())
        self.stop_btn.clicked.connect(self.stop_stream)
        self.stop_btn.setEnabled(False)
        stream_layout.addWidget(self.stop_btn)
        
        hardware_layout.addLayout(stream_layout)
        
        # Stream settings
        settings_layout = QGridLayout()
        
        settings_layout.addWidget(QLabel("Points/Packet:"), 0, 0)
        self.points_per_packet = QSpinBox()
        self.points_per_packet.setRange(10, 1000)
        self.points_per_packet.setValue(100)
        self.points_per_packet.setStyleSheet("""
            QSpinBox {
                background: #2a2a2a;
                color: #00ff88;
                border: 1px solid #00ff88;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        settings_layout.addWidget(self.points_per_packet, 0, 1)
        
        settings_layout.addWidget(QLabel("Delay (ms):"), 1, 0)
        self.delay_ms = QSpinBox()
        self.delay_ms.setRange(10, 500)
        self.delay_ms.setValue(50)
        self.delay_ms.setStyleSheet("""
            QSpinBox {
                background: #2a2a2a;
                color: #00ff88;
                border: 1px solid #00ff88;
                border-radius: 3px;
                padding: 2px;
            }
        """)
        settings_layout.addWidget(self.delay_ms, 1, 1)
        
        hardware_layout.addLayout(settings_layout)
        layout.addWidget(hardware_group)
        
        # Status
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Add signal attributes
        self.stream_started = None
        self.stream_stopped = None
        
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
            QPushButton:disabled {
                background: #1a1a1a;
                color: #666;
                border: 2px solid #666;
            }
        """
    
    def refresh_files(self):
        """Refresh the list of available PLY files"""
        self.file_combo.clear()
        files = self.hardware_manager.list_available_files()
        if files:
            self.file_combo.addItems(files)
            self.status_label.setText(f"Found {len(files)} PLY files")
        else:
            self.status_label.setText("No PLY files found in data folder")
    
    def connect_hardware(self):
        """Connect to simulated hardware"""
        if self.file_combo.currentText():
            filename = self.file_combo.currentText()
            if self.hardware_manager.load_file(filename):
                if self.hardware_manager.connect_hardware():
                    self.connect_btn.setEnabled(False)
                    self.disconnect_btn.setEnabled(True)
                    self.stream_btn.setEnabled(True)
                    self.status_label.setText(f"Connected to hardware: {filename}")
                    
                    # Show file info
                    info = self.hardware_manager.get_current_file_info()
                    if info:
                        msg = f"File: {info['filename']}\n"
                        msg += f"Points: {info['points']}\n"
                        msg += f"Has colors: {info['has_colors']}\n"
                        msg += f"Format: {info['format']}"
                        QMessageBox.information(self, "Hardware Connected", msg)
                else:
                    QMessageBox.warning(self, "Connection Failed", "Failed to connect to hardware")
            else:
                QMessageBox.warning(self, "Load Failed", f"Failed to load file: {filename}")
        else:
            QMessageBox.warning(self, "No File", "Please select a PLY file first")
    
    def disconnect_hardware(self):
        """Disconnect from hardware"""
        self.hardware_manager.disconnect_hardware()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.stream_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Hardware disconnected")
    
    def start_stream(self):
        """Start data streaming"""
        self.stream_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Starting data stream...")
        
        # Call signal to start streaming (will be connected in main window)
        if self.stream_started:
            self.stream_started(
                self.points_per_packet.value(),
                self.delay_ms.value()
            )
    
    def stop_stream(self):
        """Stop data streaming"""
        self.stream_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Stopping data stream...")
        
        # Call signal to stop streaming
        if self.stream_stopped:
            self.stream_stopped()

class HardwareDataInspector(QWidget):
    """Real hardware data inspector"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Hardware Data Inspector")
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
                background: #00aaff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Data log
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a;
                color: #00aaff;
                border: 2px solid #333;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear Log")
        self.clear_btn.setStyleSheet(self.get_button_style())
        self.clear_btn.clicked.connect(self.clear_log)
        controls_layout.addWidget(self.clear_btn)
        
        layout.addLayout(controls_layout)
        
        # Status
        self.status_label = QLabel("Waiting for hardware data...")
        self.status_label.setStyleSheet("color: #00aaff; font-weight: bold;")
        layout.addWidget(self.status_label)
        
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
    
    def on_data_received(self, packet_data):
        """Handle received hardware data packet"""
        # Convert bytes to hex representation
        raw_bytes = packet_data['raw_bytes']
        hex_data = ' '.join(f'{b:02x}' for b in raw_bytes[:32])  # Show first 32 bytes
        if len(raw_bytes) > 32:
            hex_data += ' ...'
        
        # Parse as different data types
        data_info = []
        
        # As 32-bit floats (position data)
        if len(raw_bytes) >= 12:
            try:
                floats = struct.unpack(f'<{len(raw_bytes)//4}f', raw_bytes[:len(raw_bytes)//4*4])
                float_str = ' '.join(f'{f:.3f}' for f in floats[:6])  # Show first 6 floats (2 points)
                if len(floats) > 6:
                    float_str += ' ...'
                data_info.append(f"32-bit floats (positions): {float_str}")
            except:
                pass
        
        # As bytes (color data)
        if len(raw_bytes) >= 15:
            try:
                colors = struct.unpack(f'<{len(raw_bytes)}B', raw_bytes)
                color_str = ' '.join(f'{c:3d}' for c in colors[:9])  # Show first 9 bytes (3 colors)
                if len(colors) > 9:
                    color_str += ' ...'
                data_info.append(f"Color bytes: {color_str}")
            except:
                pass
        
        # Add to log
        log_entry = f"[{time.strftime('%H:%M:%S.%f')[:-3]}] {packet_data['description']}\n"
        log_entry += f"  Progress: {packet_data['progress']:.1f}%\n"
        log_entry += f"  Hex: {hex_data}\n"
        for info in data_info:
            log_entry += f"  {info}\n"
        log_entry += f"  Size: {len(raw_bytes)} bytes\n"
        log_entry += "-" * 50 + "\n"
        
        self.log_text.append(log_entry)
        
        # Update progress
        self.progress_bar.setValue(int(packet_data['progress']))
        
        # Update status
        self.status_label.setText(f"Received: {packet_data['packet_id']} packets")
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_status_update(self, status):
        """Handle status updates"""
        self.status_label.setText(status)
    
    def clear_log(self):
        """Clear the data log"""
        self.log_text.clear()
        self.progress_bar.setValue(0)

class HardwareMainWindow(QMainWindow):
    """Main window for hardware simulation"""
    
    def __init__(self):
        super().__init__()
        self.hardware_manager = HardwareDataManager()
        self.stream_thread = None
        self.setup_ui()
        self.apply_dark_theme()
        
    def setup_ui(self):
        self.setWindowTitle("ToF Camera Hardware Simulator")
        self.setGeometry(100, 100, 1800, 1100)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("ToF Camera Hardware Simulator - Real Data Streaming")
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
        
        # Left panel - Hardware controls and data inspector
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Hardware control panel
        self.hardware_control = HardwareControlPanel(self.hardware_manager)
        left_layout.addWidget(self.hardware_control)
        
        # Data inspector
        self.data_inspector = HardwareDataInspector()
        left_layout.addWidget(self.data_inspector)
        
        # Right panel - 3D viewer
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.rt_3d_viewer = RealTime3DViewer()
        right_layout.addWidget(self.rt_3d_viewer)
        
        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        
        main_layout.addWidget(main_splitter)
        
        # Setup menu bar
        self.setup_menu()
        
        # Setup status bar
        self.statusBar().showMessage(f"Ready - Place PLY files in: {self.hardware_manager.get_data_folder_path()}")
        self.statusBar().setStyleSheet("color: #00aaff; font-weight: bold; background: #1a1a1a;")
        
        # Connect signals
        self.hardware_control.stream_started = self.start_hardware_stream
        self.hardware_control.stream_stopped = self.stop_hardware_stream
        
    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        refresh_action = QAction("Refresh Files", self)
        refresh_action.triggered.connect(self.hardware_control.refresh_files)
        file_menu.addAction(refresh_action)
        
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
    
    def start_hardware_stream(self, points_per_packet, delay_ms):
        """Start hardware data streaming"""
        if self.stream_thread is not None:
            self.stream_thread.stop()
            self.stream_thread.wait()
        
        self.stream_thread = HardwareStreamThread(
            self.hardware_manager, 
            points_per_packet, 
            delay_ms
        )
        
        # Connect signals
        self.stream_thread.data_received.connect(self.data_inspector.on_data_received)
        self.stream_thread.status_update.connect(self.data_inspector.on_status_update)
        self.stream_thread.point_received.connect(self.rt_3d_viewer.add_points)
        
        self.stream_thread.start()
    
    def stop_hardware_stream(self):
        """Stop hardware data streaming"""
        if self.stream_thread is not None:
            self.stream_thread.stop()
            self.stream_thread.wait()
            self.stream_thread = None
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About ToF Hardware Simulator",
            "<h2>ToF Camera Hardware Simulator</h2>"
            "<p>Real hardware simulation with data streaming and 3D visualization.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Real PLY file loading from hardware data folder</li>"
            "<li>Hardware connection simulation</li>"
            "<li>Real-time data streaming with byte-level inspection</li>"
            "<li>Real-time 3D visualization as data arrives</li>"
            "<li>No mock data - everything real from your files</li>"
            "</ul>"
            "<p><b>Data Folder:</b></p>"
            f"<p>{self.hardware_manager.get_data_folder_path()}</p>"
            "<p><i>Built with PyQt6 and Python</i></p>")

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("ToF Hardware Simulator")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("ToF Research")
    
    # Create and show main window
    window = HardwareMainWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 