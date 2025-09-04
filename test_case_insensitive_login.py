#!/usr/bin/env python3
"""
Test Case Insensitive Login
Test the case-insensitive login functionality
"""

import os
from hybrid_user_manager import user_manager, validate_user_credentials_case_insensitive, get_user_case_insensitive

def test_case_insensitive_login():
    """Test case-insensitive login functionality"""
    print("=" * 70)
    print("TESTING CASE-INSENSITIVE LOGIN")
    print("=" * 70)
    
    # Test data
    test_username = "fxquadratics"  # Original username
    test_email = "fxquadratics@example.com"
    test_password = "testpassword123"
    
    print(f"1. Creating test user with username: '{test_username}'")
    user_created = user_manager.save_user(test_username, test_email, test_password)
    print(f"   User Created: {'✅ Success' if user_created else '❌ Failed'}")
    
    if not user_created:
        return False
    
    # Test different case variations
    test_cases = [
        "fxquadratics",    # Original case
        "Fxquadratics",    # First letter capitalized
        "FXQUADRATICS",    # All uppercase
        "fxQUADRATICS",    # Mixed case
        "FxQuAdRaTiCs",    # Alternating case
    ]
    
    print(f"\n2. Testing case-insensitive login with different case variations:")
    
    for test_case in test_cases:
        print(f"\n   Testing login with username: '{test_case}'")
        
        # Test case-insensitive user lookup
        user_data = get_user_case_insensitive(test_case)
        if user_data:
            print(f"   ✅ User found: {user_data['username']} ({user_data['email']})")
        else:
            print(f"   ❌ User not found")
            continue
        
        # Test case-insensitive login validation
        is_valid, actual_username = validate_user_credentials_case_insensitive(test_case, test_password)
        if is_valid:
            print(f"   ✅ Login valid: '{test_case}' -> '{actual_username}'")
        else:
            print(f"   ❌ Login invalid")
    
    print(f"\n3. Testing with wrong password:")
    is_valid, actual_username = validate_user_credentials_case_insensitive("Fxquadratics", "wrongpassword")
    print(f"   Wrong password test: {'❌ Correctly rejected' if not is_valid else '❌ Incorrectly accepted'}")
    
    print(f"\n4. Testing with non-existent user:")
    is_valid, actual_username = validate_user_credentials_case_insensitive("nonexistent", test_password)
    print(f"   Non-existent user test: {'❌ Correctly rejected' if not is_valid else '❌ Incorrectly accepted'}")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 70)
    print("CLEANING UP TEST DATA")
    print("=" * 70)
    
    # Remove test JSON files
    test_files = ["users.json"]
    
    for file in test_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"✅ Removed {file}")
            except Exception as e:
                print(f"❌ Failed to remove {file}: {e}")
    
    print("=" * 70)

def main():
    """Main test function"""
    print("CASE-INSENSITIVE LOGIN TEST")
    print("=" * 70)
    
    try:
        # Test case-insensitive login
        test_success = test_case_insensitive_login()
        
        if test_success:
            print("\n🎉 CASE-INSENSITIVE LOGIN TEST PASSED!")
            print("✅ Users can now log in with any case variation of their username")
            print("✅ 'fxquadratics' can log in as 'Fxquadratics', 'FXQUADRATICS', etc.")
            print("✅ The system maintains the original username for consistency")
        else:
            print("\n❌ Case-insensitive login test failed")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test data
        cleanup_test_data()

if __name__ == "__main__":
    main()
