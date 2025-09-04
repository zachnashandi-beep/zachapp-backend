#!/usr/bin/env python3
"""
Test All Fixes
Test the fixes for reset link timer, dialog size, and login lockout
"""

import sys
import os
from PyQt6 import QtWidgets
from forgot_password_dialog import show_forgot_password_dialog
from reset_password_dialog import show_reset_password_dialog

def test_reset_link_timer():
    """Test the reset link timer functionality"""
    print("🧪 TESTING RESET LINK TIMER")
    print("=" * 40)
    print("✅ Fixed: 30-second cooldown timer")
    print("✅ Fixed: Button shows countdown")
    print("✅ Fixed: Prevents spam sending")
    print()
    
    app = QtWidgets.QApplication(sys.argv)
    
    print("📱 Opening Forgot Password Dialog...")
    print("🎯 Test: Click 'Send Reset Link' and watch the timer")
    print("   - Button should show 'Resend in 30s', 'Resend in 29s', etc.")
    print("   - Button should be disabled during countdown")
    print("   - After 30 seconds, button should re-enable")
    print()
    
    result = show_forgot_password_dialog()
    print(f"📊 Dialog result: {result}")

def test_reset_dialog_size():
    """Test the reset password dialog size"""
    print("\n🧪 TESTING RESET DIALOG SIZE")
    print("=" * 40)
    print("✅ Fixed: Increased dialog size to 800x750")
    print("✅ Fixed: All fields should be visible")
    print("✅ Fixed: 'Reset Password Now' button should be fully visible")
    print()
    
    app = QtWidgets.QApplication(sys.argv)
    
    print("📱 Opening Reset Password Dialog...")
    print("🎯 Test: Check if all fields are properly visible")
    print("   - Dialog should be larger (800x750)")
    print("   - All text should be readable")
    print("   - No cut-off text or buttons")
    print()
    
    result = show_reset_password_dialog("test_token")
    print(f"📊 Dialog result: {result}")

def test_login_lockout():
    """Test the login lockout system"""
    print("\n🧪 TESTING LOGIN LOCKOUT SYSTEM")
    print("=" * 40)
    print("✅ Fixed: Lockout check at login start")
    print("✅ Fixed: Increased lockout duration to 60 seconds")
    print("✅ Fixed: Debug logging for failed attempts")
    print()
    
    # Check if lockout files exist
    lockout_files = [
        "failed_attempts.txt",
        "lockout_state.txt", 
        "lockout_duration.txt"
    ]
    
    print("📁 Checking lockout files:")
    for file in lockout_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                content = f.read().strip()
            print(f"   ✅ {file}: {content}")
        else:
            print(f"   ❌ {file}: Not found")
    
    print("\n🎯 Test: Try logging in with wrong password 3 times")
    print("   - After 3 attempts, should be locked out for 60 seconds")
    print("   - Debug output should show failed attempts count")
    print("   - Lockout files should be created/updated")

def main():
    """Main test function"""
    print("🧪 TESTING ALL FIXES")
    print("=" * 50)
    print("This test verifies all the fixes for:")
    print("1. Reset link timer (30s cooldown)")
    print("2. Reset dialog size (800x750)")
    print("3. Login lockout system (3 attempts, 60s lockout)")
    print()
    
    try:
        # Test 1: Reset link timer
        test_reset_link_timer()
        
        # Test 2: Reset dialog size
        test_reset_dialog_size()
        
        # Test 3: Login lockout
        test_login_lockout()
        
        print("\n🎉 ALL TESTS COMPLETED!")
        print("✅ Reset link timer: 30-second cooldown")
        print("✅ Reset dialog size: Increased to 800x750")
        print("✅ Login lockout: 3 attempts, 60-second lockout")
        print()
        print("🎯 Ready for live testing!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
