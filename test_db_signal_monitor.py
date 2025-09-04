#!/usr/bin/env python3
"""
Test Database Signal Monitor
Test the database signal monitoring system
"""

import sys
import time
from PyQt6 import QtWidgets, QtCore
from database_signal_monitor import DatabaseSignalButton, get_global_monitor

class TestWindow(QtWidgets.QWidget):
    """Test window for database signal monitor"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Signal Monitor Test")
        self.setGeometry(100, 100, 400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the test UI"""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title
        title = QtWidgets.QLabel("Database Signal Monitor Test")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Signal button
        self.signal_button = DatabaseSignalButton(self, 30)
        self.signal_button.start_monitoring(1000)  # 1 second interval
        layout.addWidget(self.signal_button)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Checking database signal...")
        self.status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(self.status_label)
        
        # Info label
        self.info_label = QtWidgets.QLabel("")
        self.info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 12px; color: #666; margin: 10px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)
        
        # Connect signal updates
        self.signal_button.monitor.signal_strength_changed.connect(self.update_status)
        
        # Test buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        test_button = QtWidgets.QPushButton("Test Current Signal")
        test_button.clicked.connect(self.test_current_signal)
        button_layout.addWidget(test_button)
        
        refresh_button = QtWidgets.QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_signal)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
        # Add some spacing
        layout.addStretch()
    
    def update_status(self, signal_strength, icon_path):
        """Update status when signal changes"""
        self.status_label.setText(f"Database Signal: {signal_strength.title()}")
        
        # Update info based on signal strength
        info_text = {
            "unavailable": "Database is offline or unreachable",
            "weak": "Database connection is very slow (>500ms)",
            "okayish": "Database connection is slow (200-500ms)",
            "good": "Database connection is good (100-200ms)",
            "strong": "Database connection is fast (50-100ms)",
            "verystrong": "Database connection is excellent (<50ms)"
        }
        
        self.info_label.setText(info_text.get(signal_strength, "Unknown signal strength"))
        
        # Update button color
        color = self.signal_button.monitor.get_signal_color(signal_strength)
        self.signal_button.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid {color};
                border-radius: 5px;
                background-color: #f0f0f0;
            }}
            QPushButton:hover {{
                border-color: {color};
                background-color: #e0e0e0;
            }}
        """)
    
    def test_current_signal(self):
        """Test current signal strength"""
        signal_strength, icon_path = self.signal_button.get_current_signal()
        self.update_status(signal_strength, icon_path)
        print(f"Current signal: {signal_strength} ({icon_path})")
    
    def refresh_signal(self):
        """Manually refresh signal"""
        self.test_current_signal()

def main():
    """Main test function"""
    print("🧪 DATABASE SIGNAL MONITOR TEST")
    print("=" * 50)
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create test window
    window = TestWindow()
    window.show()
    
    print("📱 Test window opened")
    print("🔍 Monitoring database signal strength...")
    print("📡 Signal updates every 1 second")
    print("🎯 Close window to stop monitoring")
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
