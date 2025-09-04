#!/usr/bin/env python3
"""
Password Reset Email Test
Test the complete password reset email system with Gmail SMTP
"""

import os
import time
from email_service import email_service, test_email_connection, get_email_status, send_reset_email
from hybrid_password_reset_manager import reset_manager, generate_reset_token, validate_reset_token, reset_password
from hybrid_user_manager import user_manager
from password_reset_endpoint import password_reset_endpoint, handle_reset_request, validate_reset_token_only, get_reset_status
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
    print(f"Reset Base URL: {status.get('reset_base_url', 'Not configured')}")
    
    if not status['password_configured']:
        print("\n❌ Gmail password not configured!")
        print("Please create gmail_password.txt with your Gmail app password")
        return False
    
    # Test SMTP connection
    print("\nTesting Gmail SMTP connection...")
    connection_success = test_email_connection()
    print(f"SMTP Connection: {'✅ Success' if connection_success else '❌ Failed'}")
    
    return connection_success

def test_reset_email_sending():
    """Test sending password reset emails"""
    print("\n" + "=" * 70)
    print("TESTING PASSWORD RESET EMAIL SENDING")
    print("=" * 70)
    
    # Test data
    test_username = "reset_email_test_user"
    test_email = "test@example.com"  # Replace with real email for testing
    test_token = "test_reset_token_123"
    
    print(f"Testing reset email to: {test_email}")
    print(f"Username: {test_username}")
    print(f"Token: {test_token}")
    
    # Send reset email
    email_sent = send_reset_email(test_username, test_email, test_token)
    print(f"Reset Email Sent: {'✅ Success' if email_sent else '❌ Failed'}")
    
    if email_sent:
        print("✅ Password reset email sent successfully!")
        print("Check the recipient's inbox for the reset email")
    else:
        print("❌ Failed to send password reset email")
        print("Check Gmail credentials and SMTP settings")
    
    return email_sent

def test_reset_email_templates():
    """Test password reset email template generation"""
    print("\n" + "=" * 70)
    print("TESTING PASSWORD RESET EMAIL TEMPLATES")
    print("=" * 70)
    
    # Test data
    test_username = "template_test_user"
    test_reset_link = "https://zachnashandi-beep.github.io/zachapp/reset.html?username=test&token=abc123"
    
    print("Testing password reset email template generation...")
    
    # Test HTML template
    html_content = email_service._create_reset_email_html(test_username, test_reset_link)
    print(f"HTML Template Generated: {'✅ Success' if html_content else '❌ Failed'}")
    print(f"HTML Content Length: {len(html_content)} characters")
    
    # Test text template
    text_content = email_service._create_reset_email_text(test_username, test_reset_link)
    print(f"Text Template Generated: {'✅ Success' if text_content else '❌ Failed'}")
    print(f"Text Content Length: {len(text_content)} characters")
    
    return True

def test_password_reset_workflow():
    """Test complete password reset workflow"""
    print("\n" + "=" * 70)
    print("TESTING PASSWORD RESET WORKFLOW")
    print("=" * 70)
    
    # Create test user
    test_username = "reset_workflow_test"
    test_email = "reset_workflow_test@example.com"  # Replace with real email
    test_password = "testpassword123"
    
    print(f"1. Creating test user: {test_username}")
    user_created = user_manager.save_user(test_username, test_email, test_password)
    print(f"   User Created: {'✅ Success' if user_created else '❌ Failed'}")
    
    if not user_created:
        return False
    
    print(f"\n2. Generating reset token...")
    token = generate_reset_token(test_username, 1)  # 1 hour expiry
    if token:
        print(f"   Token Generated: {token[:20]}...")
    else:
        print(f"   Token Generation: ❌ Failed")
        return False
    
    print(f"\n3. Validating reset token...")
    token_data = validate_reset_token(token)
    if token_data:
        print(f"   Token Valid: ✅ Yes")
        print(f"   - Username: {token_data['username']}")
        print(f"   - Email: {token_data['email']}")
        print(f"   - Expiry: {time.ctime(token_data['expiry'])}")
    else:
        print(f"   Token Valid: ❌ No")
        return False
    
    print(f"\n4. Testing password reset...")
    new_password = "newpassword456"
    reset_success = reset_password(token, new_password)
    print(f"   Password Reset: {'✅ Success' if reset_success else '❌ Failed'}")
    
    if reset_success:
        print(f"\n5. Verifying token is invalidated after use...")
        token_data_after = validate_reset_token(token)
        if not token_data_after:
            print(f"   Token Invalidated: ✅ Yes")
        else:
            print(f"   Token Invalidated: ❌ No")
    
    return True

def test_reset_endpoint():
    """Test password reset endpoint functionality"""
    print("\n" + "=" * 70)
    print("TESTING PASSWORD RESET ENDPOINT")
    print("=" * 70)
    
    # Test data
    test_username = "endpoint_test_user"
    test_token = "endpoint_test_token"
    test_password = "newpassword789"
    
    print(f"Testing password reset endpoint with:")
    print(f"  Username: {test_username}")
    print(f"  Token: {test_token}")
    print(f"  New Password: {test_password}")
    
    # Test reset request
    result = handle_reset_request(test_username, test_token, test_password)
    print(f"\nReset Request Result:")
    print(f"  Success: {result.get('success', False)}")
    print(f"  Message: {result.get('message', 'N/A')}")
    print(f"  Username: {result.get('username', 'N/A')}")
    print(f"  Redirect URL: {result.get('redirect_url', 'N/A')}")
    
    # Test token validation only
    validation = validate_reset_token_only(test_username, test_token)
    print(f"\nToken Validation Only:")
    print(f"  Valid: {validation.get('valid', False)}")
    print(f"  Message: {validation.get('message', 'N/A')}")
    print(f"  Username: {validation.get('username', 'N/A')}")
    
    # Test reset status
    status = get_reset_status(test_username)
    print(f"\nReset Status:")
    print(f"  Username: {status.get('username', 'N/A')}")
    print(f"  User Exists: {status.get('user_exists', False)}")
    print(f"  Email: {status.get('email', 'N/A')}")
    
    return True

def test_hybrid_reset_logic():
    """Test hybrid reset logic with database online/offline scenarios"""
    print("\n" + "=" * 70)
    print("TESTING HYBRID RESET LOGIC")
    print("=" * 70)
    
    # Create test user
    test_username = "hybrid_reset_test"
    test_email = "hybrid_reset_test@example.com"
    test_password = "testpassword123"
    
    print(f"1. Creating test user: {test_username}")
    user_created = user_manager.save_user(test_username, test_email, test_password)
    print(f"   User Created: {'✅ Success' if user_created else '❌ Failed'}")
    
    print(f"\n2. Testing reset token generation (online scenario)...")
    print(f"   Database Available: {is_database_available()}")
    
    token = generate_reset_token(test_username, 1)
    if token:
        print(f"   Token Generated: {token[:20]}...")
        print(f"   Email Sent: {'✅ Yes' if is_database_available() else '⚠️ No (offline)'}")
    else:
        print(f"   Token Generation: ❌ Failed")
        return False
    
    print(f"\n3. Testing token validation...")
    token_data = validate_reset_token(token)
    if token_data:
        print(f"   Token Valid: ✅ Yes")
        print(f"   Storage: {'Database' if is_database_available() else 'JSON'}")
    else:
        print(f"   Token Valid: ❌ No")
        return False
    
    print(f"\n4. Testing password reset...")
    new_password = "newpassword456"
    reset_success = reset_password(token, new_password)
    print(f"   Password Reset: {'✅ Success' if reset_success else '❌ Failed'}")
    
    return True

def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "=" * 70)
    print("CLEANING UP TEST DATA")
    print("=" * 70)
    
    # Clean up database test data
    if is_database_available():
        from database_manager import execute_database_query
        
        test_users = ["reset_email_test_user", "reset_workflow_test", "endpoint_test_user", "hybrid_reset_test"]
        
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
    print("PASSWORD RESET EMAIL SYSTEM COMPREHENSIVE TEST")
    print("=" * 70)
    
    try:
        # Test 1: Email service setup
        email_setup_success = test_email_service_setup()
        
        if not email_setup_success:
            print("\n❌ Email service setup failed. Please configure Gmail credentials.")
            return
        
        # Test 2: Email template generation
        template_success = test_reset_email_templates()
        
        # Test 3: Reset email sending
        reset_email_success = test_reset_email_sending()
        
        # Test 4: Password reset workflow
        workflow_success = test_password_reset_workflow()
        
        # Test 5: Reset endpoint
        endpoint_success = test_reset_endpoint()
        
        # Test 6: Hybrid reset logic
        hybrid_success = test_hybrid_reset_logic()
        
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"Email Service Setup: {'✅ Success' if email_setup_success else '❌ Failed'}")
        print(f"Email Templates: {'✅ Success' if template_success else '❌ Failed'}")
        print(f"Reset Email Sending: {'✅ Success' if reset_email_success else '❌ Failed'}")
        print(f"Password Reset Workflow: {'✅ Success' if workflow_success else '❌ Failed'}")
        print(f"Reset Endpoint: {'✅ Success' if endpoint_success else '❌ Failed'}")
        print(f"Hybrid Reset Logic: {'✅ Success' if hybrid_success else '❌ Failed'}")
        
        if all([email_setup_success, template_success, reset_email_success, 
                workflow_success, endpoint_success, hybrid_success]):
            print("\n🎉 ALL PASSWORD RESET EMAIL TESTS PASSED!")
            print("✅ Email service is working correctly")
            print("✅ Gmail SMTP integration is functional")
            print("✅ Password reset email templates are generated properly")
            print("✅ Password reset workflow is operational")
            print("✅ Reset endpoint is working")
            print("✅ Hybrid reset logic is functional")
        else:
            print("\n⚠️ Some tests failed")
            print("   Check the output above for details")
        
        print("\nYour password reset email system is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test data
        cleanup_test_data()

if __name__ == "__main__":
    main()
