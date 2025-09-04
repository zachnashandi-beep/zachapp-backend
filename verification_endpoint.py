#!/usr/bin/env python3
"""
Verification Endpoint
Handles email verification requests from GitHub Pages
"""

import json
import logging
from typing import Dict, Any, Optional
from hybrid_verification_manager import verification_manager
from email_service import send_confirmation_email

class VerificationEndpoint:
    """Handles email verification requests"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging for verification operations"""
        logger = logging.getLogger('VerificationEndpoint')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def handle_verification_request(self, username: str, token: str) -> Dict[str, Any]:
        """Handle email verification request"""
        try:
            self.logger.info(f"Processing verification request for user: {username}")
            
            # Verify the email
            verification_success = verification_manager.verify_email(username, token)
            
            if verification_success:
                self.logger.info(f"✅ Email verification successful for user: {username}")
                
                # Get user email for confirmation email
                user_email = self._get_user_email(username)
                
                # Send confirmation email
                if user_email:
                    confirmation_sent = send_confirmation_email(username, user_email)
                    if confirmation_sent:
                        self.logger.info(f"✅ Confirmation email sent to {user_email}")
                    else:
                        self.logger.warning(f"⚠️ Failed to send confirmation email to {user_email}")
                
                return {
                    "success": True,
                    "message": "Email verification successful! Your account has been verified.",
                    "username": username,
                    "redirect_url": "https://zachnashandi-beep.github.io/zachapp/login?verified=true"
                }
            else:
                self.logger.warning(f"❌ Email verification failed for user: {username}")
                return {
                    "success": False,
                    "message": "Email verification failed. The token may be invalid or expired.",
                    "username": username,
                    "redirect_url": "https://zachnashandi-beep.github.io/zachapp/login?error=verification_failed"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing verification request for {username}: {e}")
            return {
                "success": False,
                "message": "An error occurred during verification. Please try again.",
                "username": username,
                "redirect_url": "https://zachnashandi-beep.github.io/zachapp/login?error=verification_error"
            }
    
    def _get_user_email(self, username: str) -> Optional[str]:
        """Get user email from verification data"""
        try:
            # Try to get from verification manager
            verification_data = verification_manager.get_verification_data(username)
            if verification_data and "email" in verification_data:
                return verification_data["email"]
            
            # Fallback: try to get from user manager
            from hybrid_user_manager import user_manager
            user = user_manager.get_user(username)
            if user and "email" in user:
                return user["email"]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user email for {username}: {e}")
            return None
    
    def get_verification_status(self, username: str) -> Dict[str, Any]:
        """Get verification status for a user"""
        try:
            is_verified = verification_manager.is_verified(username)
            verification_data = verification_manager.get_verification_data(username)
            
            return {
                "username": username,
                "verified": is_verified,
                "verification_data": verification_data
            }
            
        except Exception as e:
            self.logger.error(f"Error getting verification status for {username}: {e}")
            return {
                "username": username,
                "verified": False,
                "error": str(e)
            }

# Global verification endpoint instance
verification_endpoint = VerificationEndpoint()

# Convenience functions
def handle_verification_request(username: str, token: str) -> Dict[str, Any]:
    """Handle email verification request"""
    return verification_endpoint.handle_verification_request(username, token)

def get_verification_status(username: str) -> Dict[str, Any]:
    """Get verification status for a user"""
    return verification_endpoint.get_verification_status(username)

if __name__ == "__main__":
    # Test the verification endpoint
    print("Testing Verification Endpoint...")
    
    # Test with sample data
    test_username = "test_user"
    test_token = "test_token"
    
    print(f"Testing verification request for {test_username}...")
    result = handle_verification_request(test_username, test_token)
    print(f"Result: {result}")
    
    print(f"\nTesting verification status for {test_username}...")
    status = get_verification_status(test_username)
    print(f"Status: {status}")
