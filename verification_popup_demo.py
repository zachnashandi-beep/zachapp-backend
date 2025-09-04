#!/usr/bin/env python3
"""
Verification Popup Demo
Demonstrate the verification popup with countdown functionality
"""

import sys
import os
from PyQt6 import QtWidgets
from verification_popup import VerificationPopup

def demo_verification_popup():
    """Demo the verification popup with countdown"""
    print("=" * 70)
    print("VERIFICATION POPUP DEMO")
    print("=" * 70)
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Create a test user first
    test_username = "fxquadratics"
    test_email = "fxquadratics@example.com"
    
    print(f"📱 Opening verification popup for user: {test_username}")
    print(f"📧 Email: {test_email}")
    print()
    print("🎯 Features to test:")
    print("   ✅ Click 'Yes, Send Email' to send verification")
    print("   ✅ Watch the anti-spam countdown timer")
    print("   ✅ Click 'Resend Email' after countdown finishes")
    print("   ✅ Notice countdown increases significantly with each resend")
    print("   ✅ Real email service integration (with fallback)")
    print()
    print("🛡️ Anti-spam countdown progression:")
    print("   • Resend #1: 30 seconds")
    print("   • Resend #2: 1 minute")
    print("   • Resend #3: 5 minutes")
    print("   • Resend #4+: 10 minutes")
    print()
    print("💡 The popup will show:")
    print("   - Initial send button")
    print("   - Success message with countdown")
    print("   - Resend button (disabled during countdown)")
    print("   - Countdown timer with anti-spam protection")
    print()
    
    # Create and show the popup
    popup = VerificationPopup(None, test_username, test_email)
    
    # Center the popup on screen
    screen = app.primaryScreen().geometry()
    popup.move(
        (screen.width() - popup.width()) // 2,
        (screen.height() - popup.height()) // 2
    )
    
    result = popup.exec()
    
    if result == QtWidgets.QDialog.DialogCode.Accepted:
        verification_sent = popup.get_verification_sent()
        print(f"✅ Popup result: Email {'sent' if verification_sent else 'not sent'}")
    else:
        print("❌ Popup cancelled")
    
    print("\n🎉 Demo completed!")
    return result

def main():
    """Main demo function"""
    print("VERIFICATION POPUP WITH COUNTDOWN DEMO")
    print("=" * 70)
    
    try:
        result = demo_verification_popup()
        
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            print("\n✅ Demo successful!")
            print("🎯 The verification popup now includes:")
            print("   • Real email service integration")
            print("   • Anti-spam countdown timer (30s → 1m → 5m → 10m)")
            print("   • Resend button with significant delays")
            print("   • Case-insensitive username lookup")
            print("   • Modern, responsive UI")
        else:
            print("\n⚠️ Demo cancelled by user")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
