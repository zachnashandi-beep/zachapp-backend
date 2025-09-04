#!/usr/bin/env python3
"""
Password Reset Manager
Handles secure password reset tokens and validation
"""

import json
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class PasswordResetManager:
    """Manages password reset tokens and operations"""
    
    def __init__(self, reset_tokens_file: str = "reset_tokens.json"):
        self.reset_tokens_file = reset_tokens_file
        self._ensure_reset_tokens_file()
    
    def _ensure_reset_tokens_file(self):
        """Ensure reset_tokens.json exists"""
        if not os.path.exists(self.reset_tokens_file):
            with open(self.reset_tokens_file, 'w') as f:
                json.dump({}, f)
    
    def _load_reset_tokens(self) -> Dict[str, Any]:
        """Load reset tokens from file"""
        try:
            with open(self.reset_tokens_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_reset_tokens(self, tokens: Dict[str, Any]):
        """Save reset tokens to file"""
        with open(self.reset_tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2)
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from users.json"""
        try:
            with open("users.json", 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def generate_reset_token(self, username_or_email: str, expiry_hours: int = 1) -> Optional[str]:
        """
        Generate a reset token for username or email
        
        Args:
            username_or_email: Username or email address
            expiry_hours: Token expiry time in hours (default: 1)
            
        Returns:
            Reset token if user exists, None otherwise
        """
        users = self._load_users()
        
        # Find user by username or email
        user = None
        for user_data in users.values():
            if (user_data.get('username') == username_or_email or 
                user_data.get('email') == username_or_email):
                user = user_data
                break
        
        if not user:
            return None
        
        # Generate secure token
        token = secrets.token_hex(32)
        
        # Calculate expiry time
        expiry_time = int(time.time()) + (expiry_hours * 3600)
        
        # Load existing tokens
        tokens = self._load_reset_tokens()
        
        # Store token with user info
        tokens[token] = {
            "username": user['username'],
            "email": user['email'],
            "expiry": expiry_time,
            "created": int(time.time())
        }
        
        # Save tokens
        self._save_reset_tokens(tokens)
        
        return token
    
    def validate_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a reset token
        
        Args:
            token: Reset token to validate
            
        Returns:
            User info if token is valid, None otherwise
        """
        tokens = self._load_reset_tokens()
        
        if token not in tokens:
            return None
        
        token_data = tokens[token]
        current_time = int(time.time())
        
        # Check if token is expired
        if current_time > token_data['expiry']:
            # Remove expired token
            del tokens[token]
            self._save_reset_tokens(tokens)
            return None
        
        return token_data
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using token
        
        Args:
            token: Reset token
            new_password: New password to set
            
        Returns:
            True if successful, False otherwise
        """
        # Validate token
        token_data = self.validate_reset_token(token)
        if not token_data:
            return False
        
        # Load users
        users = self._load_users()
        username = token_data['username']
        
        # Find user and update password
        for user_id, user_data in users.items():
            if user_data.get('username') == username:
                # Hash new password
                import hashlib
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                
                # Update password
                users[user_id]['password'] = hashed_password
                
                # Save users
                with open("users.json", 'w') as f:
                    json.dump(users, f, indent=2)
                
                # Remove used token
                tokens = self._load_reset_tokens()
                if token in tokens:
                    del tokens[token]
                    self._save_reset_tokens(tokens)
                
                return True
        
        return False
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from storage"""
        tokens = self._load_reset_tokens()
        current_time = int(time.time())
        
        expired_tokens = [
            token for token, data in tokens.items()
            if current_time > data['expiry']
        ]
        
        for token in expired_tokens:
            del tokens[token]
        
        if expired_tokens:
            self._save_reset_tokens(tokens)
            print(f"Cleaned up {len(expired_tokens)} expired tokens")
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get information about a token without validating expiry"""
        tokens = self._load_reset_tokens()
        return tokens.get(token)
    
    def revoke_token(self, token: str) -> bool:
        """Manually revoke a token"""
        tokens = self._load_reset_tokens()
        if token in tokens:
            del tokens[token]
            self._save_reset_tokens(tokens)
            return True
        return False

# Global instance
reset_manager = PasswordResetManager()

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

def cleanup_expired_tokens():
    """Clean up expired tokens"""
    reset_manager.cleanup_expired_tokens()

def send_reset_email_simulation(username: str, email: str, token: str):
    """
    Simulate sending reset email (for demo purposes)
    In production, this would send actual emails via SMTP
    """
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
    # Demo the password reset manager
    print("Password Reset Manager Demo")
    print("=" * 50)
    
    # Test token generation
    token = generate_reset_token("testuser")
    if token:
        print(f"Generated token: {token[:20]}...")
        
        # Test token validation
        user_info = validate_reset_token(token)
        if user_info:
            print(f"Token valid for user: {user_info['username']}")
            print(f"Email: {user_info['email']}")
            print(f"Expires: {datetime.fromtimestamp(user_info['expiry'])}")
        else:
            print("Token validation failed")
    else:
        print("Token generation failed - user not found")
