#!/usr/bin/env python3
"""
Email Verification Demo
Demonstrates the complete email verification workflow
"""

import time
import json
import os
from email_verification import (
    verification_manager, 
    generate_verification_token, 
    verify_email, 
    is_verified, 
    resend_verification,
    send_verification_email_simulation,
    cleanup_expired_verifications
)

def demo_complete_workflow():
    """Demonstrate the complete email verification workflow"""
    print("=" * 70)
    print("COMPLETE EMAIL VERIFICATION WORKFLOW DEMO")
    print("=" * 70)
    
    username = "demo_user"
    email = "demo@example.com"
    
    # Clean up any existing verifications
    print("\n1. Cleaning up expired verifications...")
    cleaned = cleanup_expired_verifications()
    print(f"   Cleaned up {cleaned} expired verifications")
    
    # Simulate user signup
    print(f"\n2. Simulating user signup for '{username}'...")
    print(f"   Email: {email}")
    
    # Generate verification token
    print(f"\n3. Generating verification token...")
    token = generate_verification_token(username, 24)  # 24 hours
    print(f"   Token: {token[:16]}...")
    
    # Send verification email
    print(f"\n4. Sending verification email...")
    if send_verification_email_simulation(username, email, token):
        print("   ✅ Verification email sent (simulated)")
    else:
        print("   ❌ Failed to send verification email")
    
    # Check verification status (should be unverified)
    print(f"\n5. Checking verification status...")
    if is_verified(username):
        print("   ❌ User is verified (should not be)")
    else:
        print("   ✅ User is not verified (correct)")
    
    # Simulate login attempt (should be blocked)
    print(f"\n6. Simulating login attempt...")
    if is_verified(username):
        print("   ✅ Login would be allowed")
    else:
        print("   ❌ Login would be blocked (correct)")
    
    # Verify email with correct token
    print(f"\n7. Verifying email with correct token...")
    if verify_email(username, token):
        print("   ✅ Email verified successfully")
    else:
        print("   ❌ Email verification failed")
    
    # Check verification status (should be verified now)
    print(f"\n8. Checking verification status after verification...")
    if is_verified(username):
        print("   ✅ User is now verified (correct)")
    else:
        print("   ❌ User is still not verified (incorrect)")
    
    # Simulate login attempt (should be allowed now)
    print(f"\n9. Simulating login attempt after verification...")
    if is_verified(username):
        print("   ✅ Login would now be allowed (correct)")
    else:
        print("   ❌ Login would still be blocked (incorrect)")
    
    # Try to verify again (should still work)
    print(f"\n10. Trying to verify again...")
    if verify_email(username, token):
        print("   ✅ Already verified user can still verify")
    else:
        print("   ❌ Already verified user cannot verify again")
    
    print("\n" + "=" * 70)
    print("WORKFLOW DEMO COMPLETE")
    print("=" * 70)

def demo_error_cases():
    """Demonstrate error handling"""
    print("\n" + "=" * 70)
    print("ERROR HANDLING DEMO")
    print("=" * 70)
    
    username = "test_user"
    
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
    
    # Test resending verification
    print(f"\n3. Testing resend verification...")
    new_token = resend_verification(username, 24)
    print(f"   New token: {new_token[:16]}...")
    
    # Verify with new token
    print(f"\n4. Verifying with new token...")
    if verify_email(username, new_token):
        print("   ✅ New token verification successful")
    else:
        print("   ❌ New token verification failed")
    
    print("\n" + "=" * 70)
    print("ERROR HANDLING DEMO COMPLETE")
    print("=" * 70)

def demo_expired_tokens():
    """Demonstrate expired token handling"""
    print("\n" + "=" * 70)
    print("EXPIRED TOKEN DEMO")
    print("=" * 70)
    
    username = "expired_user"
    email = "expired@example.com"
    
    # Create a token with very short expiry
    print(f"\n1. Creating token with 2-second expiry...")
    token = generate_verification_token(username, 0.001)  # Very short expiry
    print(f"   Token: {token[:16]}...")
    
    # Verify immediately (should work)
    print(f"\n2. Verifying immediately...")
    if verify_email(username, token):
        print("   ✅ Immediate verification successful")
    else:
        print("   ❌ Immediate verification failed")
    
    # Wait for expiration
    print(f"\n3. Waiting for token to expire (3 seconds)...")
    time.sleep(3)
    
    # Try to verify expired token
    print(f"\n4. Trying to verify expired token...")
    if not verify_email(username, token):
        print("   ✅ Expired token correctly rejected")
    else:
        print("   ❌ Expired token incorrectly accepted")
    
    # Check if expired token was cleaned up
    print(f"\n5. Checking if expired token was cleaned up...")
    verification_info = verification_manager.get_verification_info(username)
    if not verification_info:
        print("   ✅ Expired token was cleaned up")
    else:
        print("   ❌ Expired token still exists")
    
    print("\n" + "=" * 70)
    print("EXPIRED TOKEN DEMO COMPLETE")
    print("=" * 70)

def demo_verification_file_structure():
    """Show the verification.json file structure"""
    print("\n" + "=" * 70)
    print("VERIFICATION FILE STRUCTURE")
    print("=" * 70)
    
    # Create a sample verification
    username = "sample_user"
    token = generate_verification_token(username, 24)
    
    # Show the file structure
    print(f"\n1. Created verification for '{username}'")
    print(f"   Token: {token[:16]}...")
    
    # Read and display the verification.json file
    try:
        with open("verification.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"\n2. verification.json file structure:")
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"   Error reading verification.json: {e}")
    
    print("\n" + "=" * 70)
    print("FILE STRUCTURE DEMO COMPLETE")
    print("=" * 70)

def demo_integration_with_users():
    """Demonstrate integration with users.json"""
    print("\n" + "=" * 70)
    print("INTEGRATION WITH USERS.JSON DEMO")
    print("=" * 70)
    
    # Check if users.json exists
    users_file = "users.json"
    if os.path.exists(users_file):
        print(f"\n1. Found {users_file}")
        
        try:
            with open(users_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            users = data.get("users", {})
            print(f"   Found {len(users)} users in database")
            
            # Check verification status for each user
            for username in users.keys():
                if is_verified(username):
                    print(f"   ✅ {username}: verified")
                else:
                    print(f"   ❌ {username}: not verified")
                    
        except Exception as e:
            print(f"   Error reading users.json: {e}")
    else:
        print(f"\n1. {users_file} not found")
        print("   Creating sample user for demo...")
        
        # Create a sample user
        sample_user = {
            "users": {
                "demo_user": {
                    "password": "hashed_password_here",
                    "email": "demo@example.com"
                }
            }
        }
        
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(sample_user, f, indent=2)
        
        print("   ✅ Sample user created")
    
    print("\n" + "=" * 70)
    print("INTEGRATION DEMO COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    demo_complete_workflow()
    demo_error_cases()
    demo_expired_tokens()
    demo_verification_file_structure()
    demo_integration_with_users()
    
    print("\n" + "=" * 70)
    print("ALL DEMOS COMPLETE")
    print("=" * 70)
    print("\nTo test the verification system:")
    print("1. Run the main application: python main.py")
    print("2. Create a new account (signup)")
    print("3. Check the console for the verification email simulation")
    print("4. Use the 'Verify Email' button to verify your account")
    print("5. Try logging in before and after verification")
    print("=" * 70)
