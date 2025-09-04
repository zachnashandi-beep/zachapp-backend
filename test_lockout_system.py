#!/usr/bin/env python3
"""
Test Lockout System
Test the login lockout system to ensure it works properly
"""

import os
import time
import sys
from PyQt6 import QtWidgets, QtCore

# Import the lockout functions from main.py
sys.path.append(os.path.dirname(__file__))

# Define the constants and functions from main.py
FAILED_ATTEMPTS_LIMIT = 3
FAILED_ATTEMPTS_FILE = "failed_attempts.txt"
LOCKOUT_FILE = "lockout_state.txt"
LOCKOUT_DURATION_FILE = "lockout_duration.txt"
DEFAULT_LOCKOUT_DURATION = 60

def load_failed_attempts() -> int:
    if os.path.exists(FAILED_ATTEMPTS_FILE):
        try:
            return int(open(FAILED_ATTEMPTS_FILE).read())
        except Exception:
            return 0
    return 0

def save_failed_attempts(value: int) -> None:
    with open(FAILED_ATTEMPTS_FILE, "w") as f:
        f.write(str(value))

def get_lockout_duration() -> int:
    if os.path.exists(LOCKOUT_DURATION_FILE):
        try:
            return int(open(LOCKOUT_DURATION_FILE).read())
        except Exception:
            pass
    return DEFAULT_LOCKOUT_DURATION

def set_lockout_duration(duration: int) -> None:
    with open(LOCKOUT_DURATION_FILE, "w") as f:
        f.write(str(duration))

def save_lockout() -> None:
    with open(LOCKOUT_FILE, "w") as f:
        f.write(str(int(time.time())))

def clear_lockout() -> None:
    if os.path.exists(LOCKOUT_FILE):
        os.remove(LOCKOUT_FILE)

def is_locked_out():
    if not os.path.exists(LOCKOUT_FILE):
        return False
    with open(LOCKOUT_FILE, "r") as f:
        lock_time = int(f.read())
    duration = get_lockout_duration()
    elapsed = time.time() - lock_time
    if elapsed < duration:
        return duration - elapsed
    clear_lockout()
    return False

def format_time(seconds: float) -> str:
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    if remaining_seconds == 0:
        return f"{minutes}m"
    return f"{minutes}m {remaining_seconds}s"

def test_lockout_system():
    """Test the lockout system"""
    print("🧪 TESTING LOCKOUT SYSTEM")
    print("=" * 50)
    
    # Clear any existing lockout state
    clear_lockout()
    save_failed_attempts(0)
    
    print("1️⃣ Testing failed attempts tracking...")
    failed_attempts = load_failed_attempts()
    print(f"   Initial failed attempts: {failed_attempts}")
    
    # Simulate failed login attempts
    for i in range(1, 5):
        failed_attempts += 1
        save_failed_attempts(failed_attempts)
        attempts_left = FAILED_ATTEMPTS_LIMIT - failed_attempts
        
        print(f"   Attempt {i}: Failed attempts = {failed_attempts}, Left = {attempts_left}")
        
        if failed_attempts >= FAILED_ATTEMPTS_LIMIT:
            print(f"   🚨 LOCKOUT TRIGGERED after {failed_attempts} attempts!")
            save_lockout()
            break
    
    print("\n2️⃣ Testing lockout state...")
    lockout_remaining = is_locked_out()
    if lockout_remaining:
        time_str = format_time(lockout_remaining)
        print(f"   ✅ Account is locked for {time_str}")
    else:
        print("   ❌ Account is not locked (this is wrong!)")
    
    print("\n3️⃣ Testing lockout files...")
    files_to_check = [
        (FAILED_ATTEMPTS_FILE, "Failed attempts"),
        (LOCKOUT_FILE, "Lockout state"),
        (LOCKOUT_DURATION_FILE, "Lockout duration")
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                content = f.read().strip()
            print(f"   ✅ {description}: {content}")
        else:
            print(f"   ❌ {description}: File not found")
    
    print("\n4️⃣ Testing lockout duration...")
    duration = get_lockout_duration()
    print(f"   Lockout duration: {duration} seconds ({format_time(duration)})")
    
    print("\n" + "=" * 50)
    print("🔍 Lockout system test complete!")
    
    if lockout_remaining:
        print(f"✅ System is working - account locked for {format_time(lockout_remaining)}")
    else:
        print("❌ System is broken - account should be locked")

def create_test_app():
    """Create a test app to simulate login attempts"""
    print("\n📱 CREATING TEST LOGIN APP")
    print("=" * 30)
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create test window
    window = QtWidgets.QWidget()
    window.setWindowTitle("Lockout System Test")
    window.setGeometry(100, 100, 400, 300)
    
    layout = QtWidgets.QVBoxLayout(window)
    
    # Title
    title = QtWidgets.QLabel("Lockout System Test")
    title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
    title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(title)
    
    # Status label
    status_label = QtWidgets.QLabel("Ready to test")
    status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(status_label)
    
    # Test button
    test_button = QtWidgets.QPushButton("Simulate Failed Login")
    test_button.clicked.connect(lambda: simulate_failed_login(status_label))
    layout.addWidget(test_button)
    
    # Reset button
    reset_button = QtWidgets.QPushButton("Reset Lockout State")
    reset_button.clicked.connect(lambda: reset_lockout_state(status_label))
    layout.addWidget(reset_button)
    
    # Update status
    update_status(status_label)
    
    window.show()
    return app.exec()

def simulate_failed_login(status_label):
    """Simulate a failed login attempt"""
    failed_attempts = load_failed_attempts() + 1
    save_failed_attempts(failed_attempts)
    attempts_left = FAILED_ATTEMPTS_LIMIT - failed_attempts
    
    if failed_attempts >= FAILED_ATTEMPTS_LIMIT:
        save_lockout()
        status_label.setText(f"🚨 LOCKED OUT! ({format_time(get_lockout_duration())})")
        status_label.setStyleSheet("color: red; font-weight: bold;")
    else:
        status_label.setText(f"Failed attempt {failed_attempts}/{FAILED_ATTEMPTS_LIMIT} (Left: {attempts_left})")
        status_label.setStyleSheet("color: orange; font-weight: bold;")

def reset_lockout_state(status_label):
    """Reset the lockout state"""
    clear_lockout()
    save_failed_attempts(0)
    update_status(status_label)

def update_status(status_label):
    """Update the status label"""
    failed_attempts = load_failed_attempts()
    lockout_remaining = is_locked_out()
    
    if lockout_remaining:
        status_label.setText(f"🔒 LOCKED for {format_time(lockout_remaining)}")
        status_label.setStyleSheet("color: red; font-weight: bold;")
    elif failed_attempts > 0:
        attempts_left = FAILED_ATTEMPTS_LIMIT - failed_attempts
        status_label.setText(f"Failed attempts: {failed_attempts}/{FAILED_ATTEMPTS_LIMIT} (Left: {attempts_left})")
        status_label.setStyleSheet("color: orange; font-weight: bold;")
    else:
        status_label.setText("✅ Ready - No failed attempts")
        status_label.setStyleSheet("color: green; font-weight: bold;")

def main():
    """Main test function"""
    print("LOCKOUT SYSTEM TESTER")
    print("=" * 50)
    print("This test verifies the login lockout system")
    print()
    
    try:
        # Test the lockout system
        test_lockout_system()
        
        # Ask if user wants to see interactive test
        print("\n🎮 Would you like to see the interactive test? (y/n)")
        response = input().lower().strip()
        if response in ['y', 'yes']:
            create_test_app()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
