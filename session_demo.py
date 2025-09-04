#!/usr/bin/env python3
"""
Session Management Demo
Demonstrates the sliding session functionality
"""

import time
from session_manager import session_manager, create_session, validate_session, end_session, save_remember_me, load_remember_me, clear_remember_me, auto_login_from_remember

def demo_session_management():
    """Comprehensive demo of session management features"""
    print("=" * 60)
    print("SESSION MANAGEMENT DEMO")
    print("=" * 60)
    
    username = "demo_user"
    
    # Clean up any existing sessions
    print("\n1. Cleaning up expired sessions...")
    cleaned = session_manager.cleanup_expired_sessions()
    print(f"   Cleaned up {cleaned} expired sessions")
    
    # Create a session
    print(f"\n2. Creating session for '{username}'...")
    token = create_session(username, 3600)  # 1 hour
    print(f"   Token: {token[:16]}...")
    
    # Validate session (should extend expiry)
    print(f"\n3. Validating session for '{username}'...")
    if validate_session(username, token):
        print("   ✅ Session validated and extended")
    else:
        print("   ❌ Session validation failed")
    
    # Get session info
    print(f"\n4. Getting session info for '{username}'...")
    session_info = session_manager.get_session_info(username)
    if session_info:
        print(f"   Expiry: {session_info['expiry']}")
        print(f"   Created: {session_info['created']}")
        print(f"   Time until expiry: {session_info['expiry'] - int(time.time())} seconds")
    
    # Save remember me
    print(f"\n5. Saving remember me for '{username}'...")
    if save_remember_me(username, token):
        print("   ✅ Remember me data saved")
    else:
        print("   ❌ Failed to save remember me data")
    
    # Load remember me
    print(f"\n6. Loading remember me data...")
    remember_data = load_remember_me()
    if remember_data:
        user, tok = remember_data
        print(f"   Username: {user}")
        print(f"   Token: {tok[:16]}...")
    else:
        print("   No remember me data found")
    
    # Test auto-login
    print(f"\n7. Testing auto-login...")
    auto_user = auto_login_from_remember()
    if auto_user:
        print(f"   ✅ Auto-login successful for '{auto_user}'")
    else:
        print("   ❌ Auto-login failed")
    
    # Validate session again (should extend again)
    print(f"\n8. Validating session again (sliding expiration)...")
    if validate_session(username, token):
        print("   ✅ Session validated and extended again")
        session_info = session_manager.get_session_info(username)
        if session_info:
            print(f"   New expiry: {session_info['expiry']}")
            print(f"   Time until expiry: {session_info['expiry'] - int(time.time())} seconds")
    else:
        print("   ❌ Session validation failed")
    
    # Test invalid token
    print(f"\n9. Testing invalid token...")
    fake_token = "invalid_token_12345"
    if not validate_session(username, fake_token):
        print("   ✅ Invalid token correctly rejected")
    else:
        print("   ❌ Invalid token incorrectly accepted")
    
    # Test invalid user
    print(f"\n10. Testing invalid user...")
    if not validate_session("nonexistent_user", token):
        print("   ✅ Invalid user correctly rejected")
    else:
        print("   ❌ Invalid user incorrectly accepted")
    
    # End session
    print(f"\n11. Ending session for '{username}'...")
    if end_session(username):
        print("   ✅ Session ended successfully")
    else:
        print("   ❌ Failed to end session")
    
    # Test validation after ending
    print(f"\n12. Testing validation after session ended...")
    if not validate_session(username, token):
        print("   ✅ Session correctly invalidated")
    else:
        print("   ❌ Session still valid after ending")
    
    # Test auto-login after session ended
    print(f"\n13. Testing auto-login after session ended...")
    auto_user = auto_login_from_remember()
    if auto_user:
        print(f"   ❌ Auto-login should have failed")
    else:
        print("   ✅ Auto-login correctly failed")
    
    # Clear remember me
    print(f"\n14. Clearing remember me data...")
    if clear_remember_me():
        print("   ✅ Remember me data cleared")
    else:
        print("   ❌ Failed to clear remember me data")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)

def demo_expired_session():
    """Demo handling of expired sessions"""
    print("\n" + "=" * 60)
    print("EXPIRED SESSION DEMO")
    print("=" * 60)
    
    username = "expired_user"
    
    # Create a session with very short duration
    print(f"\n1. Creating short-lived session for '{username}'...")
    token = create_session(username, 2)  # 2 seconds
    print(f"   Token: {token[:16]}...")
    
    # Validate immediately
    print(f"\n2. Validating session immediately...")
    if validate_session(username, token):
        print("   ✅ Session valid")
    else:
        print("   ❌ Session invalid")
    
    # Wait for expiration
    print(f"\n3. Waiting for session to expire (3 seconds)...")
    time.sleep(3)
    
    # Try to validate expired session
    print(f"\n4. Validating expired session...")
    if not validate_session(username, token):
        print("   ✅ Expired session correctly rejected")
    else:
        print("   ❌ Expired session incorrectly accepted")
    
    # Check if session was cleaned up
    print(f"\n5. Checking if expired session was cleaned up...")
    session_info = session_manager.get_session_info(username)
    if not session_info:
        print("   ✅ Expired session was cleaned up")
    else:
        print("   ❌ Expired session still exists")
    
    print("\n" + "=" * 60)
    print("EXPIRED SESSION DEMO COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    demo_session_management()
    demo_expired_session()
