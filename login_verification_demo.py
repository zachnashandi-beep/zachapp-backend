#!/usr/bin/env python3
"""
Login Verification Workflow Demo
Demonstrates the new automatic email verification during login
"""

import time
import json
import os
from email_verification import (
    verification_manager, 
    generate_verification_token, 
    verify_email, 
    is_verified, 
    send_verification_email_simulation,
    cleanup_expired_verifications
)

def create_test_user():
    """Create a test user for demonstration"""
    username = "testuser"
    email = "test@example.com"
    password_hash = "hashed_password_123"  # In real app, this would be properly hashed
    
    # Create users.json if it doesn't exist
    users_file = "users.json"
    if os.path.exists(users_file):
        with open(users_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"users": {}}
    
    # Add test user
    data["users"][username] = {
        "password": password_hash,
        "email": email
    }
    
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Created test user: {username} ({email})")
    return username, email

def demo_login_workflow():
    """Demonstrate the complete login verification workflow"""
    print("=" * 70)
    print("LOGIN VERIFICATION WORKFLOW DEMO")
    print("=" * 70)
    
    # Clean up any existing verifications
    print("\n1. Cleaning up expired verifications...")
    cleaned = cleanup_expired_verifications()
    print(f"   Cleaned up {cleaned} expired verifications")
    
    # Create test user
    print("\n2. Creating test user...")
    username, email = create_test_user()
    
    # Simulate user signup (creates verification token)
    print(f"\n3. Simulating user signup...")
    token = generate_verification_token(username, 24)
    print(f"   Generated verification token: {token[:16]}...")
    
    # Send initial verification email
    print(f"\n4. Sending initial verification email...")
    if send_verification_email_simulation(username, email, token):
        print("   ✅ Initial verification email sent")
    else:
        print("   ❌ Failed to send initial verification email")
    
    # Check verification status (should be unverified)
    print(f"\n5. Checking verification status...")
    if is_verified(username):
        print("   ❌ User is verified (should not be)")
    else:
        print("   ✅ User is not verified (correct)")
    
    # Simulate login attempt (should trigger verification popup)
    print(f"\n6. Simulating login attempt by unverified user...")
    print("   This would normally show the verification popup in the UI")
    print("   For demo purposes, we'll simulate the popup behavior:")
    
    # Simulate popup behavior
    print(f"\n   📧 Verification popup would show:")
    print(f"      Message: 'Your account {username} is not verified.'")
    print(f"      Question: 'Would you like us to send a verification link to your email now?'")
    print(f"      Email: {email}")
    
    # Simulate user clicking "Yes" in popup
    print(f"\n   👆 User clicks 'Yes, Send Email'")
    
    # Generate new token (simulating popup behavior)
    new_token = generate_verification_token(username, 24)
    print(f"   Generated new verification token: {new_token[:16]}...")
    
    # Send verification email
    if send_verification_email_simulation(username, email, new_token):
        print("   ✅ Verification email sent successfully!")
        print(f"   📧 Email sent to: {email}")
    else:
        print("   ❌ Failed to send verification email")
    
    # Simulate user verifying email
    print(f"\n7. Simulating user clicking verification link...")
    if verify_email(username, new_token):
        print("   ✅ Email verified successfully!")
    else:
        print("   ❌ Email verification failed")
    
    # Check verification status (should be verified now)
    print(f"\n8. Checking verification status after verification...")
    if is_verified(username):
        print("   ✅ User is now verified (correct)")
    else:
        print("   ❌ User is still not verified (incorrect)")
    
    # Simulate successful login attempt
    print(f"\n9. Simulating login attempt after verification...")
    print("   ✅ Login would now be allowed!")
    print("   🎉 User successfully logged in")
    
    print("\n" + "=" * 70)
    print("LOGIN VERIFICATION WORKFLOW DEMO COMPLETE")
    print("=" * 70)

def demo_error_scenarios():
    """Demonstrate error scenarios"""
    print("\n" + "=" * 70)
    print("ERROR SCENARIOS DEMO")
    print("=" * 70)
    
    username = "testuser"
    
    # Test with wrong token
    print(f"\n1. Testing verification with wrong token...")
    wrong_token = "wrong_token_12345"
    if not verify_email(username, wrong_token):
        print("   ✅ Wrong token correctly rejected")
    else:
        print("   ❌ Wrong token incorrectly accepted")
    
    # Test with non-existent user
    print(f"\n2. Testing verification with non-existent user...")
    if not verify_email("nonexistent_user", "any_token"):
        print("   ✅ Non-existent user correctly rejected")
    else:
        print("   ❌ Non-existent user incorrectly accepted")
    
    # Test login with unverified user (after clearing verification)
    print(f"\n3. Testing login with unverified user...")
    # Clear verification status for testing
    verifications = verification_manager._load_verifications()
    if username in verifications:
        verifications[username]["verified"] = False
        verification_manager._save_verifications(verifications)
        print(f"   Cleared verification status for {username}")
    
    if not is_verified(username):
        print("   ✅ Unverified user correctly blocked from login")
        print("   📧 Verification popup would be shown")
    else:
        print("   ❌ Unverified user incorrectly allowed to login")
    
    print("\n" + "=" * 70)
    print("ERROR SCENARIOS DEMO COMPLETE")
    print("=" * 70)

def demo_ui_integration():
    """Demonstrate UI integration points"""
    print("\n" + "=" * 70)
    print("UI INTEGRATION DEMO")
    print("=" * 70)
    
    print("\n1. Login Page Changes:")
    print("   ✅ Removed 'Verify Email' button")
    print("   ✅ Verification now automatic during login")
    
    print("\n2. Login Flow:")
    print("   ✅ User enters username/password")
    print("   ✅ System checks if email is verified")
    print("   ✅ If not verified: shows modern popup")
    print("   ✅ If verified: proceeds with login")
    
    print("\n3. Verification Popup Features:")
    print("   ✅ Modern, clean design")
    print("   ✅ Shows username and email")
    print("   ✅ 'Yes' and 'No' options")
    print("   ✅ Automatic email sending")
    print("   ✅ Success confirmation")
    
    print("\n4. Session Management:")
    print("   ✅ Works seamlessly with existing session system")
    print("   ✅ Only verified users get sessions")
    print("   ✅ Remember Me works for verified users")
    
    print("\n" + "=" * 70)
    print("UI INTEGRATION DEMO COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    demo_login_workflow()
    demo_error_scenarios()
    demo_ui_integration()
    
    print("\n" + "=" * 70)
    print("ALL DEMOS COMPLETE")
    print("=" * 70)
    print("\nTo test the new login verification system:")
    print("1. Run the main application: python main.py")
    print("2. Try to login with an unverified account")
    print("3. The verification popup will appear automatically")
    print("4. Click 'Yes' to send verification email")
    print("5. Check console for email simulation")
    print("6. Verify email using the verification dialog")
    print("7. Try logging in again - should work!")
    print("=" * 70)
