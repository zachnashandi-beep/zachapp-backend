#!/usr/bin/env python3
"""
Password Reset Endpoint
Handles password reset requests from GitHub Pages
"""

import logging
from typing import Dict, Any, Optional
from hybrid_password_reset_manager import reset_manager
from hybrid_user_manager import user_manager

class PasswordResetEndpoint:
    """Handles password reset requests"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Setup logging for password reset operations"""
        logger = logging.getLogger('PasswordResetEndpoint')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def handle_reset_request(self, username: str, token: str, new_password: str) -> Dict[str, Any]:
        """Handle password reset request"""
        try:
            self.logger.info(f"Processing password reset request for user: {username}")
            
            # Validate the reset token
            token_data = reset_manager.validate_reset_token(token)
            
            if not token_data:
                self.logger.warning(f"❌ Invalid or expired reset token for user: {username}")
                return {
                    "success": False,
                    "message": "Invalid or expired reset token. Please request a new password reset.",
                    "username": username,
                    "redirect_url": "https://zachnashandi-beep.github.io/zachapp/login?error=invalid_token"
                }
            
            # Verify the token belongs to the correct user
            if token_data["username"] != username:
                self.logger.warning(f"❌ Token username mismatch for user: {username}")
                return {
                    "success": False,
                    "message": "Invalid reset token for this user.",
                    "username": username,
                    "redirect_url": "https://zachnashandi-beep.github.io/zachapp/login?error=token_mismatch"
                }
            
            # Reset the password
            reset_success = reset_manager.reset_password(token, new_password)
            
            if reset_success:
                self.logger.info(f"✅ Password reset successful for user: {username}")
                return {
                    "success": True,
                    "message": "Password reset successful! You can now log in with your new password.",
                    "username": username,
                    "redirect_url": "https://zachnashandi-beep.github.io/zachapp/login?reset=success"
                }
            else:
                self.logger.error(f"❌ Password reset failed for user: {username}")
                return {
                    "success": False,
                    "message": "Password reset failed. Please try again or request a new reset link.",
                    "username": username,
                    "redirect_url": "https://zachnashandi-beep.github.io/zachapp/login?error=reset_failed"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing password reset request for {username}: {e}")
            return {
                "success": False,
                "message": "An error occurred during password reset. Please try again.",
                "username": username,
                "redirect_url": "https://zachnashandi-beep.github.io/zachapp/login?error=reset_error"
            }
    
    def validate_reset_token_only(self, username: str, token: str) -> Dict[str, Any]:
        """Validate reset token without resetting password (for form display)"""
        try:
            self.logger.info(f"Validating reset token for user: {username}")
            
            # Validate the reset token
            token_data = reset_manager.validate_reset_token(token)
            
            if not token_data:
                return {
                    "valid": False,
                    "message": "Invalid or expired reset token.",
                    "username": username
                }
            
            # Verify the token belongs to the correct user
            if token_data["username"] != username:
                return {
                    "valid": False,
                    "message": "Invalid reset token for this user.",
                    "username": username
                }
            
            return {
                "valid": True,
                "message": "Reset token is valid. You can now set a new password.",
                "username": username,
                "email": token_data.get("email", "")
            }
                
        except Exception as e:
            self.logger.error(f"Error validating reset token for {username}: {e}")
            return {
                "valid": False,
                "message": "An error occurred while validating the reset token.",
                "username": username
            }
    
    def get_reset_status(self, username: str) -> Dict[str, Any]:
        """Get password reset status for a user"""
        try:
            # Check if user exists
            user = user_manager.get_user(username)
            if not user:
                return {
                    "username": username,
                    "user_exists": False,
                    "message": "User not found"
                }
            
            return {
                "username": username,
                "user_exists": True,
                "email": user.get("email", ""),
                "message": "User found"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting reset status for {username}: {e}")
            return {
                "username": username,
                "user_exists": False,
                "error": str(e)
            }

# Global password reset endpoint instance
password_reset_endpoint = PasswordResetEndpoint()

# Convenience functions
def handle_reset_request(username: str, token: str, new_password: str) -> Dict[str, Any]:
    """Handle password reset request"""
    return password_reset_endpoint.handle_reset_request(username, token, new_password)

def validate_reset_token_only(username: str, token: str) -> Dict[str, Any]:
    """Validate reset token without resetting password"""
    return password_reset_endpoint.validate_reset_token_only(username, token)

def get_reset_status(username: str) -> Dict[str, Any]:
    """Get password reset status for a user"""
    return password_reset_endpoint.get_reset_status(username)

if __name__ == "__main__":
    # Test the password reset endpoint
    print("Testing Password Reset Endpoint...")
    
    # Test with sample data
    test_username = "test_user"
    test_token = "test_token"
    test_password = "newpassword123"
    
    print(f"Testing reset request for {test_username}...")
    result = handle_reset_request(test_username, test_token, test_password)
    print(f"Result: {result}")
    
    print(f"\nTesting token validation for {test_username}...")
    validation = validate_reset_token_only(test_username, test_token)
    print(f"Validation: {validation}")
    
    print(f"\nTesting reset status for {test_username}...")
    status = get_reset_status(test_username)
    print(f"Status: {status}")
