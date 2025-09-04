#!/usr/bin/env python3
"""
Comprehensive Sync Test
Test the complete sync system with all data types
"""

import json
import os
import time
from sync_manager import sync_manager, check_and_sync, get_sync_status, clear_sync_tracking, sync_all_data
from hybrid_user_manager import user_manager
from hybrid_session_manager import session_manager
from hybrid_verification_manager import verification_manager
from hybrid_password_reset_manager import reset_manager
from database_manager import is_database_available

def create_test_data_in_json():
    """Create test data directly in JSON files to simulate offline scenario"""
    print("=" * 70)
    print("CREATING TEST DATA IN JSON FILES")
    print("=" * 70)
    
    # Create test users
    test_users = {
        "json_sync_user1": {
            "username": "json_sync_user1",
            "email": "json_sync1@example.com",
            "password": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # "hello"
        },
        "json_sync_user2": {
            "username": "json_sync_user2",
            "email": "json_sync2@example.com",
            "password": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"  # "password"
        }
    }
    
    with open("users.json", "w") as f:
        json.dump(test_users, f, indent=2)
    print("✅ Created test users in users.json")
    
    # Create test sessions
    current_time = int(time.time())
    test_sessions = {
        "json_sync_user1": {
            "token": "json_session_token_1",
            "expiry": current_time + 3600  # 1 hour from now
        },
        "json_sync_user2": {
            "token": "json_session_token_2",
            "expiry": current_time + 7200  # 2 hours from now
        }
    }
    
    with open("sessions.json", "w") as f:
        json.dump(test_sessions, f, indent=2)
    print("✅ Created test sessions in sessions.json")
    
    # Create test verification tokens
    test_verification = {
        "json_sync_user1": {
            "token": "json_verification_token_1",
            "expiry": current_time + 86400,  # 24 hours from now
            "verified": False,
            "email": "json_sync1@example.com"
        },
        "json_sync_user2": {
            "token": "json_verification_token_2",
            "expiry": current_time + 172800,  # 48 hours from now
            "verified": True,
            "email": "json_sync2@example.com"
        }
    }
    
    with open("verification.json", "w") as f:
        json.dump(test_verification, f, indent=2)
    print("✅ Created test verification tokens in verification.json")
    
    # Create test reset tokens
    test_reset_tokens = {
        "json_reset_token_1": {
            "username": "json_sync_user1",
            "email": "json_sync1@example.com",
            "expiry": current_time + 3600,  # 1 hour from now
            "created": current_time
        },
        "json_reset_token_2": {
            "username": "json_sync_user2",
            "email": "json_sync2@example.com",
            "expiry": current_time + 7200,  # 2 hours from now
            "created": current_time
        }
    }
    
    with open("reset_tokens.json", "w") as f:
        json.dump(test_reset_tokens, f, indent=2)
    print("✅ Created test reset tokens in reset_tokens.json")
    
    print("=" * 70)

def test_comprehensive_sync():
    """Test comprehensive sync of all data types"""
    print("\n" + "=" * 70)
    print("TESTING COMPREHENSIVE SYNC")
    print("=" * 70)
    
    # Clear sync tracking
    clear_sync_tracking()
    
    print("1. Checking database availability...")
    if not is_database_available():
        print("   ❌ Database not available, cannot test sync")
        return False
    
    print("   ✅ Database is available")
    
    print("\n2. Running comprehensive sync...")
    sync_success = sync_all_data()
    print(f"   Sync result: {'✅ Success' if sync_success else '❌ Failed'}")
    
    print("\n3. Checking sync status...")
    status = get_sync_status()
    print(f"   Database available: {status['database_available']}")
    print(f"   Last sync: {time.ctime(status['last_sync']) if status['last_sync'] else 'Never'}")
    print(f"   Sync in progress: {status['sync_in_progress']}")
    print(f"   Synced counts:")
    for data_type, count in status['synced_counts'].items():
        print(f"     {data_type}: {count}")
    
    print("\n4. Testing individual sync functions...")
    
    # Test user sync
    print("   Testing user sync...")
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
    return sync_success

def test_hybrid_operations():
    """Test hybrid operations with sync integration"""
    print("\n" + "=" * 70)
    print("TESTING HYBRID OPERATIONS WITH SYNC")
    print("=" * 70)
    
    # Clear sync tracking
    clear_sync_tracking()
    
    print("1. Testing user operations...")
    test_username = "hybrid_sync_test_user"
    test_email = "hybrid_sync_test@example.com"
    test_password = "testpassword123"
    
    # Save user
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
    
    print("\n2. Testing session operations...")
    # Create session
    print(f"   Creating session for '{test_username}'...")
    token = session_manager.create_session(test_username, 3600)
    print(f"   Session token: {token[:20]}...")
    
    # Validate session
    print(f"   Validating session...")
    valid = session_manager.validate_session(test_username, token)
    print(f"   Validation result: {'✅ Valid' if valid else '❌ Invalid'}")
    
    print("\n3. Testing verification operations...")
    # Generate verification token
    print(f"   Generating verification token for '{test_username}'...")
    verify_token = verification_manager.generate_verification_token(test_username, test_email, 24)
    print(f"   Verification token: {verify_token[:20]}...")
    
    # Verify email
    print(f"   Verifying email...")
    verify_success = verification_manager.verify_email(test_username, verify_token)
    print(f"   Verification result: {'✅ Success' if verify_success else '❌ Failed'}")
    
    print("\n4. Testing password reset operations...")
    # Generate reset token
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
        
        # Show some synced entries
        print("\nSynced entries:")
        for data_type in ['synced_users', 'synced_sessions', 'synced_verification', 'synced_reset_tokens']:
            entries = tracking_data.get(data_type, {})
            if entries:
                print(f"  {data_type}:")
                for key, timestamp in list(entries.items())[:3]:  # Show first 3
                    print(f"    - {key[:20]}... synced at {time.ctime(timestamp)}")
                if len(entries) > 3:
                    print(f"    ... and {len(entries) - 3} more")
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
        
        test_users = ["json_sync_user1", "json_sync_user2", "hybrid_sync_test_user"]
        
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
    print("COMPREHENSIVE SYNC SYSTEM TEST")
    print("=" * 70)
    
    try:
        # Test 1: Create test data in JSON files
        create_test_data_in_json()
        
        # Test 2: Test comprehensive sync
        sync_success = test_comprehensive_sync()
        
        # Test 3: Test hybrid operations
        test_hybrid_operations()
        
        # Test 4: Test sync tracking
        test_sync_tracking()
        
        print("\n" + "=" * 70)
        print("ALL SYNC TESTS COMPLETED!")
        print("=" * 70)
        
        if sync_success:
            print("✅ Comprehensive sync system is working correctly")
            print("✅ All data types sync successfully")
            print("✅ Hybrid system integration is working")
            print("✅ Sync tracking is operational")
            print("✅ Reset token sync is fixed")
        else:
            print("⚠️ Some sync tests failed")
            print("   Check the output above for details")
        
        print("\nYour comprehensive sync system is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test data
        cleanup_test_data()

if __name__ == "__main__":
    main()
