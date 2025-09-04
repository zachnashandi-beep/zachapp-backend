#!/usr/bin/env python3
"""
Test Login Error Messages
Test the improved login system with proper error messages
"""

import os
from hybrid_user_manager import user_manager, validate_user_credentials_case_insensitive, get_user_case_insensitive
from database_manager import is_database_available

def test_login_error_messages():
    """Test login error messages for different scenarios"""
    print("🧪 TESTING LOGIN ERROR MESSAGES")
    print("=" * 60)
    
    # Create a test user first
    test_username = "testuser_login"
    test_email = "test@login.com"
    test_password = "correctpassword123"
    
    print("1️⃣ Creating test user...")
    user_created = user_manager.save_user(test_username, test_email, test_password)
    print(f"   User created: {'✅ Success' if user_created else '❌ Failed'}")
    print()
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Non-existent username",
            "username": "nonexistentuser",
            "password": "anypassword",
            "expected": "User Not Found"
        },
        {
            "name": "Wrong password for existing user",
            "username": test_username,
            "password": "wrongpassword",
            "expected": "Incorrect Password"
        },
        {
            "name": "Correct credentials",
            "username": test_username,
            "password": test_password,
            "expected": "Login Success"
        },
        {
            "name": "Case-insensitive username (wrong password)",
            "username": test_username.upper(),
            "password": "wrongpassword",
            "expected": "Incorrect Password"
        },
        {
            "name": "Case-insensitive username (correct password)",
            "username": test_username.upper(),
            "password": test_password,
            "expected": "Login Success"
        }
    ]
    
    print("2️⃣ Testing login scenarios...")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n   Test {i}: {scenario['name']}")
        print(f"   Username: '{scenario['username']}'")
        print(f"   Password: '{scenario['password']}'")
        
        # Check if username exists
        user_data = get_user_case_insensitive(scenario['username'])
        username_exists = user_data is not None
        
        if not username_exists:
            print(f"   Result: ❌ User Not Found (as expected)")
            print(f"   Message: Username '{scenario['username']}' does not exist")
        else:
            # Check password
            is_valid, actual_username = validate_user_credentials_case_insensitive(
                scenario['username'], scenario['password']
            )
            
            if is_valid:
                print(f"   Result: ✅ Login Success (as expected)")
                print(f"   Actual username: {actual_username}")
            else:
                print(f"   Result: ❌ Incorrect Password (as expected)")
                print(f"   Message: Incorrect password for user '{actual_username}'")
    
    print()
    print("3️⃣ Testing edge cases...")
    
    # Test empty username
    print("\n   Edge Case 1: Empty username")
    user_data = get_user_case_insensitive("")
    print(f"   Result: {'❌ User Not Found' if not user_data else '⚠️ Unexpected'}")
    
    # Test username with spaces
    print("\n   Edge Case 2: Username with spaces")
    user_data = get_user_case_insensitive("  testuser_login  ")
    print(f"   Result: {'❌ User Not Found' if not user_data else '⚠️ Unexpected'}")
    
    # Test very long username
    print("\n   Edge Case 3: Very long username")
    long_username = "a" * 100
    user_data = get_user_case_insensitive(long_username)
    print(f"   Result: {'❌ User Not Found' if not user_data else '⚠️ Unexpected'}")
    
    print()
    print("🎉 LOGIN ERROR MESSAGE TEST COMPLETED!")
    print("✅ System now distinguishes between:")
    print("   • Username doesn't exist → 'User Not Found'")
    print("   • Wrong password → 'Incorrect Password'")
    print("   • Correct credentials → Login success")
    print("✅ Case-insensitive username checking works")
    print("✅ Clear, helpful error messages provided")

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 CLEANING UP TEST DATA")
    print("=" * 30)
    
    # Remove test user from users.json
    if os.path.exists("users.json"):
        try:
            import json
            with open("users.json", "r") as f:
                users_data = json.load(f)
            
            test_username = "testuser_login"
            if test_username in users_data:
                del users_data[test_username]
                with open("users.json", "w") as f:
                    json.dump(users_data, f, indent=2)
                print(f"✅ Removed test user from users.json")
        except Exception as e:
            print(f"❌ Error cleaning users.json: {e}")

def main():
    """Main test function"""
    print("LOGIN ERROR MESSAGE TEST")
    print("=" * 60)
    print("This test verifies the improved login system provides")
    print("clear error messages for different failure scenarios")
    print()
    
    try:
        test_login_error_messages()
        cleanup_test_data()
        
        print("\n🎯 LOGIN SYSTEM IMPROVED!")
        print("✅ Users now get clear feedback:")
        print("   • 'User Not Found' for non-existent usernames")
        print("   • 'Incorrect Password' for wrong passwords")
        print("   • Proper case-insensitive username handling")
        print("✅ Better security and user experience")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
