#!/usr/bin/env python3
"""
Hybrid Password Reset Manager
Manages password reset tokens with database primary and JSON fallback
"""

import json
import os
import time
import secrets
import hashlib
from typing import Optional, Dict, Any
from database_manager import (
    is_database_available, save_reset_token_to_db, get_reset_token_from_db,
    delete_reset_token_from_db, cleanup_expired_tokens_from_db
)
from sync_manager import check_and_sync
from email_service import send_reset_email

class HybridPasswordResetManager:
    """Manages password reset tokens with database primary and JSON fallback"""
    
    def __init__(self, reset_tokens_file: str = "reset_tokens.json"):
        self.reset_tokens_file = reset_tokens_file
        self._ensure_reset_tokens_file()
    
    def _ensure_reset_tokens_file(self):
        """Ensure reset_tokens.json exists"""
        if not os.path.exists(self.reset_tokens_file):
            with open(self.reset_tokens_file, 'w') as f:
                json.dump({}, f)
    
    def _load_reset_tokens_from_json(self) -> Dict[str, Any]:
        """Load reset tokens from JSON file"""
        try:
            with open(self.reset_tokens_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_reset_tokens_to_json(self, tokens: Dict[str, Any]):
        """Save reset tokens to JSON file"""
        with open(self.reset_tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2)
    
    def generate_reset_token(self, username_or_email: str, expiry_hours: int = 1) -> Optional[str]:
        """Generate a reset token for username or email"""
        # First, find the user
        from hybrid_user_manager import get_user, get_user_by_email
        
        user = get_user(username_or_email) or get_user_by_email(username_or_email)
        if not user:
            print(f"❌ No user found with username or email: {username_or_email}")
            return None
        
        username = user["username"]
        email = user["email"]
        token = secrets.token_hex(32)
        expiry = int(time.time()) + (expiry_hours * 3600)
        
        # Check and sync before attempting database operations
        check_and_sync()
        
        # Try database first
        if is_database_available():
            success = save_reset_token_to_db(username, email, token, expiry)
            if success:
                print(f"✅ Reset token generated for '{username}' in database")
                return token
            else:
                print(f"⚠️ Database token generation failed for '{username}', falling back to JSON")
        
        # Fallback to JSON
        tokens = self._load_reset_tokens_from_json()
        tokens[token] = {
            "username": username,
            "email": email,
            "expiry": expiry,
            "created": int(time.time())
        }
        self._save_reset_tokens_to_json(tokens)
        print(f"✅ Reset token generated for '{username}' in JSON file")
        
        # Try to sync immediately if database becomes available
        check_and_sync()
        
        # Send reset email only if database is available (online)
        if is_database_available():
            email_sent = send_reset_email(username, email, token)
            if email_sent:
                print(f"✅ Password reset email sent to {email}")
            else:
                print(f"⚠️ Failed to send password reset email to {email}")
        else:
            print(f"⚠️ Database offline - reset token stored in JSON, email not sent")
            print(f"   Email will be sent when database comes online and sync occurs")
        
        return token
    
    def validate_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a reset token"""
        current_time = int(time.time())
        
        # Try database first
        if is_database_available():
            token_data = get_reset_token_from_db(token)
            if token_data:
                print(f"✅ Reset token validated for '{token_data['username']}' in database")
                return {
                    "username": token_data["username"],
                    "email": token_data["email"],
                    "expiry": token_data["expiry_timestamp"]
                }
            else:
                print(f"❌ Invalid or expired reset token in database")
                return None
        
        # Fallback to JSON
        tokens = self._load_reset_tokens_from_json()
        if token in tokens:
            token_data = tokens[token]
            if token_data["expiry"] > current_time:
                print(f"✅ Reset token validated for '{token_data['username']}' in JSON file")
                return {
                    "username": token_data["username"],
                    "email": token_data["email"],
                    "expiry": token_data["expiry"]
                }
            else:
                # Remove expired token
                del tokens[token]
                self._save_reset_tokens_to_json(tokens)
                print(f"❌ Expired reset token removed from JSON file")
                return None
        
        print(f"❌ Invalid reset token")
        return None
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        # Validate token first
        token_data = self.validate_reset_token(token)
        if not token_data:
            return False
        
        username = token_data["username"]
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        # Update password using hybrid user manager
        from hybrid_user_manager import update_user_password
        success = update_user_password(username, new_password)
        
        if success:
            # Delete the used token
            self._delete_reset_token(token)
            print(f"✅ Password reset successful for '{username}'")
            return True
        else:
            print(f"❌ Password reset failed for '{username}'")
            return False
    
    def _delete_reset_token(self, token: str):
        """Delete a reset token"""
        # Try database first
        if is_database_available():
            success = delete_reset_token_from_db(token)
            if success:
                print(f"✅ Reset token deleted from database")
                return
            else:
                print(f"⚠️ Database token deletion failed, falling back to JSON")
        
        # Fallback to JSON
        tokens = self._load_reset_tokens_from_json()
        if token in tokens:
            del tokens[token]
            self._save_reset_tokens_to_json(tokens)
            print(f"✅ Reset token deleted from JSON file")
    
    def cleanup_expired_tokens(self):
        """Clean up expired reset tokens"""
        # Try database first
        if is_database_available():
            cleanup_expired_tokens_from_db()
            print("✅ Expired reset tokens cleaned up in database")
            return
        
        # Fallback to JSON
        tokens = self._load_reset_tokens_from_json()
        current_time = int(time.time())
        expired_tokens = []
        
        for token, data in tokens.items():
            if current_time > data["expiry"]:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del tokens[token]
        
        if expired_tokens:
            self._save_reset_tokens_to_json(tokens)
            print(f"✅ Cleaned up {len(expired_tokens)} expired reset tokens in JSON file")
        else:
            print("ℹ️ No expired reset tokens found in JSON file")
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get information about a token without validating expiry"""
        # Try database first
        if is_database_available():
            from database_manager import execute_database_query
            query = """
                SELECT username, email, UNIX_TIMESTAMP(expiry) as expiry_timestamp, created_at 
                FROM reset_tokens 
                WHERE token = %s
            """
            result = execute_database_query(query, (token,), fetch=True)
            if result:
                token_data = result[0]
                return {
                    "username": token_data["username"],
                    "email": token_data["email"],
                    "expiry": token_data["expiry_timestamp"],
                    "created_at": str(token_data["created_at"])
                }
        
        # Fallback to JSON
        tokens = self._load_reset_tokens_from_json()
        if token in tokens:
            token_data = tokens[token]
            return {
                "username": token_data["username"],
                "email": token_data["email"],
                "expiry": token_data["expiry"],
                "created_at": time.ctime(token_data["created"])
            }
        
        return None

# Global instance
reset_manager = HybridPasswordResetManager()

# Convenience functions
def generate_reset_token(username_or_email: str, expiry_hours: int = 1) -> Optional[str]:
    """Generate a reset token for username or email"""
    return reset_manager.generate_reset_token(username_or_email, expiry_hours)

def validate_reset_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate a reset token"""
    return reset_manager.validate_reset_token(token)

def reset_password(token: str, new_password: str) -> bool:
    """Reset password using token"""
    return reset_manager.reset_password(token, new_password)

def cleanup_expired_reset_tokens():
    """Clean up expired reset tokens"""
    reset_manager.cleanup_expired_tokens()

def get_reset_token_info(token: str) -> Optional[Dict[str, Any]]:
    """Get information about a reset token"""
    return reset_manager.get_token_info(token)

# Email simulation function
def send_reset_email_simulation(username: str, email: str, token: str):
    """Simulate sending reset email"""
    reset_link = f"https://yourapp.com/reset_password?user={username}&token={token}"
    
    print("=" * 70)
    print("PASSWORD RESET EMAIL SIMULATION")
    print("=" * 70)
    print(f"To: {email}")
    print(f"Subject: Password Reset Request")
    print("-" * 70)
    print(f"Hello {username},")
    print()
    print("You requested a password reset for your account.")
    print("Click the link below to reset your password:")
    print()
    print(f"Reset Link: {reset_link}")
    print()
    print("This link will expire in 1 hour.")
    print("If you didn't request this reset, please ignore this email.")
    print()
    print("Best regards,")
    print("Your App Team")
    print("=" * 70)

if __name__ == "__main__":
    # Test the hybrid password reset manager
    print("Testing Hybrid Password Reset Manager...")
    
    test_username = "testuser_reset"
    test_email = "test@example.com"
    test_password = "newpassword123"
    
    print(f"\n1. Generating reset token for '{test_username}'...")
    token = generate_reset_token(test_username, 1)
    if token:
        print(f"Reset token: {token[:20]}...")
    else:
        print("❌ Token generation failed")
        exit(1)
    
    print(f"\n2. Validating reset token...")
    token_data = validate_reset_token(token)
    if token_data:
        print(f"✅ Token valid for: {token_data['username']}")
        print(f"   Email: {token_data['email']}")
        print(f"   Expires: {time.ctime(token_data['expiry'])}")
    else:
        print("❌ Token validation failed")
        exit(1)
    
    print(f"\n3. Resetting password...")
    success = reset_password(token, test_password)
    print(f"Password reset result: {'✅ Success' if success else '❌ Failed'}")
    
    print(f"\n4. Verifying token is deleted...")
    token_data_after = validate_reset_token(token)
    if not token_data_after:
        print("✅ Token properly deleted after use")
    else:
        print("❌ Token still exists after reset")
    
    print("\n" + "="*50)
    print("Hybrid Password Reset Manager test complete!")
    print("="*50)
