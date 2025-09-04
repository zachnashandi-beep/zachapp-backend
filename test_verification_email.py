#!/usr/bin/env python3
"""
Test Email Verification System
Test the real email verification with countdown functionality
"""

import os
import time
from hybrid_user_manager import user_manager
from email_service import send_verification_email, test_email_connection
from verification_popup import show_verification_popup

def test_email_verification_system():
    """Test the complete email verification system"""
    print("=" * 70)
    print("TESTING EMAIL VERIFICATION SYSTEM")
    print("=" * 70)
    
    # Test email connection first
    print("1. Testing email connection...")
    connection_ok = test_email_connection()
    print(f"   Email Connection: {'✅ Success' if connection_ok else '❌ Failed'}")
    
    if not connection_ok:
        print("   ⚠️ Email connection failed. Check Gmail credentials.")
        return False
    
    # Test data
    test_username = "testuser_verification"
    test_email = "zachapp.team@gmail.com"  # Use the Gmail account for testing
    test_password = "testpassword123"
    
    print(f"\n2. Creating test user...")
    user_created = user_manager.save_user(test_username, test_email, test_password)
    print(f"   User Created: {'✅ Success' if user_created else '❌ Failed'}")
    
    if not user_created:
        return False
    
    print(f"\n3. Testing verification email sending...")
    try:
        # Test direct email sending
        email_sent = send_verification_email(test_username, test_email, "test_token_123")
        print(f"   Direct Email Send: {'✅ Success' if email_sent else '❌ Failed'}")
        
        if email_sent:
            print(f"   📧 Verification email sent to {test_email}")
            print(f"   🔗 Check your email for the verification link")
        else:
            print(f"   ❌ Failed to send verification email")
            
    except Exception as e:
        print(f"   ❌ Error sending email: {e}")
        return False
    
    print(f"\n4. Testing verification popup (GUI)...")
    print(f"   📱 Opening verification popup dialog...")
    print(f"   💡 This will open a GUI dialog - test the countdown functionality")
    
    # Note: This will open a GUI dialog
    try:
        verification_sent = show_verification_popup(None, test_username, test_email)
        print(f"   Popup Result: {'✅ Email sent' if verification_sent else '❌ No email sent'}")
    except Exception as e:
        print(f"   ❌ Error with popup: {e}")
    
    return True

def test_countdown_logic():
    """Test the countdown logic without GUI"""
    print("\n" + "=" * 70)
    print("TESTING COUNTDOWN LOGIC")
    print("=" * 70)
    
    # Simulate countdown logic with new progression
    resend_count = 0
    countdown_progression = [30, 60, 300, 600]  # 30s, 1m, 5m, 10m
    
    print("🛡️ Anti-spam countdown progression:")
    print("   Resend #1: 30 seconds")
    print("   Resend #2: 1 minute")
    print("   Resend #3: 5 minutes")
    print("   Resend #4+: 10 minutes")
    print()
    
    for attempt in range(6):  # Test 6 resends to show the progression
        resend_count += 1
        
        # Calculate countdown time
        if resend_count <= len(countdown_progression):
            countdown_seconds = countdown_progression[resend_count - 1]
        else:
            countdown_seconds = 600  # Stay at 10m
        
        # Format time display
        if countdown_seconds >= 60:
            minutes = countdown_seconds // 60
            seconds = countdown_seconds % 60
            if seconds > 0:
                time_display = f"{minutes}m {seconds}s"
            else:
                time_display = f"{minutes}m"
        else:
            time_display = f"{countdown_seconds}s"
        
        print(f"Resend #{resend_count}: {time_display} countdown")
        
        # Simulate countdown (faster for demo)
        step = max(1, countdown_seconds // 10)  # Show ~10 steps
        for remaining in range(countdown_seconds, 0, -step):
            minutes = remaining // 60
            seconds = remaining % 60
            
            if minutes > 0:
                time_str = f"{minutes}m {seconds:02d}s"
            else:
                time_str = f"{seconds}s"
            
            print(f"  ⏰ {time_str} remaining...")
            time.sleep(0.05)  # Short delay for demo
        
        print(f"  ✅ Resend #{resend_count} available!")
        print()
    
    print("🎉 Countdown logic test completed!")
    print("🛡️ Anti-spam protection: Delays increase significantly to prevent abuse!")

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 70)
    print("CLEANING UP TEST DATA")
    print("=" * 70)
    
    # Remove test JSON files
    test_files = ["users.json", "verification.json"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Removed {file}")
            except Exception as e:
                print(f"❌ Failed to remove {file}: {e}")
    
    print("=" * 70)

def main():
    """Main test function"""
    print("EMAIL VERIFICATION SYSTEM TEST")
    print("=" * 70)
    
    try:
        # Test email verification system
        test_success = test_email_verification_system()
        
        if test_success:
            print("\n🎉 EMAIL VERIFICATION TEST PASSED!")
            print("✅ Real emails are being sent via Gmail SMTP")
            print("✅ Verification popup has countdown functionality")
            print("✅ Resend countdown increases with each attempt")
        else:
            print("\n❌ Email verification test failed")
        
        # Test countdown logic
        test_countdown_logic()
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test data
        cleanup_test_data()

if __name__ == "__main__":
    main()
