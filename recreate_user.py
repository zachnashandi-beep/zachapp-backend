#!/usr/bin/env python3
"""
Recreate User Account
Help recreate the fxquadratics user account
"""

from hybrid_user_manager import user_manager

def recreate_user():
    """Recreate the fxquadratics user account"""
    print("=" * 70)
    print("RECREATING USER ACCOUNT")
    print("=" * 70)
    
    # User details
    username = "fxquadratics"
    email = input("Enter your email address: ").strip()
    password = input("Enter your password: ").strip()
    
    if not email or not password:
        print("❌ Email and password are required!")
        return False
    
    print(f"\nCreating user account:")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Password: {'*' * len(password)}")
    
    # Create the user
    try:
        user_created = user_manager.save_user(username, email, password)
        
        if user_created:
            print(f"\n✅ User account created successfully!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Password: Set")
            print(f"\n🎉 You can now log in with your credentials!")
            return True
        else:
            print(f"\n❌ Failed to create user account")
            return False
            
    except Exception as e:
        print(f"\n❌ Error creating user account: {e}")
        return False

def main():
    """Main function"""
    print("USER ACCOUNT RECREATION")
    print("=" * 70)
    print("This will help you recreate your fxquadratics user account.")
    print("The system will save your data to the local JSON file.")
    print()
    
    try:
        success = recreate_user()
        
        if success:
            print("\n🎉 Account recreation completed!")
            print("✅ You can now log in with your username and password")
            print("✅ The system will use JSON storage (database is offline)")
        else:
            print("\n❌ Account recreation failed")
            print("Please check the error messages above")
        
    except Exception as e:
        print(f"\n❌ Recreation failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
