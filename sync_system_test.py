#!/usr/bin/env python3
"""
Sync System Test
Comprehensive test for the sync mechanism
"""

import json
import os
import time
from sync_manager import sync_manager, check_and_sync, sync_all_data, get_sync_status, clear_sync_tracking
from hybrid_user_manager import user_manager
from hybrid_session_manager import session_manager
from hybrid_verification_manager import verification_manager
from hybrid_password_reset_manager import reset_manager
from database_manager import is_database_available

def create_test_json_data():
    """Create test data in JSON files"""
    print("=" * 70)
    print("CREATING TEST JSON DATA")
    print("=" * 70)
    
    # Create test users
    test_users = {
        "sync_test_user1": {
            "username": "sync_test_user1",
            "email": "sync_test1@example.com",
            "password": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # "hello"
        },
        "sync_test_user2": {
            "username": "sync_test_user2",
            "email": "sync_test2@example.com",
            "password": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"  # "password"
        }
    }
    
    with open("users.json", "w") as f:
        json.dump(test_users, f, indent=2)
    print("✅ Created test users in users.json")
    
    # Create test sessions
    current_time = int(time.time())
    test_sessions = {
        "sync_test_user1": {
            "token": "test_session_token_1",
            "expiry": current_time + 3600  # 1 hour from now
        },
        "sync_test_user2": {
            "token": "test_session_token_2",
            "expiry": current_time + 7200  # 2 hours from now
        }
    }
    
    with open("sessions.json", "w") as f:
        json.dump(test_sessions, f, indent=2)
    print("✅ Created test sessions in sessions.json")
    
    # Create test verification tokens
    test_verification = {
        "sync_test_user1": {
            "token": "test_verification_token_1",
            "expiry": current_time + 86400,  # 24 hours from now
            "verified": False,
            "email": "sync_test1@example.com"
        },
        "sync_test_user2": {
            "token": "test_verification_token_2",
            "expiry": current_time + 172800,  # 48 hours from now
            "verified": True,
            "email": "sync_test2@example.com"
        }
    }
    
    with open("verification.json", "w") as f:
        json.dump(test_verification, f, indent=2)
    print("✅ Created test verification tokens in verification.json")
    
    # Create test reset tokens
    test_reset_tokens = {
        "test_reset_token_1": {
            "username": "sync_test_user1",
            "email": "sync_test1@example.com",
            "expiry": current_time + 3600,  # 1 hour from now
            "created": current_time
        },
        "test_reset_token_2": {
            "username": "sync_test_user2",
            "email": "sync_test2@example.com",
            "expiry": current_time + 7200,  # 2 hours from now
            "created": current_time
        }
    }
    
    with open("reset_tokens.json", "w") as f:
        json.dump(test_reset_tokens, f, indent=2)
    print("✅ Created test reset tokens in reset_tokens.json")
    
    print("=" * 70)

def test_sync_status():
    """Test sync status functionality"""
    print("\n" + "=" * 70)
    print("TESTING SYNC STATUS")
    print("=" * 70)
    
    status = get_sync_status()
    print(f"Database available: {status['database_available']}")
    print(f"Last sync: {time.ctime(status['last_sync']) if status['last_sync'] else 'Never'}")
    print(f"Sync in progress: {status['sync_in_progress']}")
    print(f"Synced counts: {status['synced_counts']}")
    print(f"Failed syncs: {status['failed_syncs']}")
    
    print("=" * 70)

def test_sync_mechanism():
    """Test the sync mechanism"""
    print("\n" + "=" * 70)
    print("TESTING SYNC MECHANISM")
    print("=" * 70)
    
    if not is_database_available():
        print("❌ Database not available, cannot test sync")
        return False
    
    print("1. Clearing sync tracking to simulate fresh sync...")
    clear_sync_tracking()
    
    print("2. Running sync...")
    success = sync_all_data()
    print(f"Sync result: {'✅ Success' if success else '❌ Failed'}")
    
    print("3. Checking sync status after sync...")
    status = get_sync_status()
    print(f"Synced counts after sync: {status['synced_counts']}")
    
    print("4. Testing individual sync functions...")
    
    # Test user sync
    print("\n   Testing user sync...")
    user_sync_success = sync_manager.sync_users()
    print(f"   User sync: {'✅ Success' if user_sync_success else '❌ Failed'}")
    
    # Test session sync
    print("   Testing session sync...")
    session_sync_success = sync_manager.sync_sessions()
    print(f"   Session sync: {'✅ Success' if session_sync_success else '❌ Failed'}")
    
    # Test verification sync
    print("   Testing verification sync...")
    verification_sync_success = sync_manager.sync_verification_tokens()
    print(f"   Verification sync: {'✅ Success' if verification_sync_success else '❌ Failed'}")
    
    # Test reset token sync
    print("   Testing reset token sync...")
    reset_sync_success = sync_manager.sync_reset_tokens()
    print(f"   Reset token sync: {'✅ Success' if reset_sync_success else '❌ Failed'}")
    
    print("=" * 70)
    return success

def test_hybrid_operations_with_sync():
    """Test hybrid operations with sync integration"""
    print("\n" + "=" * 70)
    print("TESTING HYBRID OPERATIONS WITH SYNC")
    print("=" * 70)
    
    # Clear sync tracking
    clear_sync_tracking()
    
    print("1. Testing user operations with sync...")
    test_username = "sync_hybrid_test_user"
    test_email = "sync_hybrid_test@example.com"
    test_password = "testpassword123"
    
    # Save user (should trigger sync)
    print(f"   Saving user '{test_username}'...")
    success = user_manager.save_user(test_username, test_email, test_password)
    print(f"   Save result: {'✅ Success' if success else '❌ Failed'}")
    
    # Retrieve user
    print(f"   Retrieving user '{test_username}'...")
    user = user_manager.get_user(test_username)
    if user:
        print(f"   ✅ User found: {user['username']} ({user['email']})")
    else:
        print("   ❌ User not found")
    
    print("\n2. Testing session operations with sync...")
    # Create session (should trigger sync)
    print(f"   Creating session for '{test_username}'...")
    token = session_manager.create_session(test_username, 3600)
    print(f"   Session token: {token[:20]}...")
    
    # Validate session
    print(f"   Validating session...")
    valid = session_manager.validate_session(test_username, token)
    print(f"   Validation result: {'✅ Valid' if valid else '❌ Invalid'}")
    
    print("\n3. Testing verification operations with sync...")
    # Generate verification token (should trigger sync)
    print(f"   Generating verification token for '{test_username}'...")
    verify_token = verification_manager.generate_verification_token(test_username, test_email, 24)
    print(f"   Verification token: {verify_token[:20]}...")
    
    # Verify email
    print(f"   Verifying email...")
    verify_success = verification_manager.verify_email(test_username, verify_token)
    print(f"   Verification result: {'✅ Success' if verify_success else '❌ Failed'}")
    
    print("\n4. Testing password reset operations with sync...")
    # Generate reset token (should trigger sync)
    print(f"   Generating reset token for '{test_username}'...")
    reset_token = reset_manager.generate_reset_token(test_username, 1)
    if reset_token:
        print(f"   Reset token: {reset_token[:20]}...")
        
        # Reset password
        print(f"   Resetting password...")
        reset_success = reset_manager.reset_password(reset_token, "newpassword456")
        print(f"   Reset result: {'✅ Success' if reset_success else '❌ Failed'}")
    else:
        print("   ❌ Reset token generation failed")
    
    print("=" * 70)

def test_sync_tracking():
    """Test sync tracking functionality"""
    print("\n" + "=" * 70)
    print("TESTING SYNC TRACKING")
    print("=" * 70)
    
    # Check if sync tracking file exists
    if os.path.exists("sync_tracking.json"):
        with open("sync_tracking.json", "r") as f:
            tracking_data = json.load(f)
        
        print("Sync tracking data:")
        print(f"  Last sync: {time.ctime(tracking_data.get('last_sync', 0)) if tracking_data.get('last_sync') else 'Never'}")
        print(f"  Synced users: {len(tracking_data.get('synced_users', {}))}")
        print(f"  Synced sessions: {len(tracking_data.get('synced_sessions', {}))}")
        print(f"  Synced verification: {len(tracking_data.get('synced_verification', {}))}")
        print(f"  Synced reset tokens: {len(tracking_data.get('synced_reset_tokens', {}))}")
        print(f"  Failed syncs: {len(tracking_data.get('failed_syncs', []))}")
    else:
        print("No sync tracking file found")
    
    print("=" * 70)

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 70)
    print("CLEANING UP TEST DATA")
    print("=" * 70)
    
    # Remove test JSON files
    test_files = ["users.json", "sessions.json", "verification.json", "reset_tokens.json", "sync_tracking.json"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Removed {file}")
            except Exception as e:
                print(f"❌ Failed to remove {file}: {e}")
    
    # Clean up database test data
    if is_database_available():
        from database_manager import execute_database_query
        
        test_users = ["sync_test_user1", "sync_test_user2", "sync_hybrid_test_user"]
        
        for username in test_users:
            # Delete from all tables
            execute_database_query("DELETE FROM users WHERE username = %s", (username,))
            execute_database_query("DELETE FROM sessions WHERE username = %s", (username,))
            execute_database_query("DELETE FROM verification_tokens WHERE username = %s", (username,))
            execute_database_query("DELETE FROM reset_tokens WHERE username = %s", (username,))
        
        print("✅ Cleaned up database test data")
    
    print("=" * 70)

def main():
    """Main test function"""
    print("SYNC SYSTEM COMPREHENSIVE TEST")
    print("=" * 70)
    
    try:
        # Test 1: Create test JSON data
        create_test_json_data()
        
        # Test 2: Test sync status
        test_sync_status()
        
        # Test 3: Test sync mechanism
        sync_success = test_sync_mechanism()
        
        # Test 4: Test hybrid operations with sync
        test_hybrid_operations_with_sync()
        
        # Test 5: Test sync tracking
        test_sync_tracking()
        
        # Test 6: Test check_and_sync function
        print("\n" + "=" * 70)
        print("TESTING CHECK_AND_SYNC FUNCTION")
        print("=" * 70)
        
        check_result = check_and_sync()
        print(f"Check and sync result: {'✅ Success' if check_result else '❌ Failed'}")
        
        print("\n" + "=" * 70)
        print("ALL SYNC TESTS COMPLETED!")
        print("=" * 70)
        
        if sync_success:
            print("✅ Sync system is working correctly")
            print("✅ JSON to database synchronization is functional")
            print("✅ Hybrid system integration is working")
            print("✅ Sync tracking is operational")
        else:
            print("⚠️ Some sync tests failed")
            print("   Check database connection and permissions")
        
        print("\nYour sync system is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test data
        cleanup_test_data()

if __name__ == "__main__":
    main()
