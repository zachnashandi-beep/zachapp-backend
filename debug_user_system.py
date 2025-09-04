#!/usr/bin/env python3
"""
Debug User System
Check what's happening with user storage and retrieval
"""

import os
import json
from hybrid_user_manager import user_manager, get_user_case_insensitive, validate_user_credentials_case_insensitive
from database_manager import is_database_available

def debug_user_system():
    """Debug the user system to see what's happening"""
    print("=" * 70)
    print("DEBUGGING USER SYSTEM")
    print("=" * 70)
    
    # Check database availability
    print("1. Database Status:")
    db_available = is_database_available()
    print(f"   Database Available: {'✅ Yes' if db_available else '❌ No'}")
    
    # Check users.json file
    print("\n2. Users.json File:")
    users_file = "users.json"
    if os.path.exists(users_file):
        try:
            with open(users_file, "r", encoding="utf-8") as f:
                users_data = json.load(f)
            print(f"   File exists: ✅ Yes")
            print(f"   File size: {len(str(users_data))} characters")
            print(f"   Content: {users_data}")
            
            if users_data:
                print(f"   Users found: {list(users_data.keys())}")
            else:
                print(f"   Users found: None (empty file)")
        except Exception as e:
            print(f"   Error reading file: {e}")
    else:
        print(f"   File exists: ❌ No")
    
    # Test user lookup
    print("\n3. User Lookup Test:")
    test_username = "fxquadratics"
    
    # Try case-insensitive lookup
    user_data = get_user_case_insensitive(test_username)
    if user_data:
        print(f"   User '{test_username}' found: ✅ Yes")
        print(f"   Email: {user_data.get('email', 'N/A')}")
        print(f"   Has password: {'✅ Yes' if user_data.get('password') else '❌ No'}")
    else:
        print(f"   User '{test_username}' found: ❌ No")
    
    # Test credential validation
    print("\n4. Credential Validation Test:")
    test_password = "testpassword123"  # You'll need to provide the actual password
    is_valid, actual_username = validate_user_credentials_case_insensitive(test_username, test_password)
    print(f"   Credentials valid: {'✅ Yes' if is_valid else '❌ No'}")
    if is_valid:
        print(f"   Actual username: {actual_username}")
    
    # Check if we can create a test user
    print("\n5. Test User Creation:")
    test_username_new = "testuser_debug"
    test_email_new = "test@example.com"
    test_password_new = "testpass123"
    
    try:
        user_created = user_manager.save_user(test_username_new, test_email_new, test_password_new)
        print(f"   Test user created: {'✅ Yes' if user_created else '❌ No'}")
        
        # Check if it was saved to JSON
        if os.path.exists(users_file):
            with open(users_file, "r", encoding="utf-8") as f:
                users_data = json.load(f)
            if test_username_new in users_data:
                print(f"   Test user in JSON: ✅ Yes")
            else:
                print(f"   Test user in JSON: ❌ No")
        
    except Exception as e:
        print(f"   Error creating test user: {e}")
    
    print("\n" + "=" * 70)

def main():
    """Main debug function"""
    print("USER SYSTEM DEBUG")
    print("=" * 70)
    
    try:
        debug_user_system()
    except Exception as e:
        print(f"\n❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
