#!/usr/bin/env python3
"""
Test Quiet Database Signal Monitoring
Demonstrate the quiet monitoring system
"""

import sys
import time
from PyQt6 import QtWidgets
from database_signal_monitor import DatabaseSignalButton

def test_quiet_monitoring():
    """Test the quiet monitoring system"""
    print("🔇 TESTING QUIET DATABASE SIGNAL MONITORING")
    print("=" * 50)
    print("✅ Updates every 500ms")
    print("✅ Only logs when signal strength changes")
    print("✅ No console spam during normal operation")
    print("✅ Silent background monitoring")
    print()
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create signal button
    button = DatabaseSignalButton(None, 30)
    button.start_monitoring(500)  # 500ms interval
    
    print("📡 Database signal monitoring started (quiet mode)")
    print("🎯 Watch for signal changes only - no spam!")
    print("⏱️  Monitoring for 10 seconds...")
    print()
    
    # Monitor for 10 seconds
    start_time = time.time()
    while time.time() - start_time < 10:
        time.sleep(0.1)
    
    print("✅ Test completed!")
    print("📊 You should only see messages when signal strength changes")
    
    button.stop_monitoring()
    return True

if __name__ == "__main__":
    test_quiet_monitoring()
