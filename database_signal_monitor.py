#!/usr/bin/env python3
"""
Database Signal Monitor
Real-time database connection monitoring with signal strength indicators
"""

import os
import time
import threading
from typing import Optional, Callable
from PyQt6 import QtCore, QtGui, QtWidgets
from database_manager import is_database_available, get_database_connection

class DatabaseSignalMonitor(QtCore.QObject):
    """Monitors database connection and provides signal strength updates"""
    
    # Signal emitted when signal strength changes
    signal_strength_changed = QtCore.pyqtSignal(str, str)  # strength, icon_path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.monitoring = False
        self.monitor_thread = None
        self.update_interval = 500  # 500 milliseconds
        self.signal_callbacks = []
        self.last_signal_strength = None  # Track last signal to avoid spam
        
        # Icon paths
        self.icon_base_path = os.path.join(os.path.dirname(__file__), "emoji")
        self.icons = {
            "unavailable": "db_unavailable_30x30.png",
            "weak": "wifi_weak_30x30.png", 
            "okayish": "wifi_okish_30x30.png",
            "good": "wifi_strong_30x30.png",
            "strong": "wifi_strong_30x30.png",
            "verystrong": "wifi_verystrong_30x30.png"
        }
        
        # Signal strength colors
        self.signal_colors = {
            "unavailable": "#FF0000",  # Red
            "weak": "#FF0000",         # Red
            "okayish": "#FFA500",      # Orange
            "good": "#FFFF00",         # Yellow
            "strong": "#00FF00",       # Green
            "verystrong": "#00FF00"    # Green
        }
    
    def start_monitoring(self, interval_ms: int = 500):
        """Start monitoring database signal strength"""
        if self.monitoring:
            return
        
        self.update_interval = interval_ms
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        # Silent start - no console spam
    
    def stop_monitoring(self):
        """Stop monitoring database signal strength"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        # Silent stop - no console spam
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread"""
        while self.monitoring:
            try:
                signal_strength = self._check_database_signal()
                icon_path = self._get_icon_path(signal_strength)
                
                # Only log when signal strength actually changes
                if signal_strength != self.last_signal_strength:
                    if self.last_signal_strength is None:
                        print(f"📡 Database signal: {signal_strength}")
                    else:
                        print(f"📡 Database signal changed: {self.last_signal_strength} → {signal_strength}")
                    self.last_signal_strength = signal_strength
                
                # Always emit signal to update UI (thread-safe)
                self.signal_strength_changed.emit(signal_strength, icon_path)
                
                # Call registered callbacks
                for callback in self.signal_callbacks:
                    try:
                        callback(signal_strength, icon_path)
                    except Exception as e:
                        print(f"Error in signal callback: {e}")
                
                time.sleep(self.update_interval / 1000.0)
                
            except Exception as e:
                print(f"Error in database monitoring: {e}")
                # Emit unavailable signal on error
                self.signal_strength_changed.emit("unavailable", self._get_icon_path("unavailable"))
                time.sleep(self.update_interval / 1000.0)
    
    def _check_database_signal(self) -> str:
        """Check database connection and return signal strength"""
        try:
            start_time = time.time()
            
            # Check if database is available
            if not is_database_available():
                return "unavailable"
            
            # Try to get connection and measure latency
            connection = get_database_connection()
            if not connection:
                return "unavailable"
            
            # Test connection with a simple query
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Map latency to signal strength
            if latency_ms < 50:
                return "verystrong"
            elif latency_ms < 100:
                return "strong"
            elif latency_ms < 200:
                return "good"
            elif latency_ms < 500:
                return "okayish"
            else:
                return "weak"
                
        except Exception as e:
            print(f"Database signal check failed: {e}")
            return "unavailable"
    
    def _get_icon_path(self, signal_strength: str) -> str:
        """Get the full path to the icon for the given signal strength"""
        icon_filename = self.icons.get(signal_strength, self.icons["unavailable"])
        return os.path.join(self.icon_base_path, icon_filename)
    
    def get_signal_color(self, signal_strength: str) -> str:
        """Get the color for the given signal strength"""
        return self.signal_colors.get(signal_strength, "#FF0000")
    
    def add_signal_callback(self, callback: Callable[[str, str], None]):
        """Add a callback function to be called when signal strength changes"""
        self.signal_callbacks.append(callback)
    
    def remove_signal_callback(self, callback: Callable[[str, str], None]):
        """Remove a signal callback"""
        if callback in self.signal_callbacks:
            self.signal_callbacks.remove(callback)
    
    def get_current_signal(self) -> tuple[str, str]:
        """Get current signal strength and icon path (synchronous)"""
        signal_strength = self._check_database_signal()
        icon_path = self._get_icon_path(signal_strength)
        return signal_strength, icon_path

class DatabaseSignalButton(QtWidgets.QPushButton):
    """A push button that displays database signal strength"""
    
    def __init__(self, parent=None, size: int = 30, skip_initial_test: bool = False):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.icon_size = size
        self.status = "unknown"
        
        # Initialize the monitor
        self.monitor = DatabaseSignalMonitor(self)
        self.monitor.signal_strength_changed.connect(self._update_signal_icon)
        
        # Set up timer for periodic checks
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._check_connection)
        
        # Set initial icon to unavailable
        self._update_signal_icon("unavailable", self.monitor._get_icon_path("unavailable"))
        
        if not skip_initial_test:
            # Start monitoring immediately if not skipped
            self.start_monitoring(1000)  # 1 second interval

    def start_monitoring(self, interval_ms: int = 1000):
        """Start monitoring database signal strength"""
        self.monitor.start_monitoring(interval_ms)
    
    def stop_monitoring(self):
        """Stop monitoring database signal strength"""
        self.monitor.stop_monitoring()
    
    def _check_connection(self):
        """Check database connection and update button icon"""
        try:
            signal_strength = self.monitor._check_database_signal()
            icon_path = self.monitor._get_icon_path(signal_strength)
            self._update_signal_icon(signal_strength, icon_path)
        except Exception as e:
            print(f"Error in _check_connection: {e}")
            self._update_signal_icon("unavailable", self.monitor._get_icon_path("unavailable"))
    
    def _update_signal_icon(self, signal_strength: str, icon_path: str):
        """Update the button icon based on signal strength"""
        try:
            if os.path.exists(icon_path):
                # Load and resize icon
                pixmap = QtGui.QPixmap(icon_path)
                if not pixmap.isNull():
                    # Resize icon while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        self.icon_size, 
                        self.icon_size, 
                        QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                        QtCore.Qt.TransformationMode.SmoothTransformation
                    )
                    
                    # Create icon
                    icon = QtGui.QIcon(scaled_pixmap)
                    self.setIcon(icon)
                    self.setIconSize(QtCore.QSize(self.icon_size, self.icon_size))
                    
                    # Update tooltip
                    self.setToolTip(f"Database: {signal_strength.title()}")
                    
                    # Update button color based on signal strength
                    color = self.monitor.get_signal_color(signal_strength)
                    self.setStyleSheet(f"""
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
                    
                    # Silent update - no console spam
                else:
                    print(f"⚠️ Failed to load icon: {icon_path}")
            else:
                print(f"⚠️ Icon file not found: {icon_path}")
                
        except Exception as e:
            print(f"❌ Error updating signal icon: {e}")
    
    def get_current_signal(self) -> tuple[str, str]:
        """Get current signal strength and icon path"""
        return self.monitor.get_current_signal()

# Global monitor instance
_global_monitor = None

def get_global_monitor() -> DatabaseSignalMonitor:
    """Get the global database signal monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = DatabaseSignalMonitor()
    return _global_monitor

def create_database_signal_button(parent=None, icon_size: int = 30) -> DatabaseSignalButton:
    """Create a database signal button with monitoring"""
    button = DatabaseSignalButton(parent, icon_size)
    button.start_monitoring(1000)  # 1 second interval
    return button

def init_async_db_monitor(button: DatabaseSignalButton, interval: int = 500):
    """Initialize database monitoring in background thread."""
    def _async_init():
        try:
            # Initial check in background
            button._check_connection()
            # Start periodic monitoring
            button.start_monitoring(interval)
            print("✅ Database monitoring started in background")
        except Exception as e:
            print(f"❌ Failed to start database monitoring: {e}")
            # Set to unavailable state
            button._update_signal_icon("unavailable", button.monitor._get_icon_path("unavailable"))
        
    thread = threading.Thread(target=_async_init, daemon=True)
    thread.start()

if __name__ == "__main__":
    import sys
    from PyQt6 import QtWidgets
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create test window
    window = QtWidgets.QWidget()
    window.setWindowTitle("Database Signal Monitor Test")
    window.setGeometry(100, 100, 300, 200)
    
    layout = QtWidgets.QVBoxLayout(window)
    
    # Create signal button
    signal_button = create_database_signal_button(window, 30)
    layout.addWidget(signal_button)
    
    # Add status label
    status_label = QtWidgets.QLabel("Database Signal Status")
    status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(status_label)
    
    # Update status label when signal changes
    def update_status(signal_strength, icon_path):
        status_label.setText(f"Status: {signal_strength.title()}")
    
    signal_button.monitor.add_signal_callback(update_status)
    
    window.show()
    sys.exit(app.exec())
    sys.exit(app.exec())
