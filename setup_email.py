#!/usr/bin/env python3
"""
Email Setup Script
Helps configure Gmail SMTP for email verification
"""

import os
import getpass
from email_service import test_email_connection, get_email_status

def setup_gmail_password():
    """Setup Gmail password for SMTP"""
    print("=" * 70)
    print("GMAIL SMTP SETUP")
    print("=" * 70)
    
    print("This script will help you set up Gmail SMTP for email verification.")
    print("\nIMPORTANT: You need to use an App Password, not your regular Gmail password!")
    print("To create an App Password:")
    print("1. Go to your Google Account settings")
    print("2. Enable 2-Factor Authentication if not already enabled")
    print("3. Go to Security > App passwords")
    print("4. Generate a new app password for 'Mail'")
    print("5. Use that 16-character password here")
    
    print("\n" + "=" * 70)
    
    # Check if password already exists
    password_file = "gmail_password.txt"
    if os.path.exists(password_file):
        print(f"Gmail password file already exists: {password_file}")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("Keeping existing password file.")
            return True
    
    # Get Gmail password
    print("\nEnter your Gmail App Password:")
    print("(The 16-character password from Google Account settings)")
    password = getpass.getpass("Gmail App Password: ").strip()
    
    if not password:
        print("❌ No password entered. Setup cancelled.")
        return False
    
    if len(password) != 16:
        print("⚠️ Warning: Gmail App Passwords are usually 16 characters long.")
        continue_setup = input("Continue anyway? (y/n): ").lower().strip()
        if continue_setup != 'y':
            print("Setup cancelled.")
            return False
    
    # Save password to file
    try:
        with open(password_file, 'w') as f:
            f.write(password)
        print(f"✅ Gmail password saved to {password_file}")
    except Exception as e:
        print(f"❌ Failed to save password file: {e}")
        return False
    
    return True

def test_email_setup():
    """Test the email setup"""
    print("\n" + "=" * 70)
    print("TESTING EMAIL SETUP")
    print("=" * 70)
    
    # Check status
    status = get_email_status()
    print(f"SMTP Server: {status['smtp_server']}")
    print(f"SMTP Port: {status['smtp_port']}")
    print(f"Sender Email: {status['sender_email']}")
    print(f"Password Configured: {status['password_configured']}")
    print(f"Verification Base URL: {status['verification_base_url']}")
    
    if not status['password_configured']:
        print("\n❌ Gmail password not configured!")
        return False
    
    # Test connection
    print("\nTesting Gmail SMTP connection...")
    connection_success = test_email_connection()
    
    if connection_success:
        print("✅ Gmail SMTP connection successful!")
        print("Your email verification system is ready to use.")
        return True
    else:
        print("❌ Gmail SMTP connection failed!")
        print("Please check your Gmail App Password and try again.")
        return False

def main():
    """Main setup function"""
    print("EMAIL VERIFICATION SETUP")
    print("=" * 70)
    
    try:
        # Setup Gmail password
        password_setup_success = setup_gmail_password()
        
        if not password_setup_success:
            print("\n❌ Password setup failed.")
            return
        
        # Test email setup
        test_success = test_email_setup()
        
        if test_success:
            print("\n🎉 EMAIL SETUP COMPLETE!")
            print("✅ Gmail SMTP is configured and working")
            print("✅ Email verification system is ready")
            print("\nYou can now:")
            print("- Send verification emails to new users")
            print("- Handle email verification via GitHub Pages")
            print("- Send confirmation emails after verification")
        else:
            print("\n❌ Email setup failed.")
            print("Please check your Gmail App Password and try again.")
    
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
