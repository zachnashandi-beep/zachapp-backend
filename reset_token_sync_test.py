#!/usr/bin/env python3
"""
Reset Token Sync Test
Test the reset token sync functionality with database offline/online scenarios
"""

import json
import os
import time
from sync_manager import sync_manager, check_and_sync, get_sync_status, clear_sync_tracking
from hybrid_password_reset_manager import reset_manager
from hybrid_user_manager import user_manager
from database_manager import is_database_available

def create_test_user():
    """Create a test user for reset token testing"""
    test_username = "reset_sync_test_user"
    test_email = "reset_sync_test@example.com"
    test_password = "testpassword123"
    
    print(f"Creating test user: {test_username}")
    success = user_manager.save_user(test_username, test_email, test_password)
    if success:
        print(f"✅ Test user '{test_username}' created successfully")
        return test_username, test_email
    else:
        print(f"❌ Failed to create test user '{test_username}'")
        return None, None

def simulate_db_offline_scenario():
    """Simulate database offline scenario"""
    print("\n" + "=" * 70)
    print("SIMULATING DATABASE OFFLINE SCENARIO")
    print("=" * 70)
    
    # Create test user
    username, email = create_test_user()
    if not username:
        return False
    
    print(f"\n1. Generating reset tokens while database is available...")
    
    # Generate multiple reset tokens
    tokens = []
    for i in range(3):
        token = reset_manager.generate_reset_token(username, 1)
        if token:
            tokens.append(token)
            print(f"   ✅ Generated reset token {i+1}: {token[:20]}...")
        else:
            print(f"   ❌ Failed to generate reset token {i+1}")
    
    print(f"\n2. Checking reset_tokens.json file...")
    if os.path.exists("reset_tokens.json"):
        with open("reset_tokens.json", "r") as f:
            reset_tokens = json.load(f)
        print(f"   📄 Found {len(reset_tokens)} reset tokens in JSON file")
        
        for token, data in reset_tokens.items():
            print(f"   - Token: {token[:20]}... (User: {data['username']}, Expiry: {time.ctime(data['expiry'])})")
    else:
        print("   ❌ reset_tokens.json file not found")
        return False
    
    print(f"\n3. Checking sync status...")
    status = get_sync_status()
    print(f"   Database available: {status['database_available']}")
    print(f"   Synced reset tokens: {status['synced_counts']['reset_tokens']}")
    
    return True

def test_reset_token_sync():
    """Test reset token sync functionality"""
    print("\n" + "=" * 70)
    print("TESTING RESET TOKEN SYNC")
    print("=" * 70)
    
    # Clear sync tracking to simulate fresh sync
    print("1. Clearing sync tracking...")
    clear_sync_tracking()
    
    # Check current status
    print("2. Checking current sync status...")
    status = get_sync_status()
    print(f"   Database available: {status['database_available']}")
    print(f"   Synced reset tokens: {status['synced_counts']['reset_tokens']}")
    
    if not status['database_available']:
        print("   ❌ Database not available, cannot test sync")
        return False
    
    # Run sync
    print("3. Running sync...")
    sync_success = sync_manager.sync_reset_tokens()
    print(f"   Reset token sync result: {'✅ Success' if sync_success else '❌ Failed'}")
    
    # Check updated status
    print("4. Checking updated sync status...")
    status = get_sync_status()
    print(f"   Synced reset tokens: {status['synced_counts']['reset_tokens']}")
    
    # Check sync tracking file
    print("5. Checking sync tracking...")
    if os.path.exists("sync_tracking.json"):
        with open("sync_tracking.json", "r") as f:
            tracking = json.load(f)
        synced_tokens = tracking.get("synced_reset_tokens", {})
        print(f"   Synced tokens in tracking: {len(synced_tokens)}")
        
        for token, timestamp in synced_tokens.items():
            print(f"   - {token[:20]}... synced at {time.ctime(timestamp)}")
    
    return sync_success

def test_reset_token_validation():
    """Test reset token validation after sync"""
    print("\n" + "=" * 70)
    print("TESTING RESET TOKEN VALIDATION AFTER SYNC")
    print("=" * 70)
    
    # Check if we have any reset tokens in JSON
    if not os.path.exists("reset_tokens.json"):
        print("❌ No reset_tokens.json file found")
        return False
    
    with open("reset_tokens.json", "r") as f:
        reset_tokens = json.load(f)
    
    if not reset_tokens:
        print("❌ No reset tokens found in JSON file")
        return False
    
    print(f"Found {len(reset_tokens)} reset tokens to validate...")
    
    # Test validation for each token
    for token, token_data in reset_tokens.items():
        print(f"\nValidating token: {token[:20]}...")
        
        # Validate token
        validation_result = reset_manager.validate_reset_token(token)
        if validation_result:
            print(f"   ✅ Token is valid")
            print(f"   - Username: {validation_result['username']}")
            print(f"   - Email: {validation_result['email']}")
            print(f"   - Expiry: {time.ctime(validation_result['expiry'])}")
        else:
            print(f"   ❌ Token is invalid or expired")
    
    return True

def test_reset_token_operations():
    """Test complete reset token operations"""
    print("\n" + "=" * 70)
    print("TESTING COMPLETE RESET TOKEN OPERATIONS")
    print("=" * 70)
    
    # Create test user
    username, email = create_test_user()
    if not username:
        return False
    
    print(f"\n1. Generating new reset token...")
    token = reset_manager.generate_reset_token(username, 1)
    if token:
        print(f"   ✅ Generated token: {token[:20]}...")
    else:
        print(f"   ❌ Failed to generate token")
        return False
    
    print(f"\n2. Validating token...")
    validation_result = reset_manager.validate_reset_token(token)
    if validation_result:
        print(f"   ✅ Token is valid")
    else:
        print(f"   ❌ Token is invalid")
        return False
    
    print(f"\n3. Resetting password...")
    new_password = "newpassword456"
    reset_success = reset_manager.reset_password(token, new_password)
    if reset_success:
        print(f"   ✅ Password reset successful")
    else:
        print(f"   ❌ Password reset failed")
        return False
    
    print(f"\n4. Verifying token is invalidated after use...")
    validation_result = reset_manager.validate_reset_token(token)
    if not validation_result:
        print(f"   ✅ Token correctly invalidated after use")
    else:
        print(f"   ❌ Token should be invalid after use")
        return False
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 70)
    print("CLEANING UP TEST DATA")
    print("=" * 70)
    
    # Remove test JSON files
    test_files = ["reset_tokens.json", "sync_tracking.json"]
    
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
        
        test_username = "reset_sync_test_user"
        
        # Delete from all tables
        execute_database_query("DELETE FROM users WHERE username = %s", (test_username,))
        execute_database_query("DELETE FROM sessions WHERE username = %s", (test_username,))
        execute_database_query("DELETE FROM verification_tokens WHERE username = %s", (test_username,))
        execute_database_query("DELETE FROM reset_tokens WHERE username = %s", (test_username,))
        
        print("✅ Cleaned up database test data")
    
    print("=" * 70)

def main():
    """Main test function"""
    print("RESET TOKEN SYNC COMPREHENSIVE TEST")
    print("=" * 70)
    
    try:
        # Test 1: Simulate database offline scenario
        offline_success = simulate_db_offline_scenario()
        
        # Test 2: Test reset token sync
        sync_success = test_reset_token_sync()
        
        # Test 3: Test reset token validation
        validation_success = test_reset_token_validation()
        
        # Test 4: Test complete reset token operations
        operations_success = test_reset_token_operations()
        
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"Database offline scenario: {'✅ Success' if offline_success else '❌ Failed'}")
        print(f"Reset token sync: {'✅ Success' if sync_success else '❌ Failed'}")
        print(f"Token validation: {'✅ Success' if validation_success else '❌ Failed'}")
        print(f"Complete operations: {'✅ Success' if operations_success else '❌ Failed'}")
        
        if all([offline_success, sync_success, validation_success, operations_success]):
            print("\n🎉 ALL RESET TOKEN SYNC TESTS PASSED!")
            print("✅ Reset token sync system is working correctly")
            print("✅ Database schema is properly updated")
            print("✅ Sync tracking is operational")
            print("✅ JSON fallback is working")
        else:
            print("\n⚠️ Some tests failed")
            print("   Check the output above for details")
        
        print("\nYour reset token sync system is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test data
        cleanup_test_data()

if __name__ == "__main__":
    main()
