#!/usr/bin/env python3
"""
Hybrid Verification Manager
Manages email verification with database primary and JSON fallback
"""

import json
import os
import time
import secrets
from typing import Optional, Dict, Any
from database_manager import (
    is_database_available, save_verification_token_to_db, get_verification_token_from_db,
    mark_verification_token_verified, is_user_verified_in_db
)
from sync_manager import check_and_sync
from email_service import send_verification_email

class HybridVerificationManager:
    """Manages email verification with database primary and JSON fallback"""
    
    def __init__(self, verification_file: str = "verification.json"):
        self.verification_file = verification_file
        self._ensure_verification_file()
    
    def _ensure_verification_file(self):
        """Ensure verification.json exists"""
        if not os.path.exists(self.verification_file):
            with open(self.verification_file, 'w') as f:
                json.dump({}, f)
    
    def _load_verification_from_json(self) -> Dict[str, Any]:
        """Load verification data from JSON file"""
        try:
            with open(self.verification_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_verification_to_json(self, verification: Dict[str, Any]):
        """Save verification data to JSON file"""
        with open(self.verification_file, 'w') as f:
            json.dump(verification, f, indent=2)
    
    def generate_verification_token(self, username: str, email: str, expiry_hours: int = 24) -> str:
        """Generate a verification token"""
        token = secrets.token_hex(32)
        expiry = int(time.time()) + (expiry_hours * 3600)
        
        # Check and sync before attempting database operations
        check_and_sync()
        
        # Try database first
        if is_database_available():
            success = save_verification_token_to_db(username, email, token, expiry)
            if success:
                print(f"✅ Verification token generated for '{username}' in database")
                return token
            else:
                print(f"⚠️ Database token generation failed for '{username}', falling back to JSON")
        
        # Fallback to JSON
        verification = self._load_verification_from_json()
        verification[username] = {
            "token": token,
            "expiry": expiry,
            "verified": False,
            "email": email
        }
        self._save_verification_to_json(verification)
        print(f"✅ Verification token generated for '{username}' in JSON file")
        
        # Try to sync immediately if database becomes available
        check_and_sync()
        
        # Send verification email
        email_sent = send_verification_email(username, email, token)
        if email_sent:
            print(f"✅ Verification email sent to {email}")
        else:
            print(f"⚠️ Failed to send verification email to {email}")
        
        return token
    
    def verify_email(self, username: str, token: str) -> bool:
        """Verify email with token"""
        current_time = int(time.time())
        
        # Try database first
        if is_database_available():
            token_data = get_verification_token_from_db(token)
            if token_data and token_data["username"] == username:
                # Mark as verified
                success = mark_verification_token_verified(token)
                if success:
                    print(f"✅ Email verified for '{username}' in database")
                    return True
            else:
                print(f"❌ Invalid or expired verification token for '{username}' in database")
                return False
        
        # Fallback to JSON
        verification = self._load_verification_from_json()
        if username in verification:
            token_data = verification[username]
            if (token_data["token"] == token and 
                token_data["expiry"] > current_time and
                not token_data["verified"]):
                
                # Mark as verified
                verification[username]["verified"] = True
                self._save_verification_to_json(verification)
                print(f"✅ Email verified for '{username}' in JSON file")
                return True
            else:
                print(f"❌ Invalid, expired, or already verified token for '{username}' in JSON file")
                return False
        
        print(f"❌ No verification data found for '{username}'")
        return False
    
    def is_verified(self, username: str) -> bool:
        """Check if user is verified"""
        # Try database first
        if is_database_available():
            verified = is_user_verified_in_db(username)
            if verified:
                print(f"✅ User '{username}' is verified in database")
                return True
            else:
                print(f"❌ User '{username}' is not verified in database")
                return False
        
        # Fallback to JSON
        verification = self._load_verification_from_json()
        if username in verification:
            token_data = verification[username]
            current_time = int(time.time())
            
            # Check if token is still valid and verified
            if token_data["expiry"] > current_time and token_data["verified"]:
                print(f"✅ User '{username}' is verified in JSON file")
                return True
            else:
                print(f"❌ User '{username}' is not verified or token expired in JSON file")
                return False
        
        print(f"❌ No verification data found for '{username}'")
        return False
    
    def resend_verification(self, username: str, email: str, expiry_hours: int = 24) -> str:
        """Resend verification token"""
        return self.generate_verification_token(username, email, expiry_hours)
    
    def get_verification_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get verification information"""
        # Try database first
        if is_database_available():
            from database_manager import execute_database_query
            query = """
                SELECT token, email, UNIX_TIMESTAMP(expiry) as expiry_timestamp, verified, created_at 
                FROM verification_tokens 
                WHERE username = %s
            """
            result = execute_database_query(query, (username,), fetch=True)
            if result:
                token_data = result[0]
                return {
                    "token": token_data["token"],
                    "email": token_data["email"],
                    "expiry": token_data["expiry_timestamp"],
                    "verified": bool(token_data["verified"]),
                    "created_at": str(token_data["created_at"])
                }
        
        # Fallback to JSON
        verification = self._load_verification_from_json()
        if username in verification:
            token_data = verification[username]
            return {
                "token": token_data["token"],
                "email": token_data["email"],
                "expiry": token_data["expiry"],
                "verified": token_data["verified"],
                "created_at": "Unknown"
            }
        
        return None
    
    def cleanup_expired_tokens(self):
        """Clean up expired verification tokens"""
        # Try database first
        if is_database_available():
            from database_manager import execute_database_query
            query = "DELETE FROM verification_tokens WHERE expiry < NOW()"
            execute_database_query(query)
            print("✅ Expired verification tokens cleaned up in database")
            return
        
        # Fallback to JSON
        verification = self._load_verification_from_json()
        current_time = int(time.time())
        expired_users = []
        
        for username, token_data in verification.items():
            if token_data["expiry"] <= current_time:
                expired_users.append(username)
        
        for username in expired_users:
            del verification[username]
        
        if expired_users:
            self._save_verification_to_json(verification)
            print(f"✅ Cleaned up {len(expired_users)} expired verification tokens in JSON file")
        else:
            print("ℹ️ No expired verification tokens found in JSON file")
    
    def get_verification_data(self, username: str) -> Optional[Dict[str, Any]]:
        """Get verification data for a user"""
        # Try database first
        if is_database_available():
            try:
                verification_data = get_verification_token_from_db(username)
                if verification_data:
                    return verification_data
            except Exception as e:
                print(f"⚠️ Database verification data retrieval failed for '{username}': {e}")
        
        # Fallback to JSON
        try:
            verification = self._load_verification_from_json()
            if username in verification:
                return verification[username]
        except Exception as e:
            print(f"⚠️ JSON verification data retrieval failed for '{username}': {e}")
        
        return None

# Global instance
verification_manager = HybridVerificationManager()

# Convenience functions
def generate_verification_token(username: str, email: str, expiry_hours: int = 24) -> str:
    """Generate a verification token"""
    return verification_manager.generate_verification_token(username, email, expiry_hours)

def verify_email(username: str, token: str) -> bool:
    """Verify email with token"""
    return verification_manager.verify_email(username, token)

def is_verified(username: str) -> bool:
    """Check if user is verified"""
    return verification_manager.is_verified(username)

def resend_verification(username: str, email: str, expiry_hours: int = 24) -> str:
    """Resend verification token"""
    return verification_manager.resend_verification(username, email, expiry_hours)

def get_verification_info(username: str) -> Optional[Dict[str, Any]]:
    """Get verification information"""
    return verification_manager.get_verification_info(username)

def get_verification_data(username: str) -> Optional[Dict[str, Any]]:
    """Get verification data for a user"""
    return verification_manager.get_verification_data(username)

def cleanup_expired_verification_tokens():
    """Clean up expired verification tokens"""
    verification_manager.cleanup_expired_tokens()

# Email simulation function
def send_verification_email_simulation(username: str, email: str, token: str):
    """Simulate sending verification email"""
    verification_link = f"https://yourapp.com/verify?user={username}&token={token}"
    
    print("=" * 70)
    print("EMAIL VERIFICATION SIMULATION")
    print("=" * 70)
    print(f"To: {email}")
    print(f"Subject: Verify Your Email Address")
    print("-" * 70)
    print(f"Hello {username},")
    print()
    print("Thank you for signing up! Please verify your email address by clicking the link below:")
    print()
    print(f"Verification Link: {verification_link}")
    print()
    print("This link will expire in 24 hours.")
    print("If you didn't create an account, please ignore this email.")
    print()
    print("Best regards,")
    print("Your App Team")
    print("=" * 70)

if __name__ == "__main__":
    # Test the hybrid verification manager
    print("Testing Hybrid Verification Manager...")
    
    test_username = "testuser_verify"
    test_email = "test@example.com"
    
    print(f"\n1. Generating verification token for '{test_username}'...")
    token = generate_verification_token(test_username, test_email, 24)
    print(f"Verification token: {token[:20]}...")
    
    print(f"\n2. Checking verification status...")
    verified = is_verified(test_username)
    print(f"Verification status: {'✅ Verified' if verified else '❌ Not verified'}")
    
    print(f"\n3. Getting verification info...")
    info = get_verification_info(test_username)
    if info:
        print(f"✅ Verification info: expires at {time.ctime(info['expiry'])}")
        print(f"   Email: {info['email']}")
        print(f"   Verified: {info['verified']}")
    else:
        print("❌ No verification info found")
    
    print(f"\n4. Verifying email...")
    success = verify_email(test_username, token)
    print(f"Verification result: {'✅ Success' if success else '❌ Failed'}")
    
    print(f"\n5. Checking verification status again...")
    verified = is_verified(test_username)
    print(f"Verification status: {'✅ Verified' if verified else '❌ Not verified'}")
    
    print("\n" + "="*50)
    print("Hybrid Verification Manager test complete!")
    print("="*50)
