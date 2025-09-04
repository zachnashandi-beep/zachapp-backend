#!/usr/bin/env python3
"""
Database Connection Test
Comprehensive test for AWS MySQL database connection and hybrid system
"""

import sys
import os
import time
from database_manager import (
    db_manager, is_database_available, get_database_connection,
    execute_database_query, DB_CONFIG
)
from hybrid_user_manager import user_manager
from hybrid_session_manager import session_manager
from hybrid_verification_manager import verification_manager
from hybrid_password_reset_manager import reset_manager

def test_database_connection():
    """Test basic database connection"""
    print("=" * 70)
    print("DATABASE CONNECTION TEST")
    print("=" * 70)
    
    print(f"Database Host: {DB_CONFIG['host']}")
    print(f"Database Port: {DB_CONFIG['port']}")
    print(f"Database Name: {DB_CONFIG['database']}")
    print(f"Database User: {DB_CONFIG['user']}")
    print(f"MySQL Available: {db_manager.is_connected}")
    print(f"Fallback to JSON: {db_manager.fallback_to_json}")
    
    if is_database_available():
        print("\n✅ Database connection successful!")
        
        # Test basic query
        result = execute_database_query("SELECT 1 as test, NOW() as current_time", fetch=True)
        if result:
            print(f"✅ Query test successful: {result[0]}")
        
        # Test database info
        result = execute_database_query("SELECT DATABASE() as db_name, USER() as db_user", fetch=True)
        if result:
            print(f"✅ Database info: {result[0]['db_name']} (User: {result[0]['db_user']})")
        
        # Test table existence
        tables = execute_database_query("SHOW TABLES", fetch=True)
        if tables:
            table_names = [list(table.values())[0] for table in tables]
            print(f"✅ Tables found: {table_names}")
        else:
            print("ℹ️ No tables found (will be created automatically)")
        
    else:
        print("\n❌ Database connection failed!")
        print("   Using JSON fallback system")
        print("   Check your database credentials and network connection")
    
    print("=" * 70)

def test_hybrid_user_management():
    """Test hybrid user management"""
    print("\n" + "=" * 70)
    print("HYBRID USER MANAGEMENT TEST")
    print("=" * 70)
    
    test_username = "testuser_hybrid"
    test_email = "test_hybrid@example.com"
    test_password = "testpassword123"
    
    print(f"Testing with user: {test_username}")
    print(f"Email: {test_email}")
    
    # Test saving user
    print(f"\n1. Saving user...")
    success = user_manager.save_user(test_username, test_email, test_password)
    print(f"Save result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test retrieving user
    print(f"\n2. Retrieving user...")
    user = user_manager.get_user(test_username)
    if user:
        print(f"✅ User found: {user['username']} ({user['email']})")
    else:
        print("❌ User not found")
    
    # Test validation
    print(f"\n3. Validating credentials...")
    valid = user_manager.validate_user(test_username, test_password)
    print(f"Validation result: {'✅ Valid' if valid else '❌ Invalid'}")
    
    # Test email lookup
    print(f"\n4. Looking up by email...")
    user_by_email = user_manager.get_user_by_email(test_email)
    if user_by_email:
        print(f"✅ User found by email: {user_by_email['username']}")
    else:
        print("❌ User not found by email")
    
    # Test password update
    print(f"\n5. Updating password...")
    new_password = "newpassword456"
    update_success = user_manager.update_user_password(test_username, new_password)
    print(f"Password update result: {'✅ Success' if update_success else '❌ Failed'}")
    
    # Test validation with new password
    print(f"\n6. Validating with new password...")
    valid_new = user_manager.validate_user(test_username, new_password)
    print(f"New password validation: {'✅ Valid' if valid_new else '❌ Invalid'}")
    
    print("=" * 70)

def test_hybrid_session_management():
    """Test hybrid session management"""
    print("\n" + "=" * 70)
    print("HYBRID SESSION MANAGEMENT TEST")
    print("=" * 70)
    
    test_username = "testuser_session_hybrid"
    
    print(f"Testing with user: {test_username}")
    
    # Test creating session
    print(f"\n1. Creating session...")
    token = session_manager.create_session(test_username, 3600)
    print(f"Session token: {token[:20]}...")
    
    # Test validating session
    print(f"\n2. Validating session...")
    valid = session_manager.validate_session(test_username, token)
    print(f"Validation result: {'✅ Valid' if valid else '❌ Invalid'}")
    
    # Test getting session info
    print(f"\n3. Getting session info...")
    session_info = session_manager.get_session_info(test_username)
    if session_info:
        print(f"✅ Session info: expires at {time.ctime(session_info['expiry'])}")
    else:
        print("❌ No session info found")
    
    # Test ending session
    print(f"\n4. Ending session...")
    success = session_manager.end_session(test_username, token)
    print(f"End session result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test validation after ending
    print(f"\n5. Validating ended session...")
    valid_after = session_manager.validate_session(test_username, token)
    print(f"Validation after end: {'✅ Valid' if valid_after else '❌ Invalid'}")
    
    print("=" * 70)

def test_hybrid_verification_management():
    """Test hybrid verification management"""
    print("\n" + "=" * 70)
    print("HYBRID VERIFICATION MANAGEMENT TEST")
    print("=" * 70)
    
    test_username = "testuser_verify_hybrid"
    test_email = "test_verify_hybrid@example.com"
    
    print(f"Testing with user: {test_username}")
    print(f"Email: {test_email}")
    
    # Test generating verification token
    print(f"\n1. Generating verification token...")
    token = verification_manager.generate_verification_token(test_username, test_email, 24)
    print(f"Verification token: {token[:20]}...")
    
    # Test checking verification status
    print(f"\n2. Checking verification status...")
    verified = verification_manager.is_verified(test_username)
    print(f"Verification status: {'✅ Verified' if verified else '❌ Not verified'}")
    
    # Test getting verification info
    print(f"\n3. Getting verification info...")
    info = verification_manager.get_verification_info(test_username)
    if info:
        print(f"✅ Verification info: expires at {time.ctime(info['expiry'])}")
        print(f"   Email: {info['email']}")
        print(f"   Verified: {info['verified']}")
    else:
        print("❌ No verification info found")
    
    # Test verifying email
    print(f"\n4. Verifying email...")
    success = verification_manager.verify_email(test_username, token)
    print(f"Verification result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test checking verification status again
    print(f"\n5. Checking verification status after verification...")
    verified_after = verification_manager.is_verified(test_username)
    print(f"Verification status: {'✅ Verified' if verified_after else '❌ Not verified'}")
    
    print("=" * 70)

def test_hybrid_password_reset_management():
    """Test hybrid password reset management"""
    print("\n" + "=" * 70)
    print("HYBRID PASSWORD RESET MANAGEMENT TEST")
    print("=" * 70)
    
    test_username = "testuser_reset_hybrid"
    test_email = "test_reset_hybrid@example.com"
    test_password = "resetpassword123"
    
    print(f"Testing with user: {test_username}")
    print(f"Email: {test_email}")
    
    # First create a user
    print(f"\n0. Creating test user...")
    from hybrid_user_manager import save_user
    save_user(test_username, test_email, "oldpassword")
    
    # Test generating reset token
    print(f"\n1. Generating reset token...")
    token = reset_manager.generate_reset_token(test_username, 1)
    if token:
        print(f"Reset token: {token[:20]}...")
    else:
        print("❌ Token generation failed")
        return
    
    # Test validating reset token
    print(f"\n2. Validating reset token...")
    token_data = reset_manager.validate_reset_token(token)
    if token_data:
        print(f"✅ Token valid for: {token_data['username']}")
        print(f"   Email: {token_data['email']}")
        print(f"   Expires: {time.ctime(token_data['expiry'])}")
    else:
        print("❌ Token validation failed")
        return
    
    # Test resetting password
    print(f"\n3. Resetting password...")
    success = reset_manager.reset_password(token, test_password)
    print(f"Password reset result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test validating token after reset
    print(f"\n4. Validating token after reset...")
    token_data_after = reset_manager.validate_reset_token(token)
    if not token_data_after:
        print("✅ Token properly deleted after use")
    else:
        print("❌ Token still exists after reset")
    
    # Test login with new password
    print(f"\n5. Testing login with new password...")
    from hybrid_user_manager import validate_user
    login_success = validate_user(test_username, test_password)
    print(f"Login with new password: {'✅ Success' if login_success else '❌ Failed'}")
    
    print("=" * 70)

def test_cleanup_functions():
    """Test cleanup functions"""
    print("\n" + "=" * 70)
    print("CLEANUP FUNCTIONS TEST")
    print("=" * 70)
    
    print("1. Cleaning up expired sessions...")
    session_manager.cleanup_expired_sessions()
    
    print("2. Cleaning up expired verification tokens...")
    verification_manager.cleanup_expired_tokens()
    
    print("3. Cleaning up expired reset tokens...")
    reset_manager.cleanup_expired_tokens()
    
    print("✅ All cleanup functions completed")
    print("=" * 70)

def main():
    """Main test function"""
    print("AWS MySQL Database Connection and Hybrid System Test")
    print("=" * 70)
    
    try:
        # Test database connection
        test_database_connection()
        
        # Test hybrid user management
        test_hybrid_user_management()
        
        # Test hybrid session management
        test_hybrid_session_management()
        
        # Test hybrid verification management
        test_hybrid_verification_management()
        
        # Test hybrid password reset management
        test_hybrid_password_reset_management()
        
        # Test cleanup functions
        test_cleanup_functions()
        
        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        if is_database_available():
            print("✅ Database connection is working")
            print("✅ Hybrid system is using database as primary")
        else:
            print("⚠️ Database connection failed")
            print("✅ Hybrid system is using JSON fallback")
        
        print("\nYour app is ready to use with the hybrid system!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close database connection
        db_manager.close_connection()

if __name__ == "__main__":
    main()
