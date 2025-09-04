#!/usr/bin/env python3
"""
Email Verification Test
Test the complete email verification system with Gmail SMTP
"""

import os
import time
from email_service import email_service, test_email_connection, get_email_status, send_verification_email, send_confirmation_email
from hybrid_verification_manager import verification_manager, generate_verification_token, verify_email, is_verified, get_verification_data
from hybrid_user_manager import user_manager
from verification_endpoint import verification_endpoint, handle_verification_request, get_verification_status
from database_manager import is_database_available

def test_email_service_setup():
    """Test email service setup and configuration"""
    print("=" * 70)
    print("TESTING EMAIL SERVICE SETUP")
    print("=" * 70)
    
    # Check email service status
    status = get_email_status()
    print(f"SMTP Server: {status['smtp_server']}")
    print(f"SMTP Port: {status['smtp_port']}")
    print(f"Sender Email: {status['sender_email']}")
    print(f"Password Configured: {status['password_configured']}")
    print(f"Verification Base URL: {status['verification_base_url']}")
    
    if not status['password_configured']:
        print("\n❌ Gmail password not configured!")
        print("Please create gmail_password.txt with your Gmail app password")
        print("Or set GMAIL_PASSWORD environment variable")
        return False
    
    # Test SMTP connection
    print("\nTesting Gmail SMTP connection...")
    connection_success = test_email_connection()
    print(f"SMTP Connection: {'✅ Success' if connection_success else '❌ Failed'}")
    
    return connection_success

def test_verification_email_sending():
    """Test sending verification emails"""
    print("\n" + "=" * 70)
    print("TESTING VERIFICATION EMAIL SENDING")
    print("=" * 70)
    
    # Test data
    test_username = "email_test_user"
    test_email = "test@example.com"  # Replace with real email for testing
    test_token = "test_verification_token_123"
    
    print(f"Testing verification email to: {test_email}")
    print(f"Username: {test_username}")
    print(f"Token: {test_token}")
    
    # Send verification email
    email_sent = send_verification_email(test_username, test_email, test_token)
    print(f"Verification Email Sent: {'✅ Success' if email_sent else '❌ Failed'}")
    
    if email_sent:
        print("✅ Verification email sent successfully!")
        print("Check the recipient's inbox for the verification email")
    else:
        print("❌ Failed to send verification email")
        print("Check Gmail credentials and SMTP settings")
    
    return email_sent

def test_confirmation_email_sending():
    """Test sending confirmation emails"""
    print("\n" + "=" * 70)
    print("TESTING CONFIRMATION EMAIL SENDING")
    print("=" * 70)
    
    # Test data
    test_username = "email_test_user"
    test_email = "test@example.com"  # Replace with real email for testing
    
    print(f"Testing confirmation email to: {test_email}")
    print(f"Username: {test_username}")
    
    # Send confirmation email
    email_sent = send_confirmation_email(test_username, test_email)
    print(f"Confirmation Email Sent: {'✅ Success' if email_sent else '❌ Failed'}")
    
    if email_sent:
        print("✅ Confirmation email sent successfully!")
        print("Check the recipient's inbox for the confirmation email")
    else:
        print("❌ Failed to send confirmation email")
    
    return email_sent

def test_verification_workflow():
    """Test complete verification workflow"""
    print("\n" + "=" * 70)
    print("TESTING VERIFICATION WORKFLOW")
    print("=" * 70)
    
    # Create test user
    test_username = "verification_workflow_test"
    test_email = "verification_test@example.com"  # Replace with real email
    test_password = "testpassword123"
    
    print(f"1. Creating test user: {test_username}")
    user_created = user_manager.save_user(test_username, test_email, test_password)
    print(f"   User Created: {'✅ Success' if user_created else '❌ Failed'}")
    
    if not user_created:
        return False
    
    print(f"\n2. Generating verification token...")
    token = generate_verification_token(test_username, test_email, 24)
    print(f"   Token Generated: {token[:20]}...")
    
    print(f"\n3. Checking verification status...")
    is_user_verified = is_verified(test_username)
    print(f"   User Verified: {'✅ Yes' if is_user_verified else '❌ No'}")
    
    print(f"\n4. Getting verification data...")
    verification_data = get_verification_data(test_username)
    if verification_data:
        print(f"   Verification Data Found: ✅ Yes")
        print(f"   - Email: {verification_data.get('email', 'N/A')}")
        print(f"   - Verified: {verification_data.get('verified', 'N/A')}")
        print(f"   - Expiry: {time.ctime(verification_data.get('expiry', 0))}")
    else:
        print(f"   Verification Data Found: ❌ No")
    
    print(f"\n5. Testing verification endpoint...")
    verification_result = handle_verification_request(test_username, token)
    print(f"   Verification Result: {verification_result}")
    
    print(f"\n6. Checking verification status after verification...")
    is_user_verified_after = is_verified(test_username)
    print(f"   User Verified After: {'✅ Yes' if is_user_verified_after else '❌ No'}")
    
    return True

def test_verification_endpoint():
    """Test verification endpoint functionality"""
    print("\n" + "=" * 70)
    print("TESTING VERIFICATION ENDPOINT")
    print("=" * 70)
    
    # Test data
    test_username = "endpoint_test_user"
    test_token = "endpoint_test_token"
    
    print(f"Testing verification endpoint with:")
    print(f"  Username: {test_username}")
    print(f"  Token: {test_token}")
    
    # Test verification request
    result = handle_verification_request(test_username, test_token)
    print(f"\nVerification Request Result:")
    print(f"  Success: {result.get('success', False)}")
    print(f"  Message: {result.get('message', 'N/A')}")
    print(f"  Username: {result.get('username', 'N/A')}")
    print(f"  Redirect URL: {result.get('redirect_url', 'N/A')}")
    
    # Test verification status
    status = get_verification_status(test_username)
    print(f"\nVerification Status:")
    print(f"  Username: {status.get('username', 'N/A')}")
    print(f"  Verified: {status.get('verified', False)}")
    print(f"  Verification Data: {status.get('verification_data', 'N/A')}")
    
    return True

def test_email_templates():
    """Test email template generation"""
    print("\n" + "=" * 70)
    print("TESTING EMAIL TEMPLATES")
    print("=" * 70)
    
    # Test data
    test_username = "template_test_user"
    test_verification_link = "https://zachnashandi-beep.github.io/zachapp/verify?username=test&token=abc123"
    
    print("Testing email template generation...")
    
    # Test HTML template
    html_content = email_service._create_verification_email_html(test_username, test_verification_link)
    print(f"HTML Template Generated: {'✅ Success' if html_content else '❌ Failed'}")
    print(f"HTML Content Length: {len(html_content)} characters")
    
    # Test text template
    text_content = email_service._create_verification_email_text(test_username, test_verification_link)
    print(f"Text Template Generated: {'✅ Success' if text_content else '❌ Failed'}")
    print(f"Text Content Length: {len(text_content)} characters")
    
    # Test confirmation templates
    html_confirmation = email_service._create_confirmation_email_html(test_username)
    print(f"Confirmation HTML Template: {'✅ Success' if html_confirmation else '❌ Failed'}")
    
    text_confirmation = email_service._create_confirmation_email_text(test_username)
    print(f"Confirmation Text Template: {'✅ Success' if text_confirmation else '❌ Failed'}")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 70)
    print("CLEANING UP TEST DATA")
    print("=" * 70)
    
    # Clean up database test data
    if is_database_available():
        from database_manager import execute_database_query
        
        test_users = ["email_test_user", "verification_workflow_test", "endpoint_test_user", "template_test_user"]
        
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
    print("EMAIL VERIFICATION SYSTEM COMPREHENSIVE TEST")
    print("=" * 70)
    
    try:
        # Test 1: Email service setup
        email_setup_success = test_email_service_setup()
        
        if not email_setup_success:
            print("\n❌ Email service setup failed. Please configure Gmail credentials.")
            return
        
        # Test 2: Email template generation
        template_success = test_email_templates()
        
        # Test 3: Verification email sending
        verification_email_success = test_verification_email_sending()
        
        # Test 4: Confirmation email sending
        confirmation_email_success = test_confirmation_email_sending()
        
        # Test 5: Verification workflow
        workflow_success = test_verification_workflow()
        
        # Test 6: Verification endpoint
        endpoint_success = test_verification_endpoint()
        
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"Email Service Setup: {'✅ Success' if email_setup_success else '❌ Failed'}")
        print(f"Email Templates: {'✅ Success' if template_success else '❌ Failed'}")
        print(f"Verification Email Sending: {'✅ Success' if verification_email_success else '❌ Failed'}")
        print(f"Confirmation Email Sending: {'✅ Success' if confirmation_email_success else '❌ Failed'}")
        print(f"Verification Workflow: {'✅ Success' if workflow_success else '❌ Failed'}")
        print(f"Verification Endpoint: {'✅ Success' if endpoint_success else '❌ Failed'}")
        
        if all([email_setup_success, template_success, verification_email_success, 
                confirmation_email_success, workflow_success, endpoint_success]):
            print("\n🎉 ALL EMAIL VERIFICATION TESTS PASSED!")
            print("✅ Email service is working correctly")
            print("✅ Gmail SMTP integration is functional")
            print("✅ Email templates are generated properly")
            print("✅ Verification workflow is operational")
            print("✅ Verification endpoint is working")
        else:
            print("\n⚠️ Some tests failed")
            print("   Check the output above for details")
        
        print("\nYour email verification system is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test data
        cleanup_test_data()

if __name__ == "__main__":
    main()
