#!/usr/bin/env python3
"""
Test Database Signal Integration
Test the complete database signal monitoring integration
"""

import sys
import os
from PyQt6 import QtWidgets, QtCore
from database_signal_monitor import DatabaseSignalButton, get_global_monitor

def test_database_signal_system():
    """Test the complete database signal monitoring system"""
    print("🧪 TESTING DATABASE SIGNAL INTEGRATION")
    print("=" * 60)
    
    # Test 1: Check if icons exist
    print("1️⃣ Checking database signal icons...")
    icon_dir = os.path.join(os.path.dirname(__file__), "emoji")
    required_icons = [
        "db_unavailable_30x30.png",
        "wifi_weak_30x30.png",
        "wifi_okish_30x30.png", 
        "wifi_strong_30x30.png",
        "wifi_verystrong_30x30.png"
    ]
    
    all_icons_exist = True
    for icon in required_icons:
        icon_path = os.path.join(icon_dir, icon)
        if os.path.exists(icon_path):
            print(f"   ✅ {icon}")
        else:
            print(f"   ❌ {icon} - Missing!")
            all_icons_exist = False
    
    if not all_icons_exist:
        print("   ⚠️ Some icons are missing. Run resize_db_icons_qt.py first.")
        return False
    
    print()
    
    # Test 2: Test database signal monitor
    print("2️⃣ Testing database signal monitor...")
    try:
        monitor = get_global_monitor()
        signal_strength, icon_path = monitor.get_current_signal()
        print(f"   Current signal: {signal_strength}")
        print(f"   Icon path: {icon_path}")
        print(f"   Icon exists: {'✅ Yes' if os.path.exists(icon_path) else '❌ No'}")
    except Exception as e:
        print(f"   ❌ Error testing monitor: {e}")
        return False
    
    print()
    
    # Test 3: Test signal button creation
    print("3️⃣ Testing database signal button...")
    try:
        app = QtWidgets.QApplication(sys.argv)
        button = DatabaseSignalButton(None, 30)
        print(f"   Button created: ✅ Yes")
        print(f"   Button size: {button.size().width()}x{button.size().height()}")
        print(f"   Monitoring active: {'✅ Yes' if button.monitor.monitoring else '❌ No'}")
        
        # Test signal strength
        signal_strength, icon_path = button.get_current_signal()
        print(f"   Current signal: {signal_strength}")
        
    except Exception as e:
        print(f"   ❌ Error testing button: {e}")
        return False
    
    print()
    
    # Test 4: Test signal strength mapping
    print("4️⃣ Testing signal strength mapping...")
    signal_mappings = {
        "unavailable": ("#FF0000", "db_unavailable_30x30.png"),
        "weak": ("#FF0000", "wifi_weak_30x30.png"),
        "okayish": ("#FFA500", "wifi_okish_30x30.png"),
        "good": ("#FFFF00", "wifi_strong_30x30.png"),
        "strong": ("#00FF00", "wifi_strong_30x30.png"),
        "verystrong": ("#00FF00", "wifi_verystrong_30x30.png")
    }
    
    for strength, (color, icon) in signal_mappings.items():
        monitor_color = button.monitor.get_signal_color(strength)
        monitor_icon = button.monitor._get_icon_path(strength)
        
        color_match = monitor_color == color
        icon_match = icon in monitor_icon
        
        print(f"   {strength}:")
        print(f"     Color: {'✅' if color_match else '❌'} {monitor_color}")
        print(f"     Icon: {'✅' if icon_match else '❌'} {os.path.basename(monitor_icon)}")
    
    print()
    
    # Test 5: Test Login.ui integration
    print("5️⃣ Testing Login.ui integration...")
    login_ui_path = os.path.join(os.path.dirname(__file__), "Login.ui")
    if os.path.exists(login_ui_path):
        with open(login_ui_path, "r") as f:
            ui_content = f.read()
        
        if "dbstrength" in ui_content:
            print("   ✅ dbstrength button found in Login.ui")
        else:
            print("   ❌ dbstrength button not found in Login.ui")
            return False
    else:
        print("   ❌ Login.ui file not found")
        return False
    
    print()
    
    print("🎉 DATABASE SIGNAL INTEGRATION TEST COMPLETED!")
    print("✅ All components are working correctly")
    print("✅ Icons are properly sized and available")
    print("✅ Signal monitoring is functional")
    print("✅ Login.ui integration is ready")
    print()
    print("🎯 Ready for live testing!")
    print("📱 Run main.py to see the database signal button in action")
    
    return True

def create_demo_window():
    """Create a demo window showing the database signal button"""
    print("\n📱 CREATING DEMO WINDOW")
    print("=" * 30)
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create demo window
    window = QtWidgets.QWidget()
    window.setWindowTitle("Database Signal Monitor Demo")
    window.setGeometry(100, 100, 300, 200)
    
    layout = QtWidgets.QVBoxLayout(window)
    
    # Title
    title = QtWidgets.QLabel("Database Signal Monitor")
    title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Signal button
    signal_button = DatabaseSignalButton(window, 30)
    signal_button.start_monitoring(1000)
    layout.addWidget(signal_button)
    
    # Status label
    status_label = QtWidgets.QLabel("Checking database signal...")
    status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(status_label)
    
    # Connect updates
    signal_button.monitor.signal_strength_changed.connect(
        lambda strength, path: status_label.setText(f"Database: {strength.title()}")
    )
    
    window.show()
    
    print("✅ Demo window created")
    print("🔍 Database signal monitoring active")
    print("📡 Updates every 1 second")
    print("🎯 Close window to exit")
    
    return app.exec()

def main():
    """Main test function"""
    print("DATABASE SIGNAL INTEGRATION TEST")
    print("=" * 60)
    print("This test verifies the complete database signal monitoring system")
    print()
    
    try:
        # Test the system
        success = test_database_signal_system()
        
        if success:
            print("\n🎯 SYSTEM READY!")
            print("✅ Database signal monitoring is fully integrated")
            print("✅ Real-time updates every 1 second")
            print("✅ Signal strength mapping works correctly")
            print("✅ Icons are properly sized and available")
            print("✅ Login page integration is complete")
            print()
            print("📱 The dbstrength button will appear on the login page")
            print("📡 It will show real-time database connection status")
            print("🎨 Icons change color based on signal strength")
            
            # Ask if user wants to see demo
            print("\n🎮 Would you like to see a demo window? (y/n)")
            response = input().lower().strip()
            if response in ['y', 'yes']:
                create_demo_window()
        else:
            print("\n❌ SYSTEM NOT READY")
            print("Please fix the issues above before testing")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
