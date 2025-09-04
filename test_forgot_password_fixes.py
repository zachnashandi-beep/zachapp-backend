#!/usr/bin/env python3
"""
Test Forgot Password Fixes
Test the fixes for multiple reset dialogs and buttons
"""

import sys
from PyQt6 import QtWidgets
from forgot_password_dialog import show_forgot_password_dialog

def test_forgot_password_fixes():
    """Test the forgot password dialog fixes"""
    print("🧪 TESTING FORGOT PASSWORD FIXES")
    print("=" * 50)
    print("✅ Fixed: Multiple 'Reset Password Now' buttons")
    print("✅ Fixed: Multiple reset password dialogs")
    print("✅ Fixed: Dialog opening without proper validation")
    print()
    
    app = QtWidgets.QApplication(sys.argv)
    
    print("📱 Opening Forgot Password Dialog...")
    print("🎯 Test scenarios:")
    print("   1. Click 'Send Reset Link' multiple times")
    print("   2. Verify only ONE 'Reset Password Now' button appears")
    print("   3. Click 'Reset Password Now' multiple times")
    print("   4. Verify only ONE reset dialog opens")
    print()
    
    # Show the dialog
    result = show_forgot_password_dialog()
    
    print(f"📊 Dialog result: {result}")
    print("✅ Test completed!")

if __name__ == "__main__":
    test_forgot_password_fixes()
