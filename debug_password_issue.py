#!/usr/bin/env python3
"""
Debug Password Issue
Debug why password validation is failing
"""

import hashlib
import json
import os
from hybrid_user_manager import user_manager, get_user_case_insensitive, validate_user_credentials_case_insensitive

def debug_password_issue():
    """Debug the password validation issue"""
    print("🔍 DEBUGGING PASSWORD VALIDATION ISSUE")
    print("=" * 50)
    
    # Get username from user
    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()
    
    print(f"\n🔍 Testing login for: {username}")
    print(f"🔍 Password length: {len(password)}")
    
    # Test 1: Check if user exists
    print("\n1️⃣ Checking if user exists...")
    user_data = get_user_case_insensitive(username)
    if user_data:
        print(f"✅ User found: {user_data['username']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Stored password hash: {user_data['password'][:20]}...")
    else:
        print("❌ User not found")
        return
    
    # Test 2: Check password hash
    print("\n2️⃣ Checking password hash...")
    input_password_hash = hashlib.sha256(password.encode()).hexdigest()
    stored_password_hash = user_data['password']
    
    print(f"   Input password hash:  {input_password_hash[:20]}...")
    print(f"   Stored password hash: {stored_password_hash[:20]}...")
    print(f"   Hashes match: {'✅ Yes' if input_password_hash == stored_password_hash else '❌ No'}")
    
    # Test 3: Test validation function
    print("\n3️⃣ Testing validation function...")
    is_valid, returned_username = validate_user_credentials_case_insensitive(username, password)
    print(f"   Validation result: {'✅ Valid' if is_valid else '❌ Invalid'}")
    print(f"   Returned username: {returned_username}")
    
    # Test 4: Check JSON file directly
    print("\n4️⃣ Checking JSON file directly...")
    users_path = os.path.join(os.path.dirname(__file__), "users.json")
    if os.path.exists(users_path):
        with open(users_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"   JSON file exists: ✅ Yes")
        print(f"   JSON structure: {type(data)}")
        
        # Check if it's old or new structure
        if isinstance(data, dict) and "users" in data:
            print("   Using old JSON structure")
            users = data.get("users", {})
            if username in users:
                user_json = users[username]
                print(f"   User in JSON: ✅ Yes")
                print(f"   JSON password: {user_json.get('password', 'N/A')[:20]}...")
            else:
                print("   User in JSON: ❌ No")
        else:
            print("   Using new JSON structure")
            if username in data:
                user_json = data[username]
                print(f"   User in JSON: ✅ Yes")
                print(f"   JSON password: {user_json.get('password', 'N/A')[:20]}...")
            else:
                print("   User in JSON: ❌ No")
    else:
        print("   JSON file exists: ❌ No")
    
    # Test 5: Test different password variations
    print("\n5️⃣ Testing password variations...")
    test_passwords = [
        password,
        password.strip(),
        password.lower(),
        password.upper(),
        password + " ",
        " " + password,
    ]
    
    for i, test_pwd in enumerate(test_passwords):
        test_hash = hashlib.sha256(test_pwd.encode()).hexdigest()
        matches = test_hash == stored_password_hash
        print(f"   Test {i+1}: {'✅' if matches else '❌'} '{test_pwd}' (len: {len(test_pwd)})")
        if matches:
            print(f"      🎯 FOUND MATCHING PASSWORD!")
            break
    
    print("\n" + "=" * 50)
    print("🔍 Password debugging complete!")

if __name__ == "__main__":
    debug_password_issue()
